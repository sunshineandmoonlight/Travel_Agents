"""
景点排程师 (Agent C1)

职责: 根据地理位置优化游览顺序，分配每日时间段
输入: 景点列表 + 风格方案 + 天气预报
输出: 每日景点时间安排
- 调用天气工具API获取天气预报
- 根据天气调整行程（雨天安排室内景点）
"""

from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger('travel_agents')


def _get_weather_forecast(destination: str, days: int) -> List[Dict[str, Any]]:
    """
    调用天气工具获取天气预报

    Args:
        destination: 目的地名称
        days: 天数

    Returns:
        天气预报列表
    """
    try:
        from tradingagents.tools.travel_tools import get_weather_forecast_tool

        weather_tool = get_weather_forecast_tool()
        forecast = weather_tool.get_forecast(destination, days)

        if forecast:
            logger.info(f"[景点排程师] 成功获取{len(forecast)}天天气预报")
            return forecast
        else:
            return []

    except Exception as e:
        logger.warning(f"[景点排程师] 天气获取失败: {e}")
        return []


def _get_attractions_for_weather(
    destination: str,
    weather: Dict[str, Any],
    limit: int = 3
) -> List[Dict[str, Any]]:
    """
    根据天气获取适合的景点

    Args:
        destination: 目的地名称
        weather: 天气信息
        limit: 返回数量限制

    Returns:
        景点列表
    """
    try:
        from tradingagents.tools.travel_tools import get_attraction_search_tool

        attraction_tool = get_attraction_search_tool()

        # 判断天气状况
        condition = weather.get("condition", "").lower()

        if "rain" in condition or "雨" in condition:
            # 雨天：搜索室内景点
            keywords = "博物馆 商场 室内景点 购物中心"
        elif "hot" in condition or "热" in condition or weather.get("temp_max", 30) > 32:
            # 热天：搜索有空调的地方或水边
            keywords = "博物馆 水上乐园 室内 海滩 湖"
        elif "cold" in condition or "冷" in condition or weather.get("temp_min", 10) < 5:
            # 冷天：搜索室内景点
            keywords = "博物馆 室内 温泉 购物中心"
        else:
            # 正常天气：搜索常规景点
            keywords = "景点 公园 文化遗址"

        attractions = attraction_tool.search_attractions(
            city=destination,
            keywords=keywords,
            limit=limit
        )

        if attractions:
            logger.info(f"[景点排程师] 根据天气搜索到{len(attractions)}个景点")
            return attractions
        else:
            return []

    except Exception as e:
        logger.warning(f"[景点排程师] 景点搜索失败: {e}")
        return []


def schedule_attractions(
    destination: str,
    dest_data: Dict[str, Any],
    style_proposal: Dict[str, Any],
    days: int,
    start_date: str,
    llm=None
) -> Dict[str, Any]:
    """
    安排景点游览时间表

    优先调用天气工具API，根据天气调整行程安排

    Args:
        destination: 目的地名称
        dest_data: 目的地数据
        style_proposal: 风格方案（包含daily_itinerary）
        days: 旅行天数
        start_date: 开始日期
        llm: LLM实例（可选）

    Returns:
        包含每日景点时间安排列表和LLM描述的字典
    """
    logger.info(f"[景点排程师] 为{destination}安排{days}天景点时间表")

    # 1. 调用天气工具获取天气预报
    daily_weather = _get_weather_forecast(destination, days)
    weather_available = len(daily_weather) > 0

    if weather_available:
        logger.info(f"[景点排程师] 已获取天气预报，将根据天气调整行程")
    else:
        logger.info(f"[景点排程师] 天气获取失败，使用默认行程安排")

    style_type = style_proposal.get("style_type", "immersive")
    daily_itinerary = style_proposal.get("daily_itinerary", [])

    if not daily_itinerary:
        # 如果没有每日行程，使用景点列表生成
        highlights = dest_data.get("highlights", [])
        daily_itinerary = _generate_daily_itinerary(highlights, days, style_type)

    # 2. 为每天生成详细的时间安排（使用智能体辅助）
    scheduled_days = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")

    for i, day_plan in enumerate(daily_itinerary[:days]):
        day_num = day_plan.get("day", i + 1)
        attractions = day_plan.get("attractions", [])
        pace = day_plan.get("pace", "中等节奏")

        # 获取当天天气
        day_weather = daily_weather[i] if weather_available and i < len(daily_weather) else None

        # 根据天气调整景点
        if day_weather and weather_available:
            # 尝试根据天气获取更合适的景点
            weather_attractions = _get_attractions_for_weather(destination, day_weather, limit=len(attractions))
            if weather_attractions and len(weather_attractions) > 0:
                # 使用天气适配的景点
                attractions = [a.get("name", a) for a in weather_attractions]
                logger.info(f"[景点排程师] 第{day_num}天根据天气调整为室内景点")

        # 生成当天的时间安排（使用智能体辅助）
        schedule = _create_daily_schedule_with_agents(
            day_num,
            attractions,
            style_type,
            pace,
            current_date.strftime("%Y-%m-%d"),
            day_weather,
            destination,
            llm
        )

        scheduled_days.append(schedule)
        current_date += timedelta(days=1)

    logger.info(f"[景点排程师] 完成{len(scheduled_days)}天景点安排")

    # 生成LLM描述文本
    llm_description = _generate_attraction_description(
        destination,
        scheduled_days,
        style_type,
        llm
    )

    return {
        "scheduled_attractions": scheduled_days,
        "llm_description": llm_description
    }


def _generate_daily_itinerary(
    attractions: List[str],
    days: int,
    style_type: str
) -> List[Dict[str, Any]]:
    """生成每日行程（当没有预定义行程时）"""
    daily_plans = []
    attractions_per_day = max(1, len(attractions) // days)

    for day in range(1, days + 1):
        start_idx = (day - 1) * attractions_per_day
        end_idx = min(start_idx + attractions_per_day + 1, len(attractions))
        day_attractions = attractions[start_idx:end_idx]

        daily_plans.append({
            "day": day,
            "attractions": day_attractions,
            "pace": _get_pace_by_style(style_type)
        })

    return daily_plans


def _get_attraction_transport_info(
    attraction: str,
    destination: str,
    period: str,
    prev_location: str = None
) -> Dict[str, Any]:
    """获取景点的交通信息"""
    # 根据目的地和景点生成具体的交通信息
    transport_info = {
        "method": "地铁/公交",
        "route": "",
        "duration": "约30分钟",
        "cost": 5,
        "tips": ""
    }

    # 针对热门城市和景点生成具体交通信息
    if destination == "北京":
        if attraction == "故宫" or "故宫" in attraction:
            transport_info = {
                "method": "地铁",
                "route": "地铁1号线天安门东站D口",
                "duration": "约30分钟",
                "cost": 4,
                "tips": "建议早上8点前到达避开人流"
            }
        elif attraction == "颐和园" or "颐和园" in attraction:
            transport_info = {
                "method": "地铁",
                "route": "地铁4号线北宫门站D口",
                "duration": "约50分钟",
                "cost": 5,
                "tips": "北宫门离主要景点更近"
            }
        elif attraction == "天坛" or "天坛" in attraction:
            transport_info = {
                "method": "地铁",
                "route": "地铁5号线天坛东门站A口",
                "duration": "约35分钟",
                "cost": 4,
                "tips": "东门进入离祈年殿最近"
            }
    elif destination == "上海":
        if attraction == "外滩" or "外滩" in attraction:
            transport_info = {
                "method": "地铁",
                "route": "地铁2号线南京东路站",
                "duration": "约25分钟",
                "cost": 4,
                "tips": "晚上看夜景最佳"
            }
        elif attraction == "东方明珠" or "东方明珠" in attraction:
            transport_info = {
                "method": "地铁",
                "route": "地铁2号线陆家嘴站",
                "duration": "约30分钟",
                "cost": 4,
                "tips": "建议提前网上购票"
            }
    elif destination == "成都":
        if attraction == "大熊猫繁育研究基地" or "熊猫" in attraction:
            transport_info = {
                "method": "地铁+公交",
                "route": "地铁3号线熊猫大道站 + 公交87路",
                "duration": "约1小时",
                "cost": 8,
                "tips": "建议早上7:30前到达看熊猫活跃"
            }
        elif attraction == "宽窄巷子" or "宽窄巷子" in attraction:
            transport_info = {
                "method": "地铁",
                "route": "地铁4号线宽窄巷子站B口",
                "duration": "约20分钟",
                "cost": 4,
                "tips": "适合晚上逛，有小吃和酒吧"
            }
    elif destination == "西安":
        if attraction == "兵马俑" or "秦始皇兵马俑" in attraction:
            transport_info = {
                "method": "地铁+公交",
                "route": "地铁9号线华清池站 + 临潼游601路",
                "duration": "约1.5小时",
                "cost": 15,
                "tips": "建议报当地一日游，省心方便"
            }
        elif attraction == "大雁塔" or "大雁塔" in attraction:
            transport_info = {
                "method": "地铁",
                "route": "地铁3号线/4号线大雁塔站",
                "duration": "约40分钟",
                "cost": 4,
                "tips": "晚上有音乐喷泉表演"
            }
        elif attraction == "回民街" or "回民街" in attraction:
            transport_info = {
                "method": "地铁",
                "route": "地铁1号线或6号线洒金桥站",
                "duration": "约30分钟",
                "cost": 4,
                "tips": "建议下午去，晚上更热闹"
            }
    elif destination == "杭州":
        if attraction == "西湖" or "西湖" in attraction:
            transport_info = {
                "method": "地铁",
                "route": "地铁1号线龙翔桥站",
                "duration": "约30分钟",
                "cost": 4,
                "tips": "推荐骑行或步行环湖"
            }
        elif attraction == "灵隐寺" or "灵隐寺" in attraction:
            transport_info = {
                "method": "公交",
                "route": "灵隐专线/7路公交车",
                "duration": "约45分钟",
                "cost": 5,
                "tips": "可以逛飞来峰景区"
            }

    return transport_info


def _get_attraction_ticket_info(attraction: str, destination: str) -> Dict[str, Any]:
    """获取景点的门票信息"""
    ticket_info = {
        "price": _estimate_ticket_price(attraction),  # 改为 price 字段
        "adult_price": _estimate_ticket_price(attraction),
        "student_price": int(_estimate_ticket_price(attraction) * 0.5),
        "notes": f"建议提前网上预约，学生票{int(_estimate_ticket_price(attraction) * 0.5)}元",  # 新增 notes 字段
        "booking_tips": "建议提前网上预约",
        "must_bring": "身份证原件",
        "highlights": []
    }

    # 针对热门景点添加详细信息
    if destination == "北京":
        if attraction == "故宫" or "故宫" in attraction:
            ticket_info = {
                "price": 60,  # 新增
                "adult_price": 60,
                "student_price": 20,
                "notes": "提前在'故宫博物院观众服务'微信小程序预约，学生票20元",  # 新增
                "booking_tips": "提前在'故宫博物院观众服务'微信小程序预约",
                "must_bring": "身份证原件",
                "recommended_route": "午门 → 太和殿 → 中和殿 → 保和殿 → 乾清宫 → 御花园 → 神武门(出)",
                "key_attractions": ["太和殿(金銮殿)", "乾清宫", "御花园"],
                "photo_spots": ["太和殿前广场", "御花园古树", "角楼"],
                "tips": "9点开门时直接冲三大殿，返程看御花园"
            }
        elif attraction == "颐和园" or "颐和园" in attraction:
            ticket_info = {
                "price": 30,  # 新增
                "adult_price": 30,
                "student_price": 15,
                "notes": "提前在'颐和园'官方小程序预约，学生票15元",  # 新增
                "booking_tips": "提前在'颐和园'官方小程序预约",
                "must_bring": "身份证原件",
                "recommended_route": "北宫门入 → 长廊 → 佛香阁 → 石舫 → 新建宫门出",
                "key_attractions": ["佛香阁", "长廊", "石舫"],
                "photo_spots": ["佛香阁俯瞰昆明湖", "十七孔桥"],
                "tips": "从北宫门进入离主要景点更近"
            }
        elif attraction == "天坛" or "天坛" in attraction:
            ticket_info = {
                "price": 15,  # 新增
                "adult_price": 15,
                "student_price": 8,
                "notes": "提前在'天坛'官方小程序预约，学生票8元",  # 新增
                "booking_tips": "提前在'天坛'官方小程序预约",
                "must_bring": "身份证原件",
                "recommended_route": "东门入 → 祈年殿 → 皇穹宇 → 圜丘 → 西门出",
                "key_attractions": ["祈年殿", "回音壁", "圜丘"],
                "photo_spots": ["祈年殿全景", "回音壁"],
                "tips": "东门进入离祈年殿最近"
            }
    elif destination == "上海":
        if attraction == "东方明珠" or "东方明珠" in attraction:
            ticket_info = {
                "price": 220,  # 新增
                "adult_price": 220,
                "student_price": 110,
                "notes": "提前在官方小程序或网站购票，学生票110元",  # 新增
                "booking_tips": "提前在官方小程序或网站购票",
                "must_bring": "身份证或订单码",
                "recommended_route": "观光走廊 → 259米透明观光层 → 351米太空舱",
                "key_attractions": ["259米观光廊", "悬空观光廊", "云中漫步"],
                "photo_spots": ["259米观光廊拍陆家嘴", "悬空走廊"],
                "tips": "建议下午去，可以看白天和日落"
            }
        elif attraction == "外滩" or "外滩" in attraction:
            ticket_info = {
                "price": 0,  # 新增
                "adult_price": 0,
                "student_price": 0,
                "notes": "免费开放，全天可游览",  # 新增
                "booking_tips": "免费开放",
                "must_bring": "无需证件",
                "recommended_route": "从南京东路步行至外滩，沿江边漫步至外白渡桥",
                "key_attractions": ["万国建筑博览群", "外白渡桥", "陆家嘴天际线"],
                "photo_spots": ["外滩源", "外白渡桥", "以陆家嘴为背景"],
                "tips": "晚上夜景最美，最佳拍照时间是日落后30分钟"
            }
    elif destination == "西安":
        if attraction == "兵马俑" or "秦始皇兵马俑" in attraction:
            ticket_info = {
                "price": 120,  # 新增
                "adult_price": 120,
                "student_price": 60,
                "notes": "提前在'秦始皇陵博物院'官方公众号预约，学生票60元",  # 新增
                "booking_tips": "提前在'秦始皇陵博物院'官方公众号预约",
                "must_bring": "身份证原件",
                "recommended_route": "一号坑 → 二号坑 → 三号坑 → 铜车马马坑",
                "key_attractions": ["一号坑(规模最大)", "铜车马(精美工艺)", "将军俑(罕见)"],
                "photo_spots": ["一号坑正面全景", "与兵马俑合影"],
                "tips": "一号坑最大最震撼，建议多停留；可以请讲解员更深入了解"
            }
        elif attraction == "大雁塔" or "大雁塔" in attraction:
            ticket_info = {
                "price": 40,  # 新增
                "adult_price": 40,
                "student_price": 20,
                "notes": "现场购票或小程序预约，学生票20元",  # 新增
                "booking_tips": "现场购票或小程序预约",
                "must_bring": "身份证件",
                "recommended_route": "大雁塔北广场 → 大慈恩寺 → 大雁塔顶层",
                "key_attractions": ["大雁塔塔身", "大慈恩寺", "音乐喷泉"],
                "photo_spots": ["大雁塔广场", "塔顶俯瞰西安城"],
                "tips": "晚上有亚洲最大的音乐喷泉表演(免费)"
            }
        elif attraction == "回民街" or "回民街" in attraction:
            ticket_info = {
                "adult_price": 0,
                "student_price": 0,
                "booking_tips": "免费开放",
                "must_bring": "无需证件",
                "recommended_route": "从鼓楼进入，沿主街步行至最深处",
                "key_attractions": ["各种小吃摊", "老字号店铺"],
                "photo_spots": ["鼓楼入口", "热闹的街景"],
                "tips": "必吃：肉夹馍、羊肉泡馍、胡辣汤；建议下午去，晚上更热闹"
            }

    return ticket_info


def _get_pace_by_style(style_type: str) -> str:
    """根据风格类型获取节奏描述"""
    pace_map = {
        "immersive": "慢节奏，深度体验",
        "exploration": "快节奏，高效游览",
        "relaxation": "最慢节奏，轻松休闲",
        "hidden_gem": "中等节奏，发现探索"
    }
    return pace_map.get(style_type, "中等节奏")


def _generate_activity_description_with_llm(
    activity: str,
    location: str,
    time_slot: str,
    weather: Dict[str, Any] = None,
    llm=None
) -> str:
    """使用LLM生成活动的生动描述"""
    if llm:
        try:
            weather_desc = ""
            if weather:
                condition = weather.get("condition", "晴")
                temp = weather.get("temp_day", "25")
                weather_desc = f"当天{condition}，气温约{temp}℃"

            prompt = f"""请用一段生动的话描述这个旅行活动（40-60字）：

活动：{activity}
地点：{location}
时间：{time_slot}
{weather_desc}

要求：
1. 描绘出活动的美好画面
2. 融入当下的氛围感
3. 让人期待这次体验
4. 自然流畅，不要用"推荐"、"建议"等推销语言

请直接输出描述文字："""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            description = response.content.strip()
            if len(description) > 20:
                return description
        except Exception as e:
            logger.warning(f"[活动描述] LLM生成失败: {e}")

    # 默认描述
    if "午餐" in activity or "晚餐" in activity:
        return f"在{location}享用{activity}，品尝当地特色美食，满足味蕾的同时感受当地饮食文化。"
    elif "游览" in activity or "探索" in activity:
        return f"深入探索{location}的独特魅力，发现隐藏的惊喜，留下难忘的旅行记忆。"
    else:
        return f"在{location}{activity}，享受惬意的旅行时光，感受不一样的风景。"


def _generate_weather_info(weather: Dict[str, Any], destination: str) -> Dict[str, Any]:
    """生成天气信息和建议"""
    if not weather:
        return None

    condition = weather.get("condition", "晴")
    temp_day = weather.get("temp_day", weather.get("temp_max", 25))
    temp_night = weather.get("temp_night", weather.get("temp_min", 15))
    weather_icon = _get_weather_icon(condition)
    weather_advice = _get_weather_advice(condition, temp_day)

    # 穿衣建议
    if temp_day >= 30:
        clothing = "建议穿轻薄透气的夏装，携带防晒用品"
    elif temp_day >= 20:
        clothing = "建议穿春秋装，早晚温差大注意添加衣物"
    elif temp_day >= 10:
        clothing = "建议穿外套或毛衣，注意保暖"
    else:
        clothing = "建议穿羽绒服等保暖衣物，注意防寒"

    return {
        "condition": condition,
        "icon": weather_icon,
        "temp_day": temp_day,
        "temp_night": temp_night,
        "advice": weather_advice,
        "clothing": clothing
    }


def _get_weather_icon(condition: str) -> str:
    """获取天气图标"""
    condition_lower = condition.lower()
    if "晴" in condition_lower or "sunny" in condition_lower:
        return "☀️"
    elif "多云" in condition_lower or "cloudy" in condition_lower:
        return "⛅"
    elif "阴" in condition_lower or "overcast" in condition_lower:
        return "☁️"
    elif "雨" in condition_lower or "rain" in condition_lower:
        return "🌧️"
    elif "雪" in condition_lower or "snow" in condition_lower:
        return "❄️"
    else:
        return "🌤️"


def _get_weather_advice(condition: str, temp: int) -> str:
    """获取天气建议"""
    if "雨" in condition:
        return "今天有雨，建议安排室内活动，记得带伞"
    elif temp >= 32:
        return "天气炎热，注意防暑降温，多补充水分"
    elif temp <= 5:
        return "天气寒冷，注意保暖，避免长时间户外活动"
    elif "多云" in condition or "阴" in condition:
        return "天气舒适，适合户外游览"
    else:
        return "天气晴好，是户外活动的好时机"


def _create_daily_schedule(
    day_num: int,
    attractions: List[str],
    style_type: str,
    pace: str,
    date: str,
    weather: Dict[str, Any] = None,
    dining_recommendations: Dict[str, Any] = None
) -> Dict[str, Any]:
    """创建每日详细时间安排

    Args:
        day_num: 天数
        attractions: 景点列表
        style_type: 风格类型
        pace: 节奏
        date: 日期
        weather: 天气信息（可选）
        dining_recommendations: 餐饮推荐数据（可选）
    """

    schedule_items = []

    # 根据风格确定时间段配置
    time_slots = _get_time_slots(style_type)

    # 获取当天的餐饮推荐
    day_dining = {}
    if dining_recommendations:
        daily_dining = dining_recommendations.get("daily_dining", [])
        for dd in daily_dining:
            if dd.get("day") == day_num:
                day_dining = dd
                break

    # 生成天气信息
    weather_info = _generate_weather_info(weather, destination) if weather else None

    # 获取上一活动的位置（用于交通规划）
    prev_location = None

    # 为每个时间段分配活动
    for slot in time_slots:
        if slot["period"] in ["lunch", "dinner"]:
            # 用餐时间 - 使用餐饮推荐数据
            meal_type = slot["period"]  # lunch 或 dinner

            # 尝试获取餐饮推荐
            meal_recommendation = day_dining.get(meal_type) if day_dining else None

            if meal_recommendation and meal_recommendation.get("restaurant_name"):
                # 使用推荐的餐厅
                restaurant_desc = meal_recommendation.get("ai_explanation") or slot["description"]
                # 如果没有LLM描述，生成一个
                if not meal_recommendation.get("ai_explanation"):
                    restaurant_desc = _generate_activity_description_with_llm(
                        f"享用{meal_type}",
                        meal_recommendation.get("restaurant_name", "当地餐厅"),
                        slot["time"],
                        weather,
                        llm
                    )

                schedule_items.append({
                    "period": slot["period"],
                    "time_range": slot["time"],
                    "activity": slot["activity"],
                    "location": meal_recommendation.get("recommended_area", "当地餐厅"),
                    "description": restaurant_desc,
                    "recommendations": {
                        "restaurant": meal_recommendation.get("restaurant_name"),
                        "specialty": meal_recommendation.get("specialty", ""),
                        "signature_dishes": [{"name": meal_recommendation.get("specialty", ""), "price": f"约{meal_recommendation.get('estimated_cost', 80)}元"}],
                        "address": meal_recommendation.get("recommended_area", ""),
                        "average_cost": meal_recommendation.get("estimated_cost", 80)
                    },
                    "estimated_cost": meal_recommendation.get("estimated_cost", 80)
                })
            else:
                # 降级到默认用餐，生成LLM描述
                default_desc = _generate_activity_description_with_llm(
                    slot["activity"],
                    "当地特色餐厅",
                    slot["time"],
                    weather,
                    llm
                )
                schedule_items.append({
                    "period": slot["period"],
                    "time_range": slot["time"],
                    "activity": slot["activity"],
                    "location": "当地特色餐厅",
                    "description": default_desc,
                    "estimated_cost": 80  # 默认用餐费用
                })
        else:
            # 游览时间 - 优先使用景点列表，如果没有则使用默认活动
            if attractions:
                attraction = attractions.pop(0)
                # 获取交通信息
                transport_info = _get_attraction_transport_info(attraction, destination, slot["period"], prev_location)
                # 获取详细门票信息
                ticket_info = _get_attraction_ticket_info(attraction, destination)
                # 生成LLM描述
                llm_desc = _generate_activity_description_with_llm(
                    f"游览{attraction}",
                    attraction,
                    slot["time"],
                    weather,
                    llm
                )
                schedule_items.append({
                    "period": slot["period"],
                    "time_range": slot["time"],
                    "activity": f"游览{attraction}",
                    "location": attraction,
                    "attraction_name": attraction,  # 新增：纯景点名用于图片获取
                    "description": llm_desc,
                    "transport": transport_info,  # 新增交通信息
                    "ticket": ticket_info,  # 使用详细门票信息
                    "tips": _get_visit_tips(style_type, slot["period"])
                })
                # 更新上一位置
                prev_location = attraction
            else:
                # 没有景点时，根据时间段生成默认活动
                default_activity = _get_default_activity(slot["period"], style_type)
                # 生成LLM描述
                llm_desc = _generate_activity_description_with_llm(
                    default_activity["activity"],
                    default_activity["location"],
                    slot["time"],
                    weather,
                    llm
                )
                schedule_items.append({
                    "period": slot["period"],
                    "time_range": slot["time"],
                    "activity": default_activity["activity"],
                    "location": default_activity["location"],
                    "description": llm_desc,
                    "estimated_cost": default_activity.get("cost", 50)
                })

    # 生成每日总结（LLM）
    day_summary = _generate_day_summary(day_num, date, weather_info, schedule_items, destination, llm)

    # 获取住宿建议
    accommodation_info = _get_day_accommodation_recommendation(destination, day_num) if day_num == 1 else None

    return {
        "day": day_num,
        "date": date,
        "title": f"第{day_num}天：{_get_day_title(schedule_items, style_type, day_num)}",
        "schedule": schedule_items,
        "pace": pace,
        "daily_budget": _calculate_daily_budget(schedule_items),
        "weather": weather_info,  # 天气信息
        "day_summary": day_summary,  # 每日总结
        "accommodation": accommodation_info  # 住宿建议（仅第一天）
    }


def _create_daily_schedule_with_agents(
    day_num: int,
    attractions: List[str],
    style_type: str,
    pace: str,
    date: str,
    weather: Dict[str, Any] = None,
    destination: str = "",
    llm=None
) -> Dict[str, Any]:
    """使用智能体和API创建每日时间安排

    Args:
        day_num: 天数
        attractions: 景点列表
        style_type: 风格类型
        pace: 节奏
        date: 日期
        weather: 天气信息
        destination: 目的地城市
        llm: LLM实例

    Returns:
        当天的详细日程
    """
    from .activity_enricher import enrich_activity_with_agent_data
    from .dining_recommender import recommend_dining
    from .accommodation_advisor import recommend_accommodation

    schedule_items = []
    time_slots = _get_time_slots(style_type)
    prev_location = None

    # 生成天气信息
    weather_info = _generate_weather_info(weather, destination) if weather else None

    # 为每个时间段分配活动
    for slot in time_slots:
        if slot["period"] in ["lunch", "dinner"]:
            # 用餐时间 - 使用餐饮推荐智能体
            meal_type = slot["period"]
            meal_recommendations = _get_dining_recommendations_for_meal(
                destination,
                meal_type,
                prev_location or destination,
                llm
            )

            schedule_items.append({
                "period": slot["period"],
                "time_range": slot["time"],
                "activity": slot["activity"],
                "location": meal_recommendations.get("area", "当地餐厅"),
                "description": meal_recommendations.get("description", ""),
                "recommendations": meal_recommendations.get("restaurants", []),
                "estimated_cost": meal_recommendations.get("estimated_cost", 80)
            })
        else:
            # 游览时间 - 使用智能体辅助获取详细信息
            if attractions:
                attraction = attractions.pop(0)

                # 使用智能体模块获取活动详情
                activity_data = enrich_activity_with_agent_data(
                    activity=f"游览{attraction}",
                    location=attraction,
                    destination=destination,
                    period=slot["period"],
                    prev_location=prev_location,
                    llm=llm
                )

                schedule_items.append({
                    "period": slot["period"],
                    "time_range": slot["time"],
                    "activity": f"游览{attraction}",
                    "location": attraction,
                    "attraction_name": attraction,  # 新增：纯景点名用于图片获取
                    "description": activity_data.get("description", ""),
                    "transport": activity_data.get("transport", {}),
                    "ticket": activity_data.get("ticket", {}),
                })

                prev_location = attraction
            else:
                # 没有景点时，生成默认活动
                default_activity = _get_default_activity(slot["period"], style_type)
                schedule_items.append({
                    "period": slot["period"],
                    "time_range": slot["time"],
                    "activity": default_activity["activity"],
                    "location": default_activity["location"],
                    "description": default_activity["description"],
                    "estimated_cost": default_activity.get("cost", 50)
                })

    # 生成每日总结（LLM）
    day_summary = _generate_day_summary(day_num, date, weather_info, schedule_items, destination, llm)

    # 获取住宿建议（仅第一天）
    accommodation_info = None
    if day_num == 1:
        try:
            accom_result = recommend_accommodation(
                destination=destination,
                scheduled_attractions=[{"day": day_num, "schedule": schedule_items}],
                budget_level="medium",
                llm=llm
            )
            accommodation_info = accom_result.get("recommended_area")
        except Exception as e:
            logger.warning(f"[住宿建议] 获取失败: {e}")

    return {
        "day": day_num,
        "date": date,
        "title": f"第{day_num}天：{_get_day_title_from_schedule(schedule_items, style_type, day_num)}",
        "schedule": schedule_items,
        "pace": pace,
        "daily_budget": _calculate_daily_budget(schedule_items),
        "weather": weather_info,
        "day_summary": day_summary,
        "accommodation": accommodation_info
    }


def _get_dining_recommendations_for_meal(
    destination: str,
    meal_type: str,
    location: str,
    llm=None
) -> Dict[str, Any]:
    """获取单次用餐的餐厅推荐"""
    try:
        # 优先使用高德API搜索餐厅
        from tradingagents.integrations.amap_client import AmapClient

        amap = AmapClient()
        search_result = amap.search_restaurants(
            city=destination,
            keyword=f"{meal_type} 餐厅" if meal_type else "餐厅",
            limit=5
        )

        if search_result.get("success") and search_result.get("restaurants"):
            restaurants = search_result["restaurants"][:3]  # 取前3个

            # 使用LLM生成推荐理由
            restaurant_list = []
            for r in restaurants:
                restaurant_list.append({
                    "name": r.get("name", ""),
                    "address": r.get("address", ""),
                    "specialty": "当地特色菜",
                    "avg_cost": 80
                })

            # 生成推荐描述
            description = _generate_dining_description_with_llm(restaurant_list, meal_type, llm)

            return {
                "area": location,
                "description": description,
                "restaurants": restaurant_list,
                "estimated_cost": sum(r["avg_cost"] for r in restaurant_list) // len(restaurant_list)
            }
    except Exception as e:
        logger.warning(f"[餐厅推荐] API调用失败: {e}")

    # 降级：使用LLM直接生成推荐
    if llm:
        try:
            prompt = f"""请为以下情况推荐餐厅（40-60字）：

城市：{destination}
区域：{location}
用餐类型：{meal_type}

要求：
1. 推荐2-3个具体的餐厅名称
2. 简要说明餐厅特色
3. 人均消费范围

请直接输出，格式自然。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            desc = response.content.strip()

            return {
                "area": location,
                "description": desc,
                "restaurants": [{"name": "当地特色餐厅", "specialty": "当地特色菜", "avg_cost": 80}],
                "estimated_cost": 80,
                "data_source": "llm_generated"
            }
        except Exception as e:
            logger.warning(f"[餐厅推荐] LLM生成失败: {e}")

    # 默认推荐
    return {
        "area": location,
        "description": f"在{location}附近享用{meal_type}，品尝当地特色美食",
        "restaurants": [{"name": "当地特色餐厅", "specialty": "当地特色菜", "avg_cost": 80}],
        "estimated_cost": 80
    }


def _generate_dining_description_with_llm(restaurants: List[Dict], meal_type: str, llm) -> str:
    """为餐厅列表生成LLM描述"""
    if not llm or not restaurants:
        return "推荐当地特色餐厅，品尝地道美食"

    try:
        restaurant_names = [r["name"] for r in restaurants[:3]]
        names_str = "、".join(restaurant_names)

        prompt = f"""请用1-2句话介绍为什么推荐这些餐厅（40-60字）：

餐厅：{names_str}
用餐类型：{meal_type}

要求：
1. 突出餐厅特色
2. 说明为什么值得尝试
3. 自然流畅，有吸引力

请直接输出："""

        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content=prompt)])
        description = response.content.strip()

        if len(description) > 15:
            return description
    except Exception as e:
        logger.warning(f"[餐厅描述] LLM生成失败: {e}")

    return f"推荐餐厅包括{names_str}等，品尝当地特色美食，满足味蕾的同时感受当地饮食文化。"


def _get_day_title_from_schedule(schedule_items: List[Dict], style_type: str, day_num: int) -> str:
    """从日程中生成当天标题"""
    # 从活动列表中提取主要景点
    main_attractions = []
    for item in schedule_items:
        activity = item.get("activity", "")
        location = item.get("location", "")
        if "游览" in activity and location and "待定" not in location and "餐厅" not in location:
            main_attractions.append(location)

    if main_attractions:
        main_attraction = main_attractions[0]
        if style_type == "immersive":
            return f"{main_attraction}深度体验"
        elif style_type == "exploration":
            return f"{main_attraction}及周边探索"
        elif style_type == "relaxation":
            return f"悠闲{main_attraction}之旅"
        else:
            return f"{main_attraction}隐秘探索"

    # 没有景点时，根据天数生成不同标题
    day_themes = {
        1: ["抵达探索", "城市初体验"],
        2: ["深度游览", "文化探索"],
        3: ["精华景点", "自然风光"],
        4: ["休闲时光", "自由活动"],
        5: ["收官之旅", "完美告别"]
    }

    style_prefix = {
        "immersive": "慢享",
        "exploration": "高效",
        "relaxation": "悠闲",
        "hidden_gem": "探索"
    }.get(style_type, "精彩")

    themes = day_themes.get(day_num, ["精彩旅程"])
    import random
    theme = random.choice(themes)

    return f"{style_prefix}{theme}"


def _get_time_slots(style_type: str) -> List[Dict[str, Any]]:
    """根据风格类型返回时间段配置"""

    # 沉浸式：上午一个景点，下午一个景点
    if style_type == "immersive":
        return [
            {"period": "morning", "time": "09:00-12:00", "activity": "游览景点", "description": "深度游览，细细品味"},
            {"period": "lunch", "time": "12:00-13:30", "activity": "午餐", "description": "当地特色美食"},
            {"period": "afternoon", "time": "14:00-17:00", "activity": "游览景点", "description": "继续深度游览"},
            {"period": "dinner", "time": "18:00-20:00", "activity": "晚餐", "description": "当地特色餐厅"},
            {"period": "evening", "time": "20:00-21:30", "activity": "自由活动", "description": "探索周边，体验夜生活"}
        ]

    # 探索式：上午两个，下午两个
    elif style_type == "exploration":
        return [
            {"period": "morning", "time": "08:30-12:00", "activity": "游览景点", "description": "高效打卡"},
            {"period": "lunch", "time": "12:00-13:00", "activity": "午餐", "description": "简餐，继续行程"},
            {"period": "afternoon", "time": "13:30-17:30", "activity": "游览景点", "description": "继续探索"},
            {"period": "dinner", "time": "18:00-19:30", "activity": "晚餐", "description": "特色美食"},
            {"period": "evening", "time": "19:30-21:00", "activity": "夜游/打卡", "description": "夜景或特色街区"}
        ]

    # 松弛式：一个景点，大量自由时间
    elif style_type == "relaxation":
        return [
            {"period": "morning", "time": "10:00-12:00", "activity": "游览景点", "description": "睡到自然醒，轻松游览"},
            {"period": "lunch", "time": "12:00-14:00", "activity": "悠闲午餐", "description": "慢慢享用美食"},
            {"period": "afternoon", "time": "15:00-17:00", "activity": "自由活动", "description": "回酒店休息或咖啡厅小坐"},
            {"period": "dinner", "time": "18:30-20:30", "activity": "晚餐", "description": "慢慢品尝美食"},
            {"period": "evening", "time": "21:00-22:00", "activity": "自由活动", "description": "散步或休息"}
        ]

    # 小众宝藏：上午一个，下午一个
    else:  # hidden_gem
        return [
            {"period": "morning", "time": "09:00-12:00", "activity": "探索景点", "description": "发现隐秘景点"},
            {"period": "lunch", "time": "12:00-13:30", "activity": "午餐", "description": "当地特色小馆"},
            {"period": "afternoon", "time": "14:00-17:00", "activity": "探索景点", "description": "继续探索"},
            {"period": "dinner", "time": "18:00-20:00", "activity": "晚餐", "description": "当地人推荐餐厅"},
            {"period": "evening", "time": "20:00-21:30", "activity": "夜游", "description": "发现夜景观光点"}
        ]


def _get_day_accommodation_recommendation(destination: str, day_num: int) -> Dict[str, Any]:
    """获取住宿建议（仅在第一天返回）"""
    try:
        from .accommodation_advisor import DESTINATION_ACCOMMODATION_DB

        accom_db = DESTINATION_ACCOMMODATION_DB.get(destination)
        if not accom_db:
            return None

        areas = accom_db.get("accommodation_areas", [])
        if not areas:
            return None

        # 选择第一个推荐区域（通常是最方便的）
        recommended_area = areas[0]

        return {
            "recommended_area": recommended_area.get("area"),
            "advantages": recommended_area.get("advantages", []),
            "nearby_attractions": recommended_area.get("nearby_attractions", []),
            "hotels": recommended_area.get("recommended_hotels", {}),
            "tips": f"建议住在{recommended_area.get('area')}附近，{', '.join(recommended_area.get('advantages', [])[:3])}"
        }
    except Exception as e:
        logger.warning(f"[住宿建议] 获取失败: {e}")
        return None


def _generate_day_summary(
    day_num: int,
    date: str,
    weather_info: Dict[str, Any],
    schedule_items: List[Dict],
    destination: str,
    llm=None
) -> str:
    """生成每日总结"""
    if not llm:
        # 默认总结
        activities = [item.get("activity", "") for item in schedule_items]
        main_activities = "、".join(activities[:3])
        return f"第{day_num}天的行程包括{main_activities}等活动，期待一次精彩的体验！"

    try:
        # 提取主要活动
        main_activities = []
        for item in schedule_items:
            activity = item.get("activity", "")
            if "游览" in activity or "探索" in activity:
                main_activities.append(activity)
        activities_text = "、".join(main_activities[:2]) if main_activities else "精彩活动"

        # 天气描述
        weather_desc = ""
        if weather_info:
            weather_desc = f"，{weather_info['condition']}天气"

        prompt = f"""请为旅行第{day_num}天写一段简短的总结（80-100字）：

目的地：{destination}
日期：第{day_num}天
主要活动：{activities_text}
天气：{weather_desc if weather_desc else '天气良好'}

要求：
1. 用游记式的语言，描绘当天的期待
2. 突出主要活动的亮点
3. 让人感到兴奋和期待
4. 自然流畅，有画面感
5. 不要用"建议"、"推荐"等推销语言

请直接输出总结文字："""

        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content=prompt)])
        summary = response.content.strip()

        if len(summary) > 30:
            return summary
    except Exception as e:
        logger.warning(f"[每日总结] LLM生成失败: {e}")

    # 默认总结
    return f"第{day_num}天将带您深入探索{destination}的魅力，体验{activities_text}等精彩活动，创造难忘的旅行回忆。"


def _calculate_daily_budget(schedule_items: List[Dict[str, Any]]) -> int:
    """
    计算每日预算

    综合考虑景点门票、餐饮、交通等费用
    """
    total = 0

    for item in schedule_items:
        # 优先使用 estimated_cost
        if "estimated_cost" in item:
            total += item["estimated_cost"]
        # 其次使用 ticket.price
        elif "ticket" in item and isinstance(item["ticket"], dict):
            ticket_price = item["ticket"].get("price", 0)
            total += ticket_price if ticket_price else 50
        # 再次使用 recommendations.average_cost（餐饮）
        elif "recommendations" in item and isinstance(item["recommendations"], dict):
            avg_cost = item["recommendations"].get("average_cost", 0)
            total += avg_cost if avg_cost else 80
        # 最后使用默认值
        else:
            total += 50

    return total


def _get_day_title(schedule_items: List[Dict], style_type: str, day_num: int = 1) -> str:
    """获取当天的标题"""
    # 从活动列表中提取主要景点
    main_attractions = []
    for item in schedule_items:
        activity = item.get("activity", "")
        location = item.get("location", "")
        if "游览" in activity and location and "待定" not in location:
            main_attractions.append(location)

    if main_attractions:
        main_attraction = main_attractions[0]
        if style_type == "immersive":
            return f"{main_attraction}深度体验"
        elif style_type == "exploration":
            return f"{main_attraction}及周边探索"
        elif style_type == "relaxation":
            return f"悠闲{main_attraction}之旅"
        else:
            return f"{main_attraction}隐秘探索"

    # 没有景点时，根据天数和风格生成不同的标题
    day_themes = {
        1: ["抵达探索", "城市初体验", "开启旅程"],
        2: ["深度游览", "文化探索", "当地生活"],
        3: ["精华景点", "自然风光", "历史遗迹"],
        4: ["休闲时光", "自由活动", "特色体验"],
        5: ["收官之旅", "完美告别", "最后探索"]
    }

    style_prefix = {
        "immersive": "慢享",
        "exploration": "高效",
        "relaxation": "悠闲",
        "hidden_gem": "探索"
    }.get(style_type, "精彩")

    # 根据天数选择主题
    themes = day_themes.get(day_num, ["精彩旅程"])
    import random
    theme = random.choice(themes)

    return f"{style_prefix}{theme}"


def _get_default_activity(period: str, style_type: str) -> Dict[str, Any]:
    """获取默认活动（当没有景点时使用）"""
    # 根据时间段和风格返回合适的默认活动
    activities = {
        "morning": {
            "immersive": {
                "activity": "市区漫步探索",
                "location": "市中心/历史街区",
                "description": "睡到自然醒，悠闲漫步在市中心，感受当地生活气息",
                "cost": 30
            },
            "exploration": {
                "activity": "周边景点打卡",
                "location": "附近热门景点",
                "description": "早起出门，高效游览周边热门景点",
                "cost": 50
            },
            "relaxation": {
                "activity": "咖啡厅小坐",
                "location": "当地特色咖啡厅",
                "description": "找一家舒适的咖啡厅，慢慢享受早晨时光",
                "cost": 40
            },
            "hidden_gem": {
                "activity": "小巷探秘",
                "location": "老街小巷",
                "description": "探索不为人知的隐秘角落",
                "cost": 20
            }
        },
        "afternoon": {
            "immersive": {
                "activity": "博物馆/美术馆参观",
                "location": "当地博物馆",
                "description": "深入了解当地文化和艺术",
                "cost": 60
            },
            "exploration": {
                "activity": "景点探索",
                "location": "推荐景点",
                "description": "继续探索当地精华景点",
                "cost": 80
            },
            "relaxation": {
                "activity": "酒店休息/SPA",
                "location": "酒店内",
                "description": "回到酒店休息，享受悠闲时光",
                "cost": 100
            },
            "hidden_gem": {
                "activity": "当地市场逛逛",
                "location": "传统市场",
                "description": "逛逛当地市场，体验地道生活",
                "cost": 50
            }
        },
        "evening": {
            "immersive": {
                "activity": "夜景漫步",
                "location": "城市夜景区",
                "description": "漫步欣赏城市夜景，感受夜晚魅力",
                "cost": 30
            },
            "exploration": {
                "activity": "夜游打卡",
                "location": "热门夜景点",
                "description": "打卡当地热门夜景观赏点",
                "cost": 40
            },
            "relaxation": {
                "activity": "早休息",
                "location": "酒店",
                "description": "早点休息，为明天积蓄精力",
                "cost": 0
            },
            "hidden_gem": {
                "activity": "小酒馆体验",
                "location": "当地小酒馆",
                "description": "体验当地夜生活小酒馆文化",
                "cost": 80
            }
        }
    }

    return activities.get(period, {}).get(style_type, activities["morning"]["immersive"])


def _get_attraction_description(attraction: str, style_type: str) -> str:
    """获取景点描述"""
    descriptions = {
        "immersive": f"深度游览{attraction}，细细品味其文化与历史",
        "exploration": f"打卡{attraction}精华景点，高效游览",
        "relaxation": f"悠闲游览{attraction}，不赶时间",
        "hidden_gem": f"探索{attraction}的独特之处"
    }
    return descriptions.get(style_type, f"游览{attraction}")


def _estimate_ticket_price(attraction: str) -> int:
    """估算门票价格"""
    # 常见景点价格参考
    price_map = {
        "故宫": 60,
        "长城": 45,
        "颐和园": 30,
        "天坛": 15,
        "西湖": 0,
        "灵隐寺": 30,
        "鼓浪屿": 0,
        "外滩": 0,
        "东方明珠": 220,
    }
    return price_map.get(attraction, 50)  # 默认50元


def _get_attraction_tips(attraction: str) -> List[str]:
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


def _get_visit_tips(style_type: str, period: str) -> List[str]:
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


def _generate_attraction_description(
    destination: str,
    scheduled_days: List[Dict[str, Any]],
    style_type: str,
    llm=None
) -> str:
    """
    使用LLM生成景点安排的自然语言描述

    Args:
        destination: 目的地
        scheduled_days: 安排的天数列表
        style_type: 风格类型
        llm: LLM实例

    Returns:
        LLM生成的描述文本
    """
    # 统计景点数量
    total_attractions = 0
    for day in scheduled_days:
        schedule = day.get("schedule", [])
        for item in schedule:
            if item.get("period") not in ["lunch", "dinner"]:
                total_attractions += 1

    # 获取前几天的亮点
    highlights = []
    for day in scheduled_days[:3]:
        title = day.get("title", "")
        if title:
            highlights.append(title)

    # 如果有LLM，使用LLM生成描述
    if llm:
        try:
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
            logger.info(f"[景点排程师] LLM生成描述成功: {len(description)}字")
            return description
        except Exception as e:
            logger.warning(f"[景点排程师] LLM生成描述失败: {e}，使用默认描述")

    # 默认描述（无LLM或LLM失败时）
    style_emoji = {
        "immersive": "🏛️",
        "exploration": "🧭",
        "relaxation": "🌸",
        "hidden_gem": "💎"
    }.get(style_type, "✨")

    highlights_text = '、'.join(highlights[:2]) if highlights else f"{destination}精华景点"

    description = f"""来{destination}，开启一场精彩的{len(scheduled_days)}天旅程！{style_emoji}

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

    return description


# LangGraph 节点函数
def attraction_scheduler_node(state: Dict) -> Dict:
    """景点调度节点（用于LangGraph）"""
    destination = state.get("selected_destination")
    dest_data = state.get("selected_destination_data", {})
    style_proposal = state.get("selected_style_proposal", {})
    days = state.get("days", 5)
    start_date = state.get("start_date", datetime.now().strftime("%Y-%m-%d"))
    llm = state.get("_llm")

    if not destination or not style_proposal:
        logger.error("[景点排程师] 缺少必要数据")
        return state

    # 安排景点
    attraction_result = schedule_attractions(
        destination,
        dest_data,
        style_proposal,
        days,
        start_date,
        llm
    )

    scheduled_attractions = attraction_result.get("scheduled_attractions", [])

    # 更新状态
    from langchain_core.messages import AIMessage
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"景点排程完成: {days}天时间安排",
        name="AttractionScheduler"
    ))

    state["scheduled_attractions"] = scheduled_attractions
    state["messages"] = messages

    return state
