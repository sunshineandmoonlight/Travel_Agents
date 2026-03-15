"""
工具增强版详细攻略生成器

真正调用外部API工具：
- 高德地图API：景点搜索、餐厅推荐、路径规划
- Open-Meteo：天气预报
- Unsplash：景点图片

新增：分优先级图片加载
1. 立即返回预设图片（快速显示）
2. 后台异步获取真实图片（高质量）
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import threading
import requests

logger = logging.getLogger('travel_agents')


class ToolEnhancedGuideGenerator:
    """工具增强版详细攻略生成器"""

    # 预设图片字典（用于快速显示）
    PRESET_IMAGES = {
        "成都": {
            "熊猫基地": "https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=400&q=80",
            "宽窄巷子": "https://images.unsplash.com/photo-1496417263034-43cfaa8c8f74?w=400&q=80",
            "锦里": "https://images.unsplash.com/photo-1496417263034-43cfaa8c8f74?w=400&q=80",
            "武侯祠": "https://images.unsplash.com/photo-1496417263034-43cfaa8c8f74?w=400&q=80",
            "杜甫草堂": "https://images.unsplash.com/photo-1544197150-b9a2ce2bb4dd?w=400&q=80",
            "青城山": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&q=80",
            "都江堰": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&q=80",
            "春熙路": "https://images.unsplash.com/photo-1496417263034-43cfaa8c8f74?w=400&q=80",
            "IFS": "https://images.unsplash.com/photo-1496417263034-43cfaa8c8f74?w=400&q=80",
            "太古里": "https://images.unsplash.com/photo-1496417263034-43cfaa8c8f74?w=400&q=80",
        },
        "杭州": {
            "西湖": "https://images.unsplash.com/photo-1564760055775-d63b17a55c44?w=400&q=80",
            "灵隐寺": "https://images.unsplash.com/photo-1544197150-b9a2ce2bb4dd?w=400&q=80",
            "雷峰塔": "https://images.unsplash.com/photo-1564760055775-d63b17a55c44?w=400&q=80",
            "断桥": "https://images.unsplash.com/photo-1564760055775-d63b17a55c44?w=400&q=80",
            "苏堤": "https://images.unsplash.com/photo-1564760055775-d63b17a55c44?w=400&q=80",
        },
        "北京": {
            "故宫": "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=400&q=80",
            "长城": "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=400&q=80",
            "天安门": "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=400&q=80",
            "颐和园": "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=400&q=80",
            "天坛": "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=400&q=80",
        },
        "上海": {
            "外滩": "https://images.unsplash.com/photo-1548948485-9b29adda8fad?w=400&q=80",
            "东方明珠": "https://images.unsplash.com/photo-1548948485-9b29adda8fad?w=400&q=80",
            "豫园": "https://images.unsplash.com/photo-1548948485-9b29adda8fad?w=400&q=80",
            "南京路": "https://images.unsplash.com/photo-1548948485-9b29adda8fad?w=400&q=80",
        },
        "新加坡": {
            "滨海湾": "https://images.unsplash.com/photo-1525625296488-f6bc9439556f?w=400&q=80",
            "圣淘沙": "https://images.unsplash.com/photo-1525625296488-f6bc9439556f?w=400&q=80",
            "乌节路": "https://images.unsplash.com/photo-1548948485-9b29adda8fad?w=400&q=80",
            "植物园": "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=400&q=80",
            "牛车水": "https://images.unsplash.com/photo-1525625296488-f6bc9439556f?w=400&q=80",
            "鱼尾狮": "https://images.unsplash.com/photo-1525625296488-f6bc9439556f?w=400&q=80",
            "金沙": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&q=80",
        },
        "西安": {
            "兵马俑": "https://images.unsplash.com/photo-1528164344705-47542687000d?w=400&q=80",
            "大雁塔": "https://images.unsplash.com/photo-1528164344705-47542687000d?w=400&q=80",
            "古城墙": "https://images.unsplash.com/photo-1528164344705-47542687000d?w=400&q=80",
        },
        "三亚": {
            "蜈支洲": "https://images.unsplash.com/photo-1559128010-7c1ad6e1b6a5?w=400&q=80",
            "蜈支洲岛": "https://images.unsplash.com/photo-1559128010-7c1ad6e1b6a5?w=400&q=80",
            "亚龙湾": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&q=80",
            "天涯海角": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&q=80",
            "南山寺": "https://images.unsplash.com/photo-1544197150-b9a2ce2bb4dd?w=400&q=80",
            "海棠湾": "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=400&q=80",
            "大东海": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&q=80",
            "三亚湾": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&q=80",
            "槟榔谷": "https://images.unsplash.com/photo-1544197150-b9a2ce2bb4dd?w=400&q=80",
        },
    }

    def __init__(self, llm=None):
        self.llm = llm

    def _get_preset_image(self, attraction_name: str, city: str) -> str:
        """获取预设图片URL（快速返回，不调用API）"""
        # 精确匹配
        if city in self.PRESET_IMAGES and attraction_name in self.PRESET_IMAGES[city]:
            return self.PRESET_IMAGES[city][attraction_name]

        # 模糊匹配（景点名称包含关键词）
        if city in self.PRESET_IMAGES:
            for key, url in self.PRESET_IMAGES[city].items():
                if key in attraction_name or attraction_name in key:
                    return url

        # 通用城市图片（最后兜底）
        city_fallback = {
            "成都": "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=400&q=80",
            "杭州": "https://images.unsplash.com/photo-1564760055775-d63b17a55c44?w=400&q=80",
            "北京": "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=400&q=80",
            "上海": "https://images.unsplash.com/photo-1548948485-9b29adda8fad?w=400&q=80",
            "新加坡": "https://images.unsplash.com/photo-1525625296488-f6bc9439556f?w=400&q=80",
            "西安": "https://images.unsplash.com/photo-1528164344705-47542687000d?w=400&q=80",
            "三亚": "https://images.unsplash.com/photo-1559128010-7c1ad6e1b6a5?w=400&q=80",
        }

        return city_fallback.get(city, "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=400&q=80")

    def generate_detailed_guide(
        self,
        basic_guide: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成详细攻略（使用真实API工具）

        新增：分优先级图片加载
        1. 立即返回预设图片（快速显示）
        2. 后台异步获取真实图片（高质量）

        Args:
            basic_guide: 基础攻略数据

        Returns:
            详细攻略
        """
        destination = basic_guide.get("destination", "")
        days = basic_guide.get("total_days", 5)

        # 支持两种数据格式
        daily_itinerary = basic_guide.get("daily_itinerary") or basic_guide.get("daily_itineraries") or []

        detailed_guide = {
            "destination": destination,
            "total_days": days,
            "daily_itineraries": [],
            "weather_forecast": None,  # 将添加天气预报
            "tool_calls": []  # 记录工具调用
        }

        logger.info(f"[工具增强版攻略生成器] 为 {destination} 生成 {days} 天详细攻略（实时API）")
        logger.info(f"[工具增强版攻略生成器] daily_itinerary数量: {len(daily_itinerary)}")
        if daily_itinerary:
            logger.info(f"[工具增强版攻略生成器] 第一天数据: {daily_itinerary[0]}")

        # 首先获取天气预报
        try:
            from tradingagents.tools.travel_tools import get_weather_forecast_tool
            weather_tool = get_weather_forecast_tool()
            weather = weather_tool.get_forecast(destination, days=days)
            detailed_guide["weather_forecast"] = weather
            detailed_guide["tool_calls"].append("weather_forecast")
            logger.info(f"[工具增强版攻略生成器] 天气预报获取成功")
        except Exception as e:
            logger.warning(f"[工具增强版攻略生成器] 天气预报获取失败: {e}")

        # 逐天生成详细攻略
        for day_info in daily_itinerary:
            day_number = day_info.get("day", 1)
            logger.info(f"[工具增强版攻略生成器] 正在生成第 {day_number} 天详细攻略...")

            detailed_day = self._generate_detailed_day_with_tools(
                destination,
                day_number,
                day_info,
                detailed_guide.get("weather_forecast")
            )

            detailed_guide["daily_itineraries"].append(detailed_day)

        # 🔥 分优先级图片加载：立即添加预设图片（快速返回）
        detailed_guide = self._add_preset_images_fast(detailed_guide)
        logger.info(f"[工具增强版攻略生成器] 预设图片已添加，攻略可立即显示")

        # 💡 在后台线程中异步获取真实图片（不阻塞返回）
        def fetch_real_images_background():
            try:
                logger.info(f"[后台任务] 开始异步获取真实图片...")
                self._fetch_real_images_for_guide(detailed_guide)
                logger.info(f"[后台任务] 真实图片获取完成")
            except Exception as e:
                logger.error(f"[后台任务] 获取真实图片失败: {e}")

        # 启动后台线程
        thread = threading.Thread(target=fetch_real_images_background, daemon=True)
        thread.start()

        logger.info(f"[工具增强版攻略生成器] 详细攻略生成完成！")

        return detailed_guide

    def _add_preset_images_fast(self, guide: Dict[str, Any]) -> Dict[str, Any]:
        """
        快速添加预设图片（不调用API）

        为所有景点添加预设图片，标记 image_source="preset"
        前端会识别这个标记并进行轮询更新
        """
        destination = guide.get("destination", "")
        daily_itineraries = guide.get("daily_itineraries", [])

        logger.info(f"[快速预设图片] 开始为 {len(daily_itineraries)} 天行程添加预设图片")

        for day_idx, day in enumerate(daily_itineraries):
            schedule = day.get("schedule", [])
            for item_idx, item in enumerate(schedule):
                # 跳过餐饮活动
                period = item.get("period", "")
                if period in ["lunch", "dinner"]:
                    continue

                # 🔥 如果已经有真实图片（来自工具API），不覆盖
                current_source = item.get("image_source", "")
                if current_source == "api":
                    logger.info(f"[快速预设图片] 跳过已有真实图片的项目: {item.get('activity')}")
                    continue

                attraction_name = item.get("location") or item.get("activity") or ""
                if not attraction_name:
                    continue

                # 快速获取预设图片（不调用API）
                preset_url = self._get_preset_image(attraction_name, destination)

                daily_itineraries[day_idx]["schedule"][item_idx]["imageUrl"] = preset_url
                daily_itineraries[day_idx]["schedule"][item_idx]["image_source"] = "preset"
                daily_itineraries[day_idx]["schedule"][item_idx]["image_loading"] = False

        guide["daily_itineraries"] = daily_itineraries
        logger.info(f"[快速预设图片] 预设图片添加完成")
        return guide

    def _fetch_real_images_for_guide(self, guide: Dict[str, Any]) -> Dict[str, str]:
        """
        异步获取真实图片（用于后台任务）

        只获取没有预设图片的景点，使用更长的超时时间
        更新 guide 的 daily_itineraries 中的图片URL
        """
        destination = guide.get("destination", "")
        daily_itineraries = guide.get("daily_itineraries", [])

        # 收集所有需要获取图片的景点（去重）
        attraction_indices = {}
        attractions_to_fetch = []

        for day_idx, day in enumerate(daily_itineraries):
            schedule = day.get("schedule", [])
            for item_idx, item in enumerate(schedule):
                # 跳过餐饮活动
                period = item.get("period", "")
                if period in ["lunch", "dinner"]:
                    continue

                # 如果已经是预设图片，尝试获取真实图片
                if item.get("image_source") == "preset":
                    attraction_name = item.get("location") or item.get("activity") or ""
                    if attraction_name:
                        image_key = attraction_name
                        if image_key not in attraction_indices:
                            attraction_indices[image_key] = []
                            attractions_to_fetch.append(attraction_name)

                        # Always record position
                        attraction_indices[image_key].append((day_idx, item_idx))

        logger.info(f"[后台图片获取] 需要获取 {len(attractions_to_fetch)} 个景点的真实图片")

        # 获取图片URL
        fetched_urls = {}
        for attraction_name in attractions_to_fetch:
            url = self._fetch_attraction_image_with_retry(attraction_name, destination)
            if url:
                fetched_urls[attraction_name] = url
                logger.info(f"[后台图片获取] {attraction_name}: {url[:60]}...")

        # 更新所有使用该景点的位置的图片
        for attraction_name, url in fetched_urls.items():
            if attraction_name in attraction_indices:
                for day_idx, item_idx in attraction_indices[attraction_name]:
                    daily_itineraries[day_idx]["schedule"][item_idx]["imageUrl"] = url
                    daily_itineraries[day_idx]["schedule"][item_idx]["image_source"] = "api"
                    daily_itineraries[day_idx]["schedule"][item_idx]["has_real_image"] = True

        logger.info(f"[后台图片获取] 图片更新完成")

        return fetched_urls

    def _fetch_attraction_image_with_retry(self, attraction_name: str, city: str, max_retries: int = 2) -> str:
        """
        使用重试机制获取景点图片URL

        Args:
            attraction_name: 景点名称
            city: 城市
            max_retries: 最大重试次数

        Returns:
            图片URL，失败返回空字符串
        """
        for attempt in range(max_retries):
            for port in [8005, 8006, 8000]:
                try:
                    import requests
                    api_url = f"http://localhost:{port}/api/travel/images/attraction"
                    params = {
                        "attraction_name": attraction_name,
                        "city": city,
                        "width": 400,
                        "height": 300
                    }

                    response = requests.get(api_url, params=params, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        url = data.get("url", "")
                        # 确保不是占位图
                        if url and "placehold.co" not in url:
                            logger.info(f"[后台图片获取] {attraction_name} 从端口{port}获取成功")
                            return url
                except Exception as e:
                    logger.debug(f"[后台图片获取] 端口{port}尝试{attempt+1}失败: {str(e)[:50]}")
                    continue

        logger.warning(f"[后台图片获取] {attraction_name} 获取失败，保留预设图片")
        return ""

    def _generate_detailed_day_with_tools(
        self,
        destination: str,
        day_number: int,
        day_info: Dict,
        weather_forecast: Dict = None
    ) -> Dict[str, Any]:
        """生成单天的详细攻略（使用工具）"""

        # 保留原有信息（包括activities字段，用于fallback）
        detailed_day = {
            "day": day_number,
            "date": day_info.get("date", ""),
            "title": day_info.get("title", f"第{day_number}天精彩旅程"),
            "theme": day_info.get("theme", ""),
            "pace": day_info.get("pace", "适中"),
            "daily_budget": day_info.get("daily_budget", day_info.get("estimated_cost", 300)),
            "schedule": [],
            "activities": day_info.get("activities", [])  # 保留activities用于fallback
        }

        # 获取当天的行程安排
        schedule_items = day_info.get("schedule", [])
        # 如果schedule为空或不存在，尝试从activities提取
        if not schedule_items:
            schedule_items = self._extract_schedule_from_old_format(day_info)
        else:
            logger.info(f"[工具增强版] day_info已有schedule，数量: {len(schedule_items)}")

        # 添加当天天气
        if weather_forecast and weather_forecast.get("forecasts"):
            forecasts = weather_forecast["forecasts"]
            if day_number - 1 < len(forecasts):
                detailed_day["weather"] = forecasts[day_number - 1]

        # 逐个活动生成详细信息（调用工具）
        for idx, item in enumerate(schedule_items):
            logger.info(f"[工具增强版] 第{day_number}天处理第{idx+1}个schedule项: period={item.get('period')}, activity={item.get('activity')[:30]}")
            # 添加缺失的time_range
            if not item.get("time_range"):
                period = item.get("period", "")
                time_range = self._get_time_range_for_period(period)
                item["time_range"] = time_range

            detailed_item = self._generate_detailed_item_with_tools(
                destination,
                day_number,
                item
            )
            detailed_day["schedule"].append(detailed_item)

        logger.info(f"[工具增强版] 第{day_number}天schedule处理完成，共{len(detailed_day['schedule'])}项")
        return detailed_day

    def _generate_detailed_item_with_tools(
        self,
        destination: str,
        day: int,
        item: Dict
    ) -> Dict[str, Any]:
        """生成单个活动的详细信息（调用API工具）"""

        time_range = item.get("time_range", "")
        period = item.get("period", "")
        activity = item.get("activity", "")
        location = item.get("location", activity)

        detailed_item = {
            "time_range": time_range,
            "period": period,
            "activity": activity,
            "location": location,
            "expanded": False,
            "tool_generated": True  # 标记为工具生成
        }

        # 根据活动类型调用不同的工具
        if period in ["lunch", "dinner"]:
            # 用餐活动 - 调用餐厅搜索工具
            detailed_item.update(self._generate_dining_with_tools(destination, day, item))
        elif period in ["morning", "afternoon", "evening"]:
            # 游览活动 - 调用景点搜索和图片工具
            detailed_item.update(self._generate_attraction_with_tools(destination, day, item))

        return detailed_item

    def _generate_dining_with_tools(self, destination: str, day: int, item: Dict) -> Dict:
        """生成用餐详细信息（调用餐厅搜索工具）"""
        meal_type = item.get("period", "lunch")
        time_range = item.get("time_range", "")
        location = item.get("location", "")

        dining_details = {
            "type": "dining",
            "time_range": time_range,
            "location": location,
            "recommendations": {}
        }

        try:
            from tradingagents.tools.travel_tools import get_restaurant_search_tool
            restaurant_tool = get_restaurant_search_tool()

            # 调用餐厅搜索工具
            restaurants = restaurant_tool.search_restaurants(
                city=destination,
                area=location,
                limit=5
            )

            if restaurants:
                # 选择评分最高的餐厅
                best = max(restaurants, key=lambda x: x.get("rating", 0))

                # 获取菜品推荐
                signature_dishes = self._get_signature_dishes(best["name"], destination)

                # 估算费用
                cost_str = best.get("cost", "")
                estimated_cost = 100
                if "元" in cost_str:
                    try:
                        estimated_cost = int(cost_str.replace("元", "").strip())
                    except:
                        pass

                dining_details["recommendations"] = {
                    "restaurant": best["name"],
                    "address": best["address"],
                    "rating": best["rating"],
                    "signature_dishes": signature_dishes,
                    "average_cost": estimated_cost,
                    "tips": f"推荐评分{best['rating']}的餐厅，{best.get('type', '餐饮')}",
                    "tool_source": "amap_api"
                }

                logger.info(f"[工具增强版] 第{day}天{meal_type}餐厅推荐（工具）: {best['name']}")

        except Exception as e:
            logger.warning(f"[工具增强版] 餐厅搜索失败: {e}，使用降级方案")
            # 降级到预置数据
            from tradingagents.services.enhanced_guide_generator import EnhancedGuideGenerator
            fallback = EnhancedGuideGenerator(self.llm)
            dining_details["recommendations"] = fallback._get_smart_restaurant(destination, location, meal_type, day)

        dining_details["has_details"] = True

        return dining_details

    def _generate_attraction_with_tools(self, destination: str, day: int, item: Dict) -> Dict:
        """生成景点详细信息（调用景点搜索和图片工具）"""
        activity = item.get("activity", "")
        location = item.get("location", activity)
        time_range = item.get("time_range", "")

        attraction_details = {
            "type": "attraction",
            "time_range": time_range,
            "activity": activity,
            "location": location
        }

        try:
            from tradingagents.tools.travel_tools import (
                get_attraction_search_tool,
                get_image_search_tool
            )

            attraction_tool = get_attraction_search_tool()
            image_tool = get_image_search_tool()

            # 1. 搜索景点详情
            attractions = attraction_tool.search_attractions(
                city=destination,
                keywords=location,
                limit=1
            )

            if attractions:
                attraction = attractions[0]

                # 使用LLM生成景点描述
                description = self._generate_attraction_description_with_llm(
                    attraction,
                    destination,
                    self.llm
                )

                attraction_details.update({
                    "description": description,
                    "highlights": [f"{location}的特色景点"],
                    "suggested_route": "按照景区指示游览",
                    "tips": [f"建议游览时间2-3小时"],
                    "tickets": {"price": "请以景区实际价格为准"},
                    "tool_source": "amap_api"
                })

                # 2. 搜索景点图片
                image_url = image_tool.search_attraction_image(location, destination)
                if image_url:
                    attraction_details["imageUrl"] = image_url
                    attraction_details["image_source"] = "api"  # 标记为API获取的真实图片
                    logger.info(f"[工具增强版] 第{day}天景点图片获取成功: {location}")

        except Exception as e:
            logger.warning(f"[工具增强版] 景点搜索失败: {e}，使用降级方案")
            # 降级到预置数据
            from tradingagents.services.enhanced_guide_generator import EnhancedGuideGenerator
            fallback = EnhancedGuideGenerator(self.llm)
            smart_details = fallback._get_smart_attraction_details(destination, location)

            attraction_details.update(smart_details)

        # 3. 添加交通信息（使用路径规划工具）
        try:
            from tradingagents.tools.travel_tools import get_route_planning_tool
            route_tool = get_route_planning_tool()

            # 如果有上一个地点的信息，可以规划路径
            # 这里简化处理，使用默认交通建议
            attraction_details["transport"] = {
                "method": "建议使用公共交通或打车",
                "duration": "约30分钟",
                "cost": 30,
                "tips": f"建议提前查询从上一地点到{location}的交通方式"
            }

        except Exception as e:
            logger.warning(f"[工具增强版] 交通规划失败: {e}")

        attraction_details["has_details"] = True

        return attraction_details

    def _generate_attraction_description_with_llm(
        self,
        attraction: Dict,
        city: str,
        llm
    ) -> str:
        """使用LLM生成景点描述"""
        if not llm:
            return f"{attraction['name']}是{city}的热门景点，值得一游。"

        try:
            from langchain_core.messages import HumanMessage

            prompt = f"""
请为以下景点生成一个简洁的描述（80-120字）：

景点名称：{attraction.get('name', '')}
地址：{attraction.get('address', '')}
城市：{city}

要求：
1. 突出景点特色和亮点
2. 简洁生动，有吸引力
3. 80-120字之间
"""

            response = llm.invoke([HumanMessage(content=prompt)])
            description = response.content.strip()

            if len(description) > 50:
                return description

        except Exception as e:
            logger.warning(f"[工具增强版] LLM生成描述失败: {e}")

        return f"{attraction.get('name', '')}是{city}的热门景点，拥有独特的魅力和历史文化底蕴，值得深入游览探索。"

    def _get_signature_dishes(self, restaurant_name: str, city: str) -> List[Dict]:
        """获取招牌菜品（基于城市特色）"""
        # 城市特色菜品数据库
        city_dishes = {
            "北京": [
                {"name": "北京烤鸭", "price": 198, "description": "皮酥肉嫩的经典北京菜"},
                {"name": "炸酱面", "price": 28, "description": "老北京家常面食"}
            ],
            "上海": [
                {"name": "小笼包", "price": 45, "description": "皮薄汁鲜的上海特色"},
                {"name": "红烧肉", "price": 68, "description": "浓油赤酱的本帮菜"}
            ],
            "成都": [
                {"name": "麻婆豆腐", "price": 38, "description": "麻辣鲜香的川菜代表"},
                {"name": "火锅", "price": 128, "description": "成都人的灵魂食物"}
            ],
            "广州": [
                {"name": "白切鸡", "price": 58, "description": "清淡鲜美的粤菜经典"},
                {"name": "肠粉", "price": 22, "description": "广州早餐文化代表"}
            ],
            "西安": [
                {"name": "肉夹馍", "price": 18, "description": "中式汉堡，陕西特色"},
                {"name": "羊肉泡馍", "price": 38, "description": "浓郁鲜美的传统美食"}
            ],
            "杭州": [
                {"name": "西湖醋鱼", "price": 88, "description": "酸甜可口的杭州名菜"},
                {"name": "龙井虾仁", "price": 98, "description": "清淡鲜美的浙江菜"}
            ]
        }

        dishes = city_dishes.get(city, [
            {"name": f"{city}特色菜", "price": 68, "description": "当地特色美食"}
        ])

        return dishes

    def _get_time_range_for_period(self, period: str) -> str:
        """根据时段返回时间范围"""
        time_ranges = {
            "morning": "09:00-12:00",
            "lunch": "12:00-13:30",
            "afternoon": "14:00-17:00",
            "dinner": "18:00-20:00",
            "evening": "20:00-21:30"
        }
        return time_ranges.get(period, "")

    def _extract_schedule_from_old_format(self, day_info: Dict) -> List[Dict]:
        """从旧格式提取行程安排

        支持两种格式：
        1. activities数组格式：[{"time": "上午", "activity": "...", "attraction_id": "..."}, ...]
        2. 时段键格式：{"morning": {...}, "lunch": {...}, ...}
        """
        schedule = []

        # 优先使用activities数组格式（来自Group B智能体）
        activities = day_info.get("activities", [])
        logger.info(f"[工具增强版] _extract_schedule_from_old_format: activities数量={len(activities)}")
        if activities:
            # 时期映射（支持多种可能的中文表述）
            time_mapping = {
                "上午": "morning",
                "中午": "lunch",
                "下午": "afternoon",
                "晚上": "evening"
            }

            # 如果时间字段映射失败，使用索引位置作为fallback
            period_fallback = ["morning", "lunch", "afternoon", "evening"]

            for idx, activity in enumerate(activities):
                time_cn = activity.get("time", "")
                period = time_mapping.get(time_cn, "")

                # Fallback: 如果没有映射到时段，使用索引
                if not period and idx < len(period_fallback):
                    period = period_fallback[idx]

                if period:
                    item = {
                        "period": period,
                        "time_range": "",  # 将在后续处理时填充
                        "activity": activity.get("activity", ""),
                        "location": activity.get("attraction_id", activity.get("activity", ""))
                    }
                    schedule.append(item)

            logger.info(f"[工具增强版] 从activities提取了{len(schedule)}个schedule项")
            return schedule

        # 降级：使用时段键格式
        periods = ["morning", "lunch", "afternoon", "dinner", "evening"]
        for period in periods:
            if period in day_info and day_info[period]:
                period_data = day_info[period]

                item = {
                    "period": period,
                    "time_range": period_data.get("time", ""),
                    "activity": period_data.get("activity", ""),
                    "location": period_data.get("attraction", period_data.get("activity", ""))
                }

                if "estimated_cost" in period_data:
                    item["estimated_cost"] = period_data["estimated_cost"]

                schedule.append(item)

        return schedule


def create_tool_enhanced_guide_generator(llm=None) -> ToolEnhancedGuideGenerator:
    """创建工具增强版详细攻略生成器"""
    return ToolEnhancedGuideGenerator(llm)

