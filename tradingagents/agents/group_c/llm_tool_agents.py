"""
Group C 智能体 - LLM工具调用版本

使用 LangChain 的 bind_tools 机制，让 LLM 自主决定是否调用工具。

新增功能：
- 工具调用缓存
- 智能体间数据共享
"""

from typing import Dict, Any, List, Optional, TypedDict
import logging
import json
from datetime import datetime, timedelta

logger = logging.getLogger('travel_agents')


# ============================================================
# 景点排程师 (LLM工具调用版本)
# ============================================================

class AttractionSchedulerWithTools:
    """
    景点排程师 - LLM工具调用版本

    使用 LLM + Tools 的方式，让 LLM 自主决定何时调用天气和景点搜索工具
    """

    def __init__(self, llm=None):
        """
        初始化景点排程师

        Args:
            llm: LLM 实例
        """
        self.llm = llm
        self._llm_with_tools = None

        # 绑定工具
        if llm and hasattr(llm, 'bind_tools'):
            from tradingagents.tools.langchain_tools import (
                attraction_search_tool,
                weather_forecast_tool
            )
            tools = [attraction_search_tool, weather_forecast_tool]
            self._llm_with_tools = llm.bind_tools(tools)
            logger.info(f"[景点排程师-LLM] 已绑定 {len(tools)} 个工具")
        else:
            logger.warning("[景点排程师-LLM] LLM不支持bind_tools，回退到直接调用模式")

    def schedule_attractions(
        self,
        destination: str,
        dest_data: Dict[str, Any],
        style_proposal: Dict[str, Any],
        days: int,
        start_date: str
    ) -> Dict[str, Any]:
        """
        安排景点游览时间表

        使用 LLM 工具调用方式获取天气和景点数据

        Args:
            destination: 目的地名称
            dest_data: 目的地数据
            style_proposal: 风格方案
            days: 旅行天数
            start_date: 开始日期

        Returns:
            包含每日景点时间安排列表和LLM描述的字典
        """
        logger.info(f"[景点排程师-LLM] 为{destination}安排{days}天景点时间表")

        # 如果有绑定工具的LLM，使用它
        llm_to_use = self._llm_with_tools if self._llm_with_tools else self.llm

        # 使用 LLM 获取天气和景点建议
        daily_weather = self._get_weather_via_llm(destination, days, llm_to_use)
        weather_available = len(daily_weather) > 0

        # 获取景点列表 - 【数据共享】优先使用 Group B 的搜索结果
        style_type = style_proposal.get("style_type", "immersive")
        highlights = dest_data.get("highlights", [])
        daily_itinerary = style_proposal.get("daily_itinerary", [])

        # 尝试从共享数据获取 Group B 已搜索的景点
        shared_attractions = None
        try:
            from tradingagents.utils.shared_data import load_group_b_attractions, get_api_sources_used
            shared_attractions = load_group_b_attractions()

            if shared_attractions:
                api_sources = get_api_sources_used()
                logger.info(f"[景点排程师-LLM] 复用 Group B 搜索结果: {len(shared_attractions)} 个景点, API: {api_sources}")
            else:
                logger.debug("[景点排程师-LLM] 无 Group B 共享数据")
        except Exception as e:
            logger.debug(f"[景点排程师-LLM] 获取共享数据失败: {e}")

        # 如果没有共享数据，从 daily_itinerary 获取
        if not daily_itinerary:
            if shared_attractions:
                # 使用 Group B 的景点数据
                attraction_names = []
                for attr in shared_attractions[:days * 4]:  # 取前 days*4 个景点
                    if isinstance(attr, dict):
                        name = attr.get("name", "")
                    else:
                        name = attr
                    if name and name not in attraction_names:
                        attraction_names.append(name)

                daily_itinerary = self._generate_daily_itinerary(attraction_names, days, style_type)
                logger.info(f"[景点排程师-LLM] 使用共享景点数据: {len(attraction_names)} 个")
            else:
                daily_itinerary = self._generate_daily_itinerary(highlights, days, style_type)

        if not daily_itinerary:
            daily_itinerary = self._generate_daily_itinerary(highlights, days, style_type)

        # 为每天生成详细的时间安排
        scheduled_days = []
        current_date = datetime.strptime(start_date, "%Y-%m-%d")

        for i, day_plan in enumerate(daily_itinerary[:days]):
            day_num = day_plan.get("day", i + 1)
            attractions = day_plan.get("attractions", [])
            pace = day_plan.get("pace", "中等节奏")

            # 获取当天天气
            day_weather = daily_weather[i] if weather_available and i < len(daily_weather) else None

            # 如果有天气且天气不佳，使用LLM搜索替代景点
            if day_weather and weather_available:
                if self._should_find_alternative_attractions(day_weather):
                    alternative_attractions = self._find_attractions_via_llm(
                        destination, day_weather, len(attractions), llm_to_use
                    )
                    if alternative_attractions:
                        attractions = alternative_attractions
                        logger.info(f"[景点排程师-LLM] 第{day_num}天根据天气调整为替代景点")

            # 创建每日时间安排
            schedule = self._create_daily_schedule(
                day_num,
                attractions,
                style_type,
                pace,
                current_date.strftime("%Y-%m-%d"),
                day_weather
            )

            scheduled_days.append(schedule)
            current_date += timedelta(days=1)

        logger.info(f"[景点排程师-LLM] 完成{len(scheduled_days)}天景点安排")

        # 生成LLM描述文本
        llm_description = self._generate_llm_description(
            destination,
            scheduled_days,
            style_type,
            llm_to_use
        )

        return {
            "scheduled_attractions": scheduled_days,
            "llm_description": llm_description,
            "tool_used": "llm_tools" if self._llm_with_tools else "direct"
        }

    def _get_weather_via_llm(
        self,
        destination: str,
        days: int,
        llm
    ) -> List[Dict[str, Any]]:
        """
        通过 LLM 工具调用获取天气预报（带缓存和共享）

        优先级：
        1. 共享数据中已有
        2. 缓存中的数据
        3. LLM 工具调用
        4. 直接调用
        """
        # 1. 检查共享数据
        try:
            from tradingagents.utils.shared_data import load_weather_forecast
            shared_weather = load_weather_forecast(destination)
            if shared_weather:
                logger.info(f"[景点排程师-LLM] 使用共享天气数据: {destination}")
                return shared_weather[:days]
        except Exception as e:
            logger.debug(f"[景点排程师-LLM] 共享天气获取失败: {e}")

        # 2. 检查缓存
        try:
            from tradingagents.utils.tool_cache import get_cache_manager, get_ttl_for_tool
            cache_manager = get_cache_manager()
            cached_weather = cache_manager.get(
                "weather_forecast",
                {"city": destination, "days": days},
                ttl=get_ttl_for_tool("weather_forecast")
            )
            if cached_weather:
                logger.info(f"[景点排程师-LLM] 使用缓存天气数据: {destination}")
                return cached_weather
        except Exception as e:
            logger.debug(f"[景点排程师-LLM] 缓存天气获取失败: {e}")

        # 3. LLM 工具调用或直接调用
        if not llm:
            return self._get_weather_direct(destination, days)

        # 尝试通过 LLM 获取天气
        try:
            from langchain_core.messages import HumanMessage

            prompt = f"""【必须使用工具】请使用 weather_forecast_tool 工具查询{destination}未来{days}天的天气预报。

重要提示：
1. 必须使用 weather_forecast_tool 工具来获取实时天气数据
2. 调用工具时参数：city="{destination}", days={days}
3. 请直接调用工具，不要猜测天气数据

工具调用示例：
weather_forecast_tool(city="{destination}", days={days})

获取到数据后，请整理返回每天的天气信息，包括：
- 日期
- 最高温度
- 最低温度
- 天气状况（晴、多云、雨等）
- 降水概率

请现在调用工具获取天气数据。"""

            response = llm.invoke([HumanMessage(content=prompt)])

            # 解析 LLM 返回的天气信息
            weather_data = self._parse_weather_response(response.content, days)

            if weather_data:
                logger.info(f"[景点排程师-LLM] LLM工具获取到{len(weather_data)}天天气")
                return weather_data

        except Exception as e:
            logger.warning(f"[景点排程师-LLM] LLM获取天气失败: {e}")

        # 回退到直接调用
        return self._get_weather_direct(destination, days)

    def _get_weather_direct(self, destination: str, days: int) -> List[Dict[str, Any]]:
        """直接调用天气工具（回退方法，带缓存保存）"""
        try:
            from tradingagents.tools.travel_tools import get_weather_forecast_tool
            from tradingagents.utils.tool_cache import get_cache_manager, get_ttl_for_tool
            from tradingagents.utils.shared_data import save_weather_forecast

            tool = get_weather_forecast_tool()
            forecast = tool.get_forecast(destination, days)

            # 处理返回结果
            if forecast and isinstance(forecast, dict) and "forecasts" in forecast:
                weather_data = forecast["forecasts"]
            elif isinstance(forecast, list):
                weather_data = forecast
            else:
                return []

            # 【缓存】保存到缓存
            if weather_data:
                try:
                    cache_manager = get_cache_manager()
                    cache_manager.set(
                        "weather_forecast",
                        {"city": destination, "days": days},
                        weather_data,
                        get_ttl_for_tool("weather_forecast")
                    )
                    logger.info(f"[景点排程师-LLM] 天气数据已缓存: {destination}")
                except Exception as e:
                    logger.debug(f"[景点排程师-LLM] 缓存保存失败: {e}")

                # 【共享数据】保存到共享数据
                try:
                    save_weather_forecast(destination, weather_data)
                    logger.info(f"[景点排程师-LLM] 天气数据已共享: {destination}")
                except Exception as e:
                    logger.debug(f"[景点排程师-LLM] 共享数据保存失败: {e}")

            return weather_data

        except Exception as e:
            logger.warning(f"[景点排程师-LLM] 直接获取天气失败: {e}")
            return []

    def _parse_weather_response(self, response: str, days: int) -> List[Dict[str, Any]]:
        """解析LLM返回的天气信息"""
        try:
            # 尝试从响应中提取JSON格式的天气数据
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
                data = json.loads(json_str)
                if isinstance(data, list):
                    return data
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
                data = json.loads(json_str)
                if isinstance(data, list):
                    return data
        except Exception as e:
            logger.debug(f"[景点排程师-LLM] 解析天气JSON失败: {e}")

        # 尝试从文本中提取天气信息
        return []

    def _should_find_alternative_attractions(self, weather: Dict[str, Any]) -> bool:
        """判断是否需要寻找替代景点"""
        condition = weather.get("weather", "").lower()
        temp_max = weather.get("temp_max", 30)

        # 雨天或极热/极冷天气需要调整
        return any([
            "雨" in condition,
            "rain" in condition,
            temp_max > 35,
            temp_max < 0
        ])

    def _find_attractions_via_llm(
        self,
        destination: str,
        weather: Dict[str, Any],
        limit: int,
        llm
    ) -> Optional[List[str]]:
        """通过 LLM 工具调用搜索适合当前天气的景点"""
        if not llm:
            return None

        try:
            condition = weather.get("weather", "")

            # 根据天气确定搜索关键词
            if "雨" in condition or "rain" in condition.lower():
                keywords = "博物馆 商场 室内景点"
                reason = "由于下雨，需要搜索室内景点"
            elif weather.get("temp_max", 30) > 32:
                keywords = "博物馆 水上乐园 室内 海滩"
                reason = "由于天气炎热，搜索有空调或水边的景点"
            elif weather.get("temp_min", 10) < 5:
                keywords = "博物馆 室内 温泉"
                reason = "由于天气寒冷，搜索室内景点"
            else:
                keywords = "景点 公园 文化遗址"
                reason = "搜索常规景点"

            prompt = f"""【必须使用工具】{reason}，请使用 attraction_search_tool 工具在{destination}搜索{limit}个景点。

重要提示：
1. 必须使用 attraction_search_tool 工具来获取实时景点数据
2. 调用工具时参数：city="{destination}", keywords="{keywords}", limit={limit}
3. 请直接调用工具，不要使用预设的景点列表

当前天气：{condition}，温度：{weather.get('temp_min', '')}°C - {weather.get('temp_max', '')}°C

工具调用示例：
attraction_search_tool(city="{destination}", keywords="{keywords}", limit={limit})

请现在调用工具获取景点数据。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])

            # 解析返回的景点列表
            attractions = self._parse_attractions_response(response.content)
            return attractions

        except Exception as e:
            logger.warning(f"[景点排程师-LLM] LLM搜索景点失败: {e}")
            return None

    def _parse_attractions_response(self, response: str) -> Optional[List[str]]:
        """解析LLM返回的景点列表"""
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
                data = json.loads(json_str)
                if isinstance(data, dict) and "attractions" in data:
                    return [a.get("name") if isinstance(a, dict) else a for a in data["attractions"]]
                elif isinstance(data, list):
                    return [d.get("name") if isinstance(d, dict) else d for d in data]
        except Exception as e:
            logger.debug(f"[景点排程师-LLM] 解析景点JSON失败: {e}")
        return None

    def _generate_daily_itinerary(
        self,
        attractions: List[str],
        days: int,
        style_type: str
    ) -> List[Dict[str, Any]]:
        """生成每日行程"""
        daily_plans = []
        attractions_per_day = max(1, len(attractions) // days)

        for day in range(1, days + 1):
            start_idx = (day - 1) * attractions_per_day
            end_idx = min(start_idx + attractions_per_day + 1, len(attractions))
            day_attractions = attractions[start_idx:end_idx]

            daily_plans.append({
                "day": day,
                "attractions": day_attractions,
                "pace": self._get_pace_by_style(style_type)
            })

        return daily_plans

    def _get_pace_by_style(self, style_type: str) -> str:
        """根据风格类型获取节奏描述"""
        pace_map = {
            "immersive": "慢节奏，深度体验",
            "exploration": "快节奏，高效游览",
            "relaxation": "最慢节奏，轻松休闲",
            "hidden_gem": "中等节奏，发现探索"
        }
        return pace_map.get(style_type, "中等节奏")

    def _create_daily_schedule(
        self,
        day_num: int,
        attractions: List[str],
        style_type: str,
        pace: str,
        date: str,
        weather: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """创建每日详细时间安排"""
        schedule_items = []
        time_slots = self._get_time_slots(style_type)

        # 天气信息
        weather_info = ""
        if weather:
            condition = weather.get("weather", "")
            temp_min = weather.get("temp_min", "")
            temp_max = weather.get("temp_max", "")
            if temp_min and temp_max:
                weather_info = f"({condition} {temp_min}°C-{temp_max}°C)"

        for slot in time_slots:
            if not attractions and slot["period"] not in ["lunch", "dinner"]:
                continue

            if slot["period"] in ["lunch", "dinner"]:
                schedule_items.append({
                    "period": slot["period"],
                    "time_range": slot["time"],
                    "activity": slot["activity"],
                    "location": "待定",
                    "description": slot["description"]
                })
            else:
                if attractions:
                    attraction = attractions.pop(0)
                    schedule_items.append({
                        "period": slot["period"],
                        "time_range": slot["time"],
                        "activity": f"游览{attraction}",
                        "location": attraction,
                        "description": self._get_attraction_description(attraction, style_type),
                        "ticket": {
                            "price": self._estimate_ticket_price(attraction),
                            "booking": "建议提前网上预约",
                            "tips": self._get_attraction_tips(attraction)
                        },
                        "tips": self._get_visit_tips(style_type, slot["period"])
                    })

        return {
            "day": day_num,
            "date": date,
            "title": f"第{day_num}天：{self._get_day_title(attractions, style_type)}",
            "schedule": schedule_items,
            "pace": pace
        }

    def _get_time_slots(self, style_type: str) -> List[Dict[str, str]]:
        """根据风格类型返回时间段配置"""
        if style_type == "immersive":
            return [
                {"period": "morning", "time": "09:00-12:00", "activity": "游览景点", "description": "深度游览，细细品味"},
                {"period": "lunch", "time": "12:00-13:30", "activity": "午餐", "description": "当地特色美食"},
                {"period": "afternoon", "time": "14:00-17:00", "activity": "游览景点", "description": "继续深度游览"},
                {"period": "dinner", "time": "18:00-20:00", "activity": "晚餐", "description": "当地特色餐厅"},
                {"period": "evening", "time": "20:00-21:30", "activity": "自由活动", "description": "探索周边，体验夜生活"}
            ]
        elif style_type == "exploration":
            return [
                {"period": "morning", "time": "08:30-12:00", "activity": "游览景点", "description": "高效打卡"},
                {"period": "lunch", "time": "12:00-13:00", "activity": "午餐", "description": "简餐，继续行程"},
                {"period": "afternoon", "time": "13:30-17:30", "activity": "游览景点", "description": "继续探索"},
                {"period": "dinner", "time": "18:00-19:30", "activity": "晚餐", "description": "特色美食"},
                {"period": "evening", "time": "19:30-21:00", "activity": "夜游/打卡", "description": "夜景或特色街区"}
            ]
        elif style_type == "relaxation":
            return [
                {"period": "morning", "time": "10:00-12:00", "activity": "游览景点", "description": "睡到自然醒，轻松游览"},
                {"period": "lunch", "time": "12:00-14:00", "activity": "悠闲午餐", "description": "慢慢享用美食"},
                {"period": "afternoon", "time": "15:00-17:00", "activity": "自由活动", "description": "回酒店休息或咖啡厅小坐"},
                {"period": "dinner", "time": "18:30-20:30", "activity": "晚餐", "description": "慢慢品尝美食"},
                {"period": "evening", "time": "21:00-22:00", "activity": "自由活动", "description": "散步或休息"}
            ]
        else:  # hidden_gem
            return [
                {"period": "morning", "time": "09:00-12:00", "activity": "探索景点", "description": "发现隐秘景点"},
                {"period": "lunch", "time": "12:00-13:30", "activity": "午餐", "description": "当地特色小馆"},
                {"period": "afternoon", "time": "14:00-17:00", "activity": "探索景点", "description": "继续探索"},
                {"period": "dinner", "time": "18:00-20:00", "activity": "晚餐", "description": "当地人推荐餐厅"},
                {"period": "evening", "time": "20:00-21:30", "activity": "夜游", "description": "发现夜景观光点"}
            ]

    def _get_day_title(self, attractions: List[str], style_type: str) -> str:
        """获取当天的标题"""
        if attractions:
            main_attraction = attractions[0] if attractions else "探索"
            if style_type == "immersive":
                return f"{main_attraction}深度体验"
            elif style_type == "exploration":
                return f"{main_attraction}及周边探索"
            elif style_type == "relaxation":
                return f"悠闲{main_attraction}之旅"
            else:
                return f"{main_attraction}隐秘探索"
        return "精彩一天"

    def _get_attraction_description(self, attraction: str, style_type: str) -> str:
        """获取景点描述"""
        descriptions = {
            "immersive": f"深度游览{attraction}，细细品味其文化与历史",
            "exploration": f"打卡{attraction}精华景点，高效游览",
            "relaxation": f"悠闲游览{attraction}，不赶时间",
            "hidden_gem": f"探索{attraction}的独特之处"
        }
        return descriptions.get(style_type, f"游览{attraction}")

    def _estimate_ticket_price(self, attraction: str) -> int:
        """估算门票价格"""
        price_map = {
            "故宫": 60, "长城": 45, "颐和园": 30, "天坛": 15,
            "西湖": 0, "灵隐寺": 30, "鼓浪屿": 0, "外滩": 0,
            "东方明珠": 220,
        }
        return price_map.get(attraction, 50)

    def _get_attraction_tips(self, attraction: str) -> List[str]:
        """获取景点游览提示"""
        tips = []
        if "故宫" in attraction:
            tips = ["建议提前网上预约", "周一闭馆，注意安排", "从午门进入，神武门出"]
        elif "长城" in attraction:
            tips = ["穿舒适运动鞋", "带好防晒用品", "建议缆车上下节省体力"]
        elif "西湖" in attraction:
            tips = ["建议租自行车游览", "早晚风景最佳", "可坐游船体验"]
        else:
            tips = ["建议提前了解开放时间", "注意天气情况"]
        return tips

    def _get_visit_tips(self, style_type: str, period: str) -> List[str]:
        """获取游览建议"""
        tips = []

        if style_type == "immersive":
            tips = ["放慢节奏，细细品味", "与当地人交流了解文化"]
        elif style_type == "exploration":
            tips = ["注意时间管理", "提前规划路线"]
        elif style_type == "relaxation":
            tips = ["累了就休息", "不要赶时间"]
        else:  # hidden_gem
            tips = ["留意细节", "拍照记录独特之处"]

        if period == "morning":
            tips.append("趁人少先游览主要景点")
        elif period == "afternoon":
            tips.append("下午适合深度体验")

        return tips

    def _generate_llm_description(
        self,
        destination: str,
        scheduled_days: List[Dict[str, Any]],
        style_type: str,
        llm
    ) -> str:
        """使用LLM生成景点安排的自然语言描述"""
        if not llm:
            return self._get_default_description(destination, scheduled_days, style_type)

        try:
            total_attractions = sum(
                1 for day in scheduled_days
                for item in day.get("schedule", [])
                if item.get("period") not in ["lunch", "dinner"]
            )

            highlights = [
                day.get("title", "")
                for day in scheduled_days[:3]
                if day.get("title")
            ]

            highlights_text = '\n'.join(highlights)
            style_desc = {
                "immersive": "深度文化体验",
                "exploration": "探索发现之旅",
                "relaxation": "轻松休闲度假",
                "hidden_gem": "小众宝藏探索"
            }.get(style_type, "精彩旅程")

            prompt = f"""请为以下景点安排生成一段自然、吸引人的描述文字（约150-200字）：

目的地：{destination}
旅行天数：{len(scheduled_days)}天
安排景点数：{total_attractions}个
旅行风格：{style_desc}
行程亮点：
{highlights_text}

描述要求：
1. 用兴奋期待的语气，让人对旅程充满期待
2. 突出目的地的主要景点和特色
3. 体现旅行风格的特点
4. 给出实用的游览建议
5. 语言要生动有趣，有画面感

请直接输出描述文字，不要标题和格式符号。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            description = response.content.strip()
            logger.info(f"[景点排程师-LLM] LLM生成描述成功: {len(description)}字")
            return description

        except Exception as e:
            logger.warning(f"[景点排程师-LLM] LLM生成描述失败: {e}，使用默认描述")
            return self._get_default_description(destination, scheduled_days, style_type)

    def _get_default_description(
        self,
        destination: str,
        scheduled_days: List[Dict[str, Any]],
        style_type: str
    ) -> str:
        """生成默认描述"""
        style_emoji = {
            "immersive": "🏛️",
            "exploration": "🧭",
            "relaxation": "🌸",
            "hidden_gem": "💎"
        }.get(style_type, "✨")

        total_attractions = sum(
            1 for day in scheduled_days
            for item in day.get("schedule", [])
            if item.get("period") not in ["lunch", "dinner"]
        )

        highlights = [day.get("title", "") for day in scheduled_days[:2] if day.get("title")]
        highlights_text = '、'.join(highlights[:2]) if highlights else f"{destination}精华景点"

        return f"""来{destination}，开启一场精彩的{len(scheduled_days)}天旅程！{style_emoji}

我们精心为您安排了{total_attractions}个精彩景点，包括{highlights_text}等必游之地。

📅 行程特色：
• 合理安排时间，轻松游览不赶路
• 经典景点与小众景点相结合，体验更丰富
• 根据天气灵活调整，确保最佳游览体验

💡 游览小贴士：
• 早起出门可以避开人流高峰
• 建议提前网上预约门票，节省现场排队时间
• 穿舒适的鞋子，每天步数不少哦
• 关注天气预报，准备合适的衣物
• 景点拍照时注意安全，不要为了拍照冒险

祝您旅途愉快！🎉"""


# ============================================================
# 导出工厂函数
# ============================================================

def create_attraction_scheduler_with_tools(llm=None) -> AttractionSchedulerWithTools:
    """创建带工具绑定的景点排程师"""
    return AttractionSchedulerWithTools(llm)


# ============================================================
# LangGraph 节点函数
# ============================================================

def attraction_scheduler_llm_tools_node(state: Dict) -> Dict:
    """景点排程节点（LLM工具调用版本）"""
    destination = state.get("selected_destination")
    dest_data = state.get("selected_destination_data", {})
    style_proposal = state.get("selected_style_proposal", {})
    days = state.get("days", 5)
    start_date = state.get("start_date", datetime.now().strftime("%Y-%m-%d"))
    llm = state.get("_llm")

    if not destination or not style_proposal:
        logger.error("[景点排程师-LLM] 缺少必要数据")
        return state

    # 创建带工具的排程师
    scheduler = create_attraction_scheduler_with_tools(llm)

    # 安排景点
    result = scheduler.schedule_attractions(
        destination,
        dest_data,
        style_proposal,
        days,
        start_date
    )

    # 更新状态
    from langchain_core.messages import AIMessage
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"景点排程完成: {days}天时间安排 (LLM工具调用)",
        name="AttractionSchedulerLLM"
    ))

    state["scheduled_attractions"] = result.get("scheduled_attractions", [])
    state["messages"] = messages

    return state


# ============================================================
# 餐饮推荐师 (LLM工具调用版本)
# ============================================================

class DiningRecommenderWithTools:
    """
    餐饮推荐师 - LLM工具调用版本

    使用 LLM + Tools 的方式，让 LLM 自主决定何时调用餐厅搜索工具
    """

    def __init__(self, llm=None):
        """
        初始化餐饮推荐师

        Args:
            llm: LLM 实例
        """
        self.llm = llm
        self._llm_with_tools = None

        # 绑定工具
        if llm and hasattr(llm, 'bind_tools'):
            from tradingagents.tools.langchain_tools import restaurant_search_tool
            tools = [restaurant_search_tool]
            self._llm_with_tools = llm.bind_tools(tools)
            logger.info(f"[餐饮推荐师-LLM] 已绑定 {len(tools)} 个工具")
        else:
            logger.warning("[餐饮推荐师-LLM] LLM不支持bind_tools，回退到直接调用模式")

    def recommend_dining(
        self,
        destination: str,
        scheduled_attractions: List[Dict[str, Any]],
        budget_level: str = "medium"
    ) -> Dict[str, Any]:
        """
        推荐餐饮

        使用 LLM 工具调用方式搜索餐厅

        Args:
            destination: 目的地名称
            scheduled_attractions: 已安排的景点日程
            budget_level: 预算等级

        Returns:
            餐饮推荐信息
        """
        logger.info(f"[餐饮推荐师-LLM] 为{destination}推荐餐饮")

        llm_to_use = self._llm_with_tools if self._llm_with_tools else self.llm

        # 收集需要推荐餐饮的区域
        areas_to_search = self._collect_dining_areas(scheduled_attractions)

        # 使用LLM搜索餐厅
        dining_recommendations = []

        for area in areas_to_search:
            restaurants = self._search_restaurants_via_llm(
                destination, area, budget_level, llm_to_use
            )
            if restaurants:
                dining_recommendations.extend(restaurants)

        # 如果没有找到足够的餐厅，使用LLM生成推荐
        if len(dining_recommendations) < 3:
            fallback_recommendations = self._generate_fallback_recommendations(
                destination, budget_level, llm_to_use
            )
            dining_recommendations.extend(fallback_recommendations)

        # 生成每日餐饮计划
        daily_dining = self._create_daily_dining_plan(
            scheduled_attractions, dining_recommendations, budget_level
        )

        # 生成LLM描述
        llm_description = self._generate_llm_description(
            destination,
            daily_dining,
            budget_level,
            llm_to_use
        )

        return {
            "destination": destination,
            "daily_dining": daily_dining,
            "dining_recommendations": dining_recommendations[:10],
            "llm_description": llm_description,
            "tool_used": "llm_tools" if self._llm_with_tools else "direct"
        }

    def _collect_dining_areas(self, scheduled_attractions: List[Dict]) -> List[str]:
        """收集需要推荐餐饮的区域"""
        areas = set()

        for day_schedule in scheduled_attractions:
            schedule = day_schedule.get("schedule", [])
            for item in schedule:
                location = item.get("location", "")
                if location and location != "待定":
                    # 使用景点位置作为搜索区域
                    areas.add(location)

        return list(areas)[:5]  # 限制最多5个区域

    def _search_restaurants_via_llm(
        self,
        destination: str,
        area: str,
        budget_level: str,
        llm
    ) -> List[Dict[str, Any]]:
        """通过 LLM 工具调用搜索餐厅"""
        if not llm:
            return self._search_restaurants_direct(destination, area, budget_level)

        try:
            budget_desc = {
                "economy": "经济实惠，人均50元以下",
                "medium": "中档，人均50-150元",
                "luxury": "高档精致，人均150元以上"
            }.get(budget_level, "中档")

            # 根据预算调整搜索关键词
            budget_keywords = {
                "economy": "便宜 实惠 人均50以下 小吃",
                "medium": "中档 人均50-150 特色",
                "luxury": "高档 精致 人均150以上"
            }.get(budget_level, "中档")

            prompt = f"""【必须使用工具】请使用 restaurant_search_tool 工具在{destination}的{area}附近搜索餐厅。

重要提示：
1. 必须使用 restaurant_search_tool 工具来获取实时餐厅数据
2. 调用工具时参数：city="{destination}", area="{area}", limit=10
3. 请直接调用工具，不要使用预设的餐厅列表

当前搜索区域：{area}
预算要求：{budget_desc}

工具调用示例：
restaurant_search_tool(city="{destination}", area="{area}", limit=10)

获取数据后，请筛选符合{budget_desc}要求的餐厅，返回餐厅的：
- 餐厅名称
- 地址
- 评分
- 预计人均消费

请现在调用工具获取餐厅数据。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])

            # 解析返回的餐厅列表
            restaurants = self._parse_restaurants_response(response.content)
            return restaurants

        except Exception as e:
            logger.warning(f"[餐饮推荐师-LLM] LLM搜索餐厅失败: {e}")
            return self._search_restaurants_direct(destination, area, budget_level)

    def _search_restaurants_direct(
        self,
        destination: str,
        area: str,
        budget_level: str
    ) -> List[Dict[str, Any]]:
        """直接调用餐厅工具（回退方法，带缓存保存）"""
        try:
            from tradingagents.tools.travel_tools import get_restaurant_search_tool
            from tradingagents.utils.tool_cache import get_cache_manager, get_ttl_for_tool

            # 检查缓存
            cache_manager = get_cache_manager()
            cache_key_params = {"city": destination, "area": area}
            cached_restaurants = cache_manager.get(
                "restaurant_search",
                cache_key_params,
                ttl=get_ttl_for_tool("restaurant_search")
            )

            if cached_restaurants:
                logger.info(f"[餐饮推荐师-LLM] 使用缓存餐厅数据: {destination} - {area}")
                return cached_restaurants

            # 缓存未命中，调用工具
            tool = get_restaurant_search_tool()
            restaurants = tool.search_restaurants(
                city=destination,
                area=area,
                limit=5
            )

            # 保存到缓存
            if restaurants:
                cache_manager.set(
                    "restaurant_search",
                    cache_key_params,
                    restaurants,
                    get_ttl_for_tool("restaurant_search")
                )
                logger.info(f"[餐饮推荐师-LLM] 餐厅数据已缓存: {destination} - {area}")

            return restaurants if restaurants else []

        except Exception as e:
            logger.warning(f"[餐饮推荐师-LLM] 直接搜索餐厅失败: {e}")
            return []

    def _parse_restaurants_response(self, response: str) -> List[Dict[str, Any]]:
        """解析LLM返回的餐厅列表"""
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
                data = json.loads(json_str)
                if isinstance(data, dict) and "restaurants" in data:
                    return data["restaurants"]
                elif isinstance(data, list):
                    return data
        except Exception as e:
            logger.debug(f"[餐饮推荐师-LLM] 解析餐厅JSON失败: {e}")
        return []

    def _generate_fallback_recommendations(
        self,
        destination: str,
        budget_level: str,
        llm
    ) -> List[Dict[str, Any]]:
        """生成后备推荐（当搜索失败时）"""
        try:
            prompt = f"""请为{destination}推荐3家适合{budget_level}预算的餐厅。

每家餐厅包含：
- 餐厅名称
- 推荐菜/特色
- 大致人均消费
- 推荐理由

请以JSON格式返回。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])

            # 解析返回
            restaurants = self._parse_restaurants_response(response.content)
            return restaurants if restaurants else []

        except Exception as e:
            logger.warning(f"[餐饮推荐师-LLM] 生成后备推荐失败: {e}")
            return []

    def _create_daily_dining_plan(
        self,
        scheduled_attractions: List[Dict],
        restaurants: List[Dict],
        budget_level: str
    ) -> List[Dict]:
        """创建每日餐饮计划"""
        daily_dining = []

        for day_schedule in scheduled_attractions:
            day_num = day_schedule.get("day", 1)
            schedule = day_schedule.get("schedule", [])

            # 找到午餐和晚餐时间段
            lunch_spot = None
            dinner_spot = None

            for item in schedule:
                if item.get("period") == "lunch":
                    lunch_spot = item.get("location", "")
                elif item.get("period") == "dinner":
                    dinner_spot = item.get("location", "")

            # 选择合适的餐厅
            lunch_restaurant = self._select_restaurant(lunch_spot, restaurants, budget_level)
            dinner_restaurant = self._select_restaurant(dinner_spot, restaurants, budget_level)

            daily_dining.append({
                "day": day_num,
                "lunch": lunch_restaurant or {"name": "待定", "area": lunch_spot or "市中心", "specialty": "当地特色菜"},
                "dinner": dinner_restaurant or {"name": "待定", "area": dinner_spot or "市中心", "specialty": "当地特色菜"}
            })

        return daily_dining

    def _select_restaurant(
        self,
        location: str,
        restaurants: List[Dict],
        budget_level: str
    ) -> Optional[Dict]:
        """选择合适的餐厅"""
        if not restaurants:
            return None

        # 如果有位置信息，优先选择附近的
        if location:
            for restaurant in restaurants:
                rest_location = restaurant.get("address", "")
                if location in rest_location or rest_location in location:
                    return {
                        "name": restaurant.get("name", ""),
                        "area": location,
                        "specialty": "当地特色",
                        "average_cost": restaurant.get("rating", 0) * 20  # 估算
                    }

        # 否则选择第一个
        first = restaurants[0]
        return {
            "name": first.get("name", ""),
            "area": first.get("address", "")[:20] if first.get("address") else "市中心",
            "specialty": "当地特色",
            "average_cost": first.get("rating", 0) * 20
        }

    def _generate_llm_description(
        self,
        destination: str,
        daily_dining: List[Dict],
        budget_level: str,
        llm
    ) -> str:
        """使用LLM生成餐饮推荐描述"""
        if not llm:
            return self._get_default_dining_description(destination, daily_dining, budget_level)

        try:
            sample_restaurants = []
            for day in daily_dining[:3]:
                lunch = day.get("lunch", {}).get("name", "")
                dinner = day.get("dinner", {}).get("name", "")
                if lunch:
                    sample_restaurants.append(f"午餐: {lunch}")
                if dinner:
                    sample_restaurants.append(f"晚餐: {dinner}")

            sample_text = "\n".join(sample_restaurants[:5])

            budget_desc = {
                "economy": "经济实惠",
                "medium": "舒适均衡",
                "luxury": "精致品质"
            }.get(budget_level, "舒适")

            prompt = f"""请为以下餐饮推荐生成一段吸引人的描述（约150-200字）：

目的地：{destination}
预算等级：{budget_desc}
推荐餐厅示例：
{sample_text}

描述要求：
1. 用美食探索的语气，让人对当地美食充满期待
2. 突出目的地美食特色
3. 给出实用的美食建议
4. 语言要生动有趣，有画面感

请直接输出描述文字，不要标题和格式符号。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            description = response.content.strip()
            logger.info(f"[餐饮推荐师-LLM] LLM生成描述成功: {len(description)}字")
            return description

        except Exception as e:
            logger.warning(f"[餐饮推荐师-LLM] LLM生成描述失败: {e}")
            return self._get_default_dining_description(destination, daily_dining, budget_level)

    def _get_default_dining_description(
        self,
        destination: str,
        daily_dining: List[Dict],
        budget_level: str
    ) -> str:
        """生成默认餐饮描述"""
        budget_desc = {
            "economy": "经济实惠",
            "medium": "舒适均衡",
            "luxury": "精致品质"
        }.get(budget_level, "舒适")

        return f"""在{destination}品尝地道美食，开启一场味蕾之旅！🍜🍲

我们为您精心安排了{len(daily_dining)}天的餐饮计划，涵盖当地特色美食，预算{budget_desc}。

🍽️ 餐饮特色：
• 精选当地人气餐厅，地道口味
• 每日午餐和晚餐合理搭配
• 融合当地特色与创新料理

💡 美食小贴士：
• 早点去热门餐厅排队，或提前预约
• 尝试当地街边小吃，往往有意外的惊喜
• 注意餐厅营业时间，避免跑空
• 不妨问问当地人推荐，他们最懂地道美食

祝您用餐愉快！🎉"""


# ============================================================
# 交通规划师 (LLM工具调用版本)
# ============================================================

class TransportPlannerWithTools:
    """
    交通规划师 - LLM工具调用版本

    使用 LLM + Tools 的方式，让 LLM 自主决定何时调用路径规划工具
    """

    def __init__(self, llm=None):
        """
        初始化交通规划师

        Args:
            llm: LLM 实例
        """
        self.llm = llm
        self._llm_with_tools = None

        # 绑定工具
        if llm and hasattr(llm, 'bind_tools'):
            from tradingagents.tools.langchain_tools import route_planning_tool
            tools = [route_planning_tool]
            self._llm_with_tools = llm.bind_tools(tools)
            logger.info(f"[交通规划师-LLM] 已绑定 {len(tools)} 个工具")
        else:
            logger.warning("[交通规划师-LLM] LLM不支持bind_tools，回退到直接调用模式")

    def plan_transport(
        self,
        destination: str,
        scheduled_attractions: List[Dict[str, Any]],
        budget_level: str = "medium"
    ) -> Dict[str, Any]:
        """
        规划交通方式

        使用 LLM 工具调用方式规划路径

        Args:
            destination: 目的地名称
            scheduled_attractions: 已安排的景点日程
            budget_level: 预算等级

        Returns:
            交通规划信息
        """
        logger.info(f"[交通规划师-LLM] 为{destination}规划交通方式")

        llm_to_use = self._llm_with_tools if self._llm_with_tools else self.llm

        # 为每天规划交通
        daily_transport = []
        total_cost = 0
        api_call_count = 0

        for day_schedule in scheduled_attractions:
            day_num = day_schedule.get("day", 1)
            schedule = day_schedule.get("schedule", [])

            day_transport = {
                "day": day_num,
                "transport_segments": []
            }

            # 分析当天的活动顺序，规划交通
            prev_location = "酒店"

            for item in schedule:
                period = item.get("period", "")
                location = item.get("location", item.get("activity", ""))

                # 跳过用餐时段
                if period in ["lunch", "dinner"]:
                    continue

                # 规划到该地点的交通
                if location and location != "待定":
                    transport_segment = self._plan_segment_via_llm(
                        prev_location,
                        location,
                        destination,
                        budget_level,
                        llm_to_use
                    )

                    if transport_segment and transport_segment.get("data_source") == "realtime_api":
                        api_call_count += 1

                    day_transport["transport_segments"].append(transport_segment)

                    if transport_segment:
                        total_cost += transport_segment.get("cost", 0)

                    prev_location = location

            daily_transport.append(day_transport)

        # 生成交通建议
        recommendations = self._get_transport_recommendations(destination, budget_level, llm_to_use)

        # 生成LLM描述
        llm_description = self._generate_llm_description(
            destination,
            daily_transport,
            budget_level,
            llm_to_use
        )

        return {
            "destination": destination,
            "daily_transport": daily_transport,
            "total_transport_cost": total_cost,
            "transport_recommendations": recommendations,
            "api_used": api_call_count > 0,
            "llm_description": llm_description,
            "tool_used": "llm_tools" if self._llm_with_tools else "direct"
        }

    def _plan_segment_via_llm(
        self,
        origin: str,
        destination: str,
        city: str,
        budget_level: str,
        llm
    ) -> Dict[str, Any]:
        """通过 LLM 工具调用规划单个交通路段"""
        if not llm:
            return self._estimate_transport_direct(origin, destination, city, budget_level)

        try:
            budget_desc = {
                "economy": "经济型，优先选择地铁/公交等公共交通",
                "medium": "舒适型，可考虑地铁或打车结合",
                "luxury": "品质型，优先选择打车/专车"
            }.get(budget_level, "舒适型")

            prompt = f"""【必须使用工具】请使用 route_planning_tool 工具规划从{origin}到{destination}的交通路线。

重要提示：
1. 必须使用 route_planning_tool 工具来获取实时路线数据
2. 调用工具时参数：origin="{origin}", destination="{destination}", city="{city}"
3. 请直接调用工具，不要使用估算数据

路线信息：
- 出发地：{origin}
- 目的地：{destination}
- 城市：{city}
- 预算要求：{budget_desc}

工具调用示例：
route_planning_tool(origin="{origin}", destination="{destination}", city="{city}")

获取到数据后，请整理返回：
- 推荐的交通方式
- 预计耗时
- 预计费用
- 简要路线描述

请现在调用工具获取路线数据。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])

            # 解析返回的路径信息
            route_info = self._parse_route_response(response.content)

            if route_info:
                route_info["data_source"] = "realtime_api"

                # 【缓存】保存到缓存
                try:
                    from tradingagents.utils.tool_cache import get_cache_manager, get_ttl_for_tool
                    cache_manager = get_cache_manager()
                    cache_manager.set(
                        "route_planning",
                        {"origin": origin, "destination": destination, "city": city},
                        route_info,
                        get_ttl_for_tool("route_planning")
                    )
                    logger.info(f"[交通规划师-LLM] 路径数据已缓存: {origin} -> {destination}")
                except Exception as e:
                    logger.debug(f"[交通规划师-LLM] 缓存保存失败: {e}")

                return route_info
            else:
                return self._estimate_transport_direct(origin, destination, city, budget_level)

        except Exception as e:
            logger.warning(f"[交通规划师-LLM] LLM规划路径失败: {e}")
            return self._estimate_transport_direct(origin, destination, city, budget_level)

    def _estimate_transport_direct(
        self,
        origin: str,
        destination: str,
        city: str,
        budget_level: str
    ) -> Dict[str, Any]:
        """直接估算交通（回退方法）"""
        # 简单估算
        distance_km = 5

        if budget_level == "economy":
            method = "地铁/公交"
            cost = 5
            duration = "40分钟"
        elif budget_level == "luxury":
            method = "打车"
            cost = 30
            duration = "20分钟"
        else:
            method = "地铁/公交或打车"
            cost = 15
            duration = "30分钟"

        return {
            "method": method,
            "route": f"从{origin}到{destination}",
            "duration": duration,
            "cost": cost,
            "data_source": "estimated"
        }

    def _parse_route_response(self, response: str) -> Optional[Dict[str, Any]]:
        """解析LLM返回的路径信息"""
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            elif "{" in response:
                # 尝试提取JSON对象
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            logger.debug(f"[交通规划师-LLM] 解析路径JSON失败: {e}")
        return None

    def _get_transport_recommendations(
        self,
        destination: str,
        budget_level: str,
        llm
    ) -> List[str]:
        """获取交通建议"""
        recommendations = []

        # 通用建议
        recommendations.append("建议下载当地交通APP（如：高德地图、百度地图）")

        if destination == "北京":
            recommendations.extend([
                "北京地铁发达，建议优先选择地铁出行",
                "早高峰(7-9点)避开三环内主要路段"
            ])
        elif destination == "上海":
            recommendations.extend([
                "上海地铁网络完善，推荐地铁出行",
                "外滩、南京路步行街建议地铁到达后步行"
            ])
        elif destination == "成都":
            recommendations.extend([
                "市区景点相对集中，打车比较便宜"
            ])
        else:
            recommendations.append("建议提前查询当地交通路线")

        # 根据预算建议
        if budget_level == "economy":
            recommendations.append("为节省费用，优先选择公共交通")
        elif budget_level == "luxury":
            recommendations.append("为节省时间，可考虑专车接送")

        return recommendations

    def _generate_llm_description(
        self,
        destination: str,
        daily_transport: List[Dict],
        budget_level: str,
        llm
    ) -> str:
        """使用LLM生成交通规划描述"""
        if not llm:
            return self._get_default_transport_description(destination, daily_transport, budget_level)

        try:
            # 统计主要交通方式
            transport_methods = []
            total_cost = 0

            for day in daily_transport:
                for segment in day.get("transport_segments", []):
                    method = segment.get("method", "")
                    if method and method not in transport_methods:
                        transport_methods.append(method)
                    total_cost += segment.get("cost", 0)

            methods_text = '、'.join(transport_methods[:5])

            prompt = f"""请为以下交通规划生成一段实用建议的描述（约150-200字）：

目的地：{destination}
主要交通方式：{methods_text}
预算等级：{budget_level}
总交通费用：约{total_cost}元

描述要求：
1. 用实用建议的语气，帮助用户高效出行
2. 突出当地交通特点和优势
3. 给出具体的交通方式和路线建议
4. 包含省时省费的小技巧
5. 语言要实用具体，有操作性

请直接输出描述文字，不要标题和格式符号。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            description = response.content.strip()
            logger.info(f"[交通规划师-LLM] LLM生成描述成功: {len(description)}字")
            return description

        except Exception as e:
            logger.warning(f"[交通规划师-LLM] LLM生成描述失败: {e}")
            return self._get_default_transport_description(destination, daily_transport, budget_level)

    def _get_default_transport_description(
        self,
        destination: str,
        daily_transport: List[Dict],
        budget_level: str
    ) -> str:
        """生成默认交通描述"""
        total_cost = sum(
            segment.get("cost", 0)
            for day in daily_transport
            for segment in day.get("transport_segments", [])
        )

        transport_methods = []
        for day in daily_transport:
            for segment in day.get("transport_segments", []):
                method = segment.get("method", "")
                if method and method not in transport_methods:
                    transport_methods.append(method)

        methods_text = '、'.join(transport_methods[:4]) if transport_methods else "地铁、公交、步行"

        return f"""在{destination}出行，交通非常便利！🚇🚕

推荐主要交通方式：{methods_text}

预计总交通费用约{total_cost}元，平均每天出行很经济实惠。

💡 出行小贴士：
• 建议下载当地交通APP，如高德地图/百度地图，实时导航很方便
• {methods_text.split('、')[0] if methods_text else '地铁'}是最可靠的出行方式，不易堵车
• 早晚高峰时段尽量错峰出行，节省时间
• 买一张交通卡或使用手机扫码，乘车更便捷

祝您出行顺利！🎯"""


# ============================================================
# 导出工厂函数
# ============================================================

def create_attraction_scheduler_with_tools(llm=None) -> AttractionSchedulerWithTools:
    """创建带工具绑定的景点排程师"""
    return AttractionSchedulerWithTools(llm)


def create_dining_recommender_with_tools(llm=None) -> DiningRecommenderWithTools:
    """创建带工具绑定的餐饮推荐师"""
    return DiningRecommenderWithTools(llm)


def create_transport_planner_with_tools(llm=None) -> TransportPlannerWithTools:
    """创建带工具绑定的交通规划师"""
    return TransportPlannerWithTools(llm)


# ============================================================
# LangGraph 节点函数
# ============================================================

def attraction_scheduler_llm_tools_node(state: Dict) -> Dict:
    """景点排程节点（LLM工具调用版本）"""
    destination = state.get("selected_destination")
    dest_data = state.get("selected_destination_data", {})
    style_proposal = state.get("selected_style_proposal", {})
    days = state.get("days", 5)
    start_date = state.get("start_date", datetime.now().strftime("%Y-%m-%d"))
    llm = state.get("_llm")

    if not destination or not style_proposal:
        logger.error("[景点排程师-LLM] 缺少必要数据")
        return state

    # 创建带工具的排程师
    scheduler = create_attraction_scheduler_with_tools(llm)

    # 安排景点
    result = scheduler.schedule_attractions(
        destination,
        dest_data,
        style_proposal,
        days,
        start_date
    )

    # 更新状态
    from langchain_core.messages import AIMessage
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"景点排程完成: {days}天时间安排 (LLM工具调用)",
        name="AttractionSchedulerLLM"
    ))

    state["scheduled_attractions"] = result.get("scheduled_attractions", [])
    state["messages"] = messages

    return state


def dining_recommender_llm_tools_node(state: Dict) -> Dict:
    """餐饮推荐节点（LLM工具调用版本）"""
    destination = state.get("selected_destination")
    scheduled_attractions = state.get("scheduled_attractions", [])
    user_portrait = state.get("user_portrait", {})
    budget_level = user_portrait.get("budget_level", "medium")
    llm = state.get("_llm")

    if not destination:
        logger.error("[餐饮推荐师-LLM] 缺少必要数据")
        return state

    # 创建带工具的推荐师
    recommender = create_dining_recommender_with_tools(llm)

    # 推荐餐饮
    result = recommender.recommend_dining(
        destination,
        scheduled_attractions,
        budget_level
    )

    # 更新状态
    from langchain_core.messages import AIMessage
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"餐饮推荐完成 (LLM工具调用)",
        name="DiningRecommenderLLM"
    ))

    state["dining_plan"] = result
    state["messages"] = messages

    return state


def transport_planner_llm_tools_node(state: Dict) -> Dict:
    """交通规划节点（LLM工具调用版本）"""
    destination = state.get("selected_destination")
    scheduled_attractions = state.get("scheduled_attractions", [])
    user_portrait = state.get("user_portrait", {})
    budget_level = user_portrait.get("budget_level", "medium")
    llm = state.get("_llm")

    if not destination:
        logger.error("[交通规划师-LLM] 缺少必要数据")
        return state

    # 创建带工具的规划师
    planner = create_transport_planner_with_tools(llm)

    # 规划交通
    result = planner.plan_transport(
        destination,
        scheduled_attractions,
        budget_level
    )

    # 更新状态
    from langchain_core.messages import AIMessage
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"交通规划完成: 总费用{result.get('total_transport_cost', 0)}元 (LLM工具调用)",
        name="TransportPlannerLLM"
    ))

    state["transport_plan"] = result
    state["messages"] = messages

    return state


__all__ = [
    "AttractionSchedulerWithTools",
    "DiningRecommenderWithTools",
    "TransportPlannerWithTools",
    "create_attraction_scheduler_with_tools",
    "create_dining_recommender_with_tools",
    "create_transport_planner_with_tools",
    "attraction_scheduler_llm_tools_node",
    "dining_recommender_llm_tools_node",
    "transport_planner_llm_tools_node",
]

