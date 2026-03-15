"""
攻略格式化师 (Agent C5)

职责: 整合所有智能体输出，生成可读性强的详细攻略
输入: 景点安排 + 交通 + 餐饮 + 住宿 + 天气
输出: 格式化完整攻略
"""

from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta

# Import transport enhancer
from .transport_planner import enhance_schedule_with_transport

logger = logging.getLogger('travel_agents')


def _get_weather_for_dates(destination: str, days: int) -> List[Dict]:
    """获取行程日期的天气预报"""
    try:
        from tradingagents.services.travel_data_enrichment import get_enrichment_service

        service = get_enrichment_service()
        result = service.get_detailed_weather(destination, days)

        if result.get("success"):
            return result.get("weather", [])

        logger.warning(f"[攻略格式化师] 天气数据获取失败: {result.get('error', '未知错误')}")
        return []

    except Exception as e:
        logger.error(f"[攻略格式化师] 获取天气数据失败: {e}")
        return []


def format_detailed_guide(
    destination: str,
    style_proposal: Dict[str, Any],
    scheduled_attractions: List[Dict[str, Any]],
    transport_plan: Dict[str, Any],
    dining_plan: Dict[str, Any],
    accommodation_plan: Dict[str, Any],
    user_requirements: Dict[str, Any],
    llm=None
) -> Dict[str, Any]:
    """
    格式化详细攻略

    Args:
        destination: 目的地名称
        style_proposal: 风格方案
        scheduled_attractions: 景点日程安排
        transport_plan: 交通计划
        dining_plan: 餐饮计划
        accommodation_plan: 住宿计划
        user_requirements: 用户需求
        llm: LLM实例（可选）

    Returns:
        完整详细攻略
    """
    logger.info(f"[攻略格式化师] 为{destination}生成详细攻略")

    # 获取天气数据
    weather_data = _get_weather_for_dates(destination, len(scheduled_attractions))

    # 计算总费用
    total_budget = _calculate_total_budget(
        style_proposal,
        transport_plan,
        dining_plan,
        accommodation_plan
    )

    # 整合交通信息到日程安排中
    enhanced_attractions = enhance_schedule_with_transport(
        scheduled_attractions,
        transport_plan
    )

    # 构建每日详细行程
    daily_itineraries = _build_daily_itineraries(
        enhanced_attractions,
        dining_plan,
        accommodation_plan,
        weather_data
    )

    # 生成汇总信息
    summary = _generate_summary(
        destination,
        style_proposal,
        scheduled_attractions,
        transport_plan,
        dining_plan,
        accommodation_plan,
        total_budget
    )

    # 生成打包清单
    packing_list = _generate_packing_list(
        destination,
        user_requirements,
        style_proposal
    )

    # 生成旅行贴士
    tips = _generate_travel_tips(
        destination,
        style_proposal,
        user_requirements
    )

    detailed_guide = {
        "destination": destination,
        "style_type": style_proposal.get("style_type"),
        "style_name": style_proposal.get("style_name"),
        "total_days": len(scheduled_attractions),
        "start_date": user_requirements.get("start_date", datetime.now().strftime("%Y-%m-%d")),

        # 每日详细行程
        "daily_itineraries": daily_itineraries,

        # 汇总信息
        "summary": summary,

        # 预算明细
        "budget_breakdown": {
            "total_budget": total_budget,
            "attractions": _calculate_attraction_cost(scheduled_attractions),
            "transport": transport_plan.get("total_transport_cost", 0),
            "dining": dining_plan.get("estimated_meal_cost", {}).get("per_day", 200) * len(scheduled_attractions),
            "accommodation": accommodation_plan.get("accommodation_cost", {}).get("total_cost", 0)
        },

        # 打包清单和贴士
        "packing_list": packing_list,
        "travel_tips": tips,

        # 元数据
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "v3.0"
    }

    logger.info(f"[攻略格式化师] 完成{len(daily_itineraries)}天详细攻略")

    return detailed_guide


def _calculate_total_budget(
    style_proposal: Dict,
    transport_plan: Dict,
    dining_plan: Dict,
    accommodation_plan: Dict
) -> int:
    """计算总预算"""

    # 基础费用（来自风格方案）
    base_cost = style_proposal.get("estimated_cost", 0)

    # 交通费用
    transport_cost = transport_plan.get("total_transport_cost", 0)

    # 住宿费用
    accommodation_cost = accommodation_plan.get("accommodation_cost", {}).get("total_cost", 0)

    # 餐饮费用
    meal_cost = dining_plan.get("estimated_meal_cost", {}).get("per_day", 200)
    days = len(transport_plan.get("daily_transport", []))
    dining_cost = meal_cost * days if days > 0 else 0

    return base_cost + transport_cost + accommodation_cost + dining_cost


def _calculate_attraction_cost(scheduled_attractions: List[Dict]) -> int:
    """计算门票费用"""
    total = 0
    for day in scheduled_attractions:
        for item in day.get("schedule", []):
            ticket = item.get("ticket", {})
            if isinstance(ticket, dict):
                total += ticket.get("price", 0)
    return total


def _build_daily_itineraries(
    scheduled_attractions: List[Dict[str, Any]],
    dining_plan: Dict[str, Any],
    accommodation_plan: Dict[str, Any],
    weather_data: List[Dict] = None
) -> List[Dict[str, Any]]:
    """构建每日详细行程"""

    daily_itineraries = []
    daily_dining = dining_plan.get("daily_dining", [])

    for i, day_schedule in enumerate(scheduled_attractions):
        day_num = day_schedule.get("day", i + 1)
        date = day_schedule.get("date", "")
        schedule_items = day_schedule.get("schedule", [])

        # 获取当天天气
        day_weather = None
        if weather_data and i < len(weather_data):
            day_weather = weather_data[i]

        # 获取当天的餐饮信息
        day_dining = None
        if i < len(daily_dining):
            day_dining = daily_dining[i]

        # 整合餐饮信息到行程中，增强餐厅详细信息
        enhanced_schedule = []
        for item in schedule_items:
            enhanced_item = item.copy()

            # 添加餐饮推荐（包含详细餐厅信息）
            if item.get("period") == "lunch" and day_dining:
                lunch = day_dining.get("lunch")
                enhanced_item["dining"] = _enrich_dining_info(lunch)
            elif item.get("period") == "dinner" and day_dining:
                dinner = day_dining.get("dinner")
                enhanced_item["dining"] = _enrich_dining_info(dinner)

            enhanced_schedule.append(enhanced_item)

        # 构建每日行程
        daily_itinerary = {
            "day": day_num,
            "date": date,
            "title": day_schedule.get("title"),
            "schedule": enhanced_schedule,
            "pace": day_schedule.get("pace"),
            "weather": day_weather,
            "daily_budget": _estimate_daily_budget(enhanced_schedule, day_dining),
            "accommodation": _extract_accommodation_info(accommodation_plan)
        }

        daily_itineraries.append(daily_itinerary)

    return daily_itineraries


def _enrich_dining_info(dining: Dict) -> Dict:
    """增强餐饮信息，确保包含详细的餐厅信息"""
    if not dining:
        return dining

    # 确保有推荐餐厅
    restaurant = dining.get("recommended_restaurant")
    if restaurant:
        # 如果是真实API数据，已经包含详细信息
        if isinstance(restaurant, dict) and restaurant.get("address"):
            return dining

        # 如果是静态数据，增强显示
        dining["restaurant_details"] = {
            "name": restaurant.get("name", "待定餐厅"),
            "address": restaurant.get("area", "具体地址待查询"),
            "phone": restaurant.get("phone", "待查询"),
            "specialty": restaurant.get("specialty", ""),
            "price": restaurant.get("price", ""),
            "note": "建议提前电话确认营业时间和是否需要预订"
        }

    return dining


def _estimate_daily_budget(schedule: List[Dict], dining: Dict) -> int:
    """估算每日预算"""
    budget = 0

    # 门票费用
    for item in schedule:
        ticket = item.get("ticket", {})
        if isinstance(ticket, dict):
            budget += ticket.get("price", 0)

        # 交通费用
        transport = item.get("transport", {})
        if isinstance(transport, dict):
            budget += transport.get("cost", 0)

    # 餐饮费用
    if dining:
        lunch = dining.get("lunch", {})
        dinner = dining.get("dinner", {})
        budget += lunch.get("estimated_cost", 80)
        budget += dinner.get("estimated_cost", 120)

    return budget


def _extract_accommodation_info(accommodation_plan: Dict) -> Dict[str, str]:
    """
    安全提取住宿信息

    处理recommended_area可能是字符串或字典的情况
    """
    if not accommodation_plan:
        return {"area": "待定", "description": ""}

    recommended_area = accommodation_plan.get("recommended_area")

    # 如果是字符串，直接作为area
    if isinstance(recommended_area, str):
        return {
            "area": recommended_area,
            "description": ""
        }

    # 如果是字典，提取信息
    if isinstance(recommended_area, dict):
        return {
            "area": recommended_area.get("area", "待定"),
            "description": recommended_area.get("reason", "")
        }

    # 默认值
    return {"area": "待定", "description": ""}


def _generate_summary(
    destination: str,
    style_proposal: Dict,
    scheduled_attractions: List[Dict],
    transport_plan: Dict,
    dining_plan: Dict,
    accommodation_plan: Dict,
    total_budget: int
) -> Dict[str, Any]:
    """生成汇总信息"""

    # 统计景点总数
    total_attractions = 0
    for day in scheduled_attractions:
        for item in day.get("schedule", []):
            if item.get("period") not in ["lunch", "dinner"]:
                total_attractions += 1

    # 获取特色菜
    special_dishes = []
    if dining_plan:
        dishes = dining_plan.get("special_dishes", {})
        special_dishes = (
            dishes.get("dinner", [])[:3] +
            dishes.get("snacks", [])[:2]
        )

    return {
        "destination": destination,
        "style": style_proposal.get("style_name"),
        "total_days": len(scheduled_attractions),
        "total_attractions": total_attractions,
        "total_budget": total_budget,
        "budget_per_day": total_budget // len(scheduled_attractions) if scheduled_attractions else 0,
        "special_dishes": special_dishes,
        "accommodation_area": _extract_accommodation_info(accommodation_plan).get("area", ""),
        "transport_method": _get_main_transport_method(transport_plan)
    }


def _get_main_transport_method(transport_plan: Dict) -> str:
    """获取主要交通方式"""
    recommendations = transport_plan.get("transport_recommendations", [])
    if recommendations:
        return recommendations[0]
    return "地铁/公交"


def _generate_packing_list(
    destination: str,
    user_requirements: Dict,
    style_proposal: Dict
) -> List[str]:
    """生成打包清单"""

    style_type = style_proposal.get("style_type", "immersive")
    base_list = []

    # 通用物品
    base_list.extend([
        "身份证/护照",
        "手机、充电器、充电宝",
        "现金和银行卡",
        "换洗衣物（根据天数准备）",
        "洗漱用品（小瓶装）",
        "常用药品（感冒药、肠胃药等）",
        "防晒用品（防晒霜、帽子、墨镜）"
    ])

    # 根据风格添加
    if style_type == "exploration":
        base_list.extend([
            "舒适运动鞋（必备！）",
            "双肩包",
            "水壶",
            "纸巾/湿巾"
        ])
    elif style_type == "relaxation":
        base_list.extend([
            "休闲衣物",
            "舒适的拖鞋",
            "书籍/Kindle",
            "防晒伞"
        ])
    elif style_type == "hidden_gem":
        base_list.extend([
            "相机（记录发现）",
            "手电筒（探索暗处）",
            "防蚊液"
        ])

    # 根据目的地添加
    if destination in ["北京", "西安", "成都"]:
        base_list.append("舒适的步行鞋（古迹多，需要多走）")

    # 根据季节添加（简化版）
    month = datetime.now().month
    if month in [12, 1, 2]:  # 冬季
        base_list.extend(["保暖外套", "围巾", "手套"])
    elif month in [6, 7, 8]:  # 夏季
        base_list.extend(["雨具", "防蚊液", "消暑药品"])

    return base_list


def _generate_travel_tips(
    destination: str,
    style_proposal: Dict,
    user_requirements: Dict
) -> List[str]:
    """生成旅行贴士"""

    tips = []
    style_type = style_proposal.get("style_type", "immersive")

    # 通用贴士
    tips.extend([
        "提前查看天气预报，准备相应衣物",
        "下载离线地图，以防没网",
        "提前了解当地文化和习俗",
        "保持手机电量，携带充电宝"
    ])

    # 根据风格的贴士
    if style_type == "immersive":
        tips.extend([
            "放慢节奏，不要赶时间",
            "多与当地人交流，了解真实生活",
            "尝试当地特色美食，哪怕看起来奇怪"
        ])
    elif style_type == "exploration":
        tips.extend([
            "提前规划好路线，节省时间",
            "注意体力分配，不要过度疲劳",
            "热门景点早起或晚去，避开人流"
        ])
    elif style_type == "relaxation":
        tips.extend([
            "不要把行程排太满",
            "累了就休息，不要勉强",
            "找个喜欢的咖啡厅发呆也是旅行"
        ])
    elif style_type == "hidden_gem":
        tips.extend([
            "保持好奇心，随时准备发现惊喜",
            "不要害怕走小路",
            "拍照记录独特之处"
        ])

    # 根据目的地的贴士
    if destination == "北京":
        tips.extend([
            "故宫周一闭馆，注意安排",
            "长城建议坐缆车上下，节省体力",
            "北京地铁发达，建议下载相关APP"
        ])
    elif destination == "上海":
        tips.extend([
            "外滩、南京路人多，注意保管财物",
            "上海夏天很热，注意防暑",
            "本帮菜偏甜，点菜可提前说明"
        ])
    elif destination == "成都":
        tips.extend([
            "川菜辣度可要求调整，不一定要吃特辣",
            "火锅底料可选微辣或鸳鸯锅",
            "成都生活节奏慢，享受悠闲时光"
        ])

    return tips


def format_guide_as_text(detailed_guide: Dict[str, Any]) -> str:
    """将攻略格式化为文本（用于导出或显示）"""

    lines = []
    lines.append("=" * 60)
    lines.append(f"  {detailed_guide['destination']} {detailed_guide['style_name']}旅行攻略")
    lines.append("=" * 60)
    lines.append(f"  行程天数: {detailed_guide['total_days']}天")
    lines.append(f"  出发日期: {detailed_guide['start_date']}")
    lines.append(f"  总预算: ¥{detailed_guide['budget_breakdown']['total_budget']}")
    lines.append("")

    # 每日行程
    for day in detailed_guide['daily_itineraries']:
        lines.append("-" * 60)
        lines.append(f"  📅 {day['title']}")

        # 添加天气信息
        if day.get('weather'):
            weather = day['weather']
            lines.append(f"  🌤️ 天气: {weather.get('weather', '未知')} {weather.get('temperature', '')}")
            if weather.get('wind'):
                lines.append(f"     {weather.get('wind', '')}")

        lines.append("-" * 60)

        for item in day['schedule']:
            period_emoji = {
                "morning": "☀️",
                "lunch": "🍜",
                "afternoon": "🌤️",
                "dinner": "🍽️",
                "evening": "🌙"
            }
            emoji = period_emoji.get(item['period'], "📍")

            lines.append(f"\n  {emoji} {item['time_range']} - {item['activity']}")
            lines.append(f"     📍 {item.get('location', '')}")

            if item.get('description'):
                lines.append(f"     📝 {item['description']}")

            if item.get('ticket'):
                ticket = item['ticket']
                lines.append(f"     🎫 门票: ¥{ticket.get('price', 0)}")

            if item.get('transport'):
                transport = item['transport']
                lines.append(f"     🚇 交通: {transport['method']} ({transport['duration']})")

            if item.get('dining'):
                dining = item['dining']
                restaurant = dining.get('recommended_restaurant')

                lines.append(f"     🍴 餐饮: {dining.get('recommended_area', '')}")

                # 详细餐厅信息
                if restaurant:
                    if isinstance(restaurant, dict):
                        lines.append(f"     📍 推荐餐厅: {restaurant.get('name', '待定')}")
                        if restaurant.get('address'):
                            lines.append(f"        地址: {restaurant['address']}")
                        if restaurant.get('phone'):
                            lines.append(f"        电话: {restaurant['phone']}")
                        if restaurant.get('cost_range'):
                            lines.append(f"        人均: {restaurant['cost_range']}")
                        if restaurant.get('specialties'):
                            specialties = ', '.join(restaurant['specialties'][:3])
                            lines.append(f"        特色: {specialties}")

                if dining.get('special_dishes'):
                    dishes = ', '.join(dining['special_dishes'][:3])
                    lines.append(f"     🍽️ 推荐菜品: {dishes}")

        lines.append(f"\n  🏨 住宿: {day['accommodation']['area']}")
        lines.append(f"  💰 当日预算: ¥{day['daily_budget']}")

    # 汇总信息
    lines.append("\n" + "=" * 60)
    lines.append("  📊 行程汇总")
    lines.append("=" * 60)
    summary = detailed_guide['summary']
    lines.append(f"  总景点数: {summary['total_attractions']}个")
    lines.append(f"  人均预算: ¥{summary['budget_per_day']}/天")
    lines.append(f"  住宿区域: {summary['accommodation_area']}")

    # 贴士
    lines.append("\n" + "=" * 60)
    lines.append("  💡 旅行贴士")
    lines.append("=" * 60)
    for tip in detailed_guide['travel_tips'][:10]:
        lines.append(f"  • {tip}")

    # 打包清单
    lines.append("\n" + "=" * 60)
    lines.append("  🎒 打包清单")
    lines.append("=" * 60)
    for item in detailed_guide['packing_list']:
        lines.append(f"  ☐ {item}")

    lines.append("\n" + "=" * 60)
    lines.append(f"  生成时间: {detailed_guide['generated_at']}")
    lines.append("=" * 60)

    return '\n'.join(lines)


# LangGraph 节点函数
def guide_formatter_node(state: Dict) -> Dict:
    """攻略格式化节点（用于LangGraph）"""
    destination = state.get("selected_destination")
    style_proposal = state.get("selected_style_proposal", {})
    scheduled_attractions = state.get("scheduled_attractions", [])
    transport_plan = state.get("transport_plan", {})
    dining_plan = state.get("dining_plan", {})
    accommodation_plan = state.get("accommodation_plan", {})
    user_requirements = state.get("user_requirements", {})
    llm = state.get("_llm")

    if not destination or not scheduled_attractions:
        logger.error("[攻略格式化师] 缺少必要数据")
        return state

    # 格式化攻略
    detailed_guide = format_detailed_guide(
        destination,
        style_proposal,
        scheduled_attractions,
        transport_plan,
        dining_plan,
        accommodation_plan,
        user_requirements,
        llm
    )

    # 同时生成文本版本
    guide_text = format_guide_as_text(detailed_guide)

    # 更新状态
    from langchain_core.messages import AIMessage
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"详细攻略生成完成: {len(scheduled_attractions)}天完整行程",
        name="GuideFormatter"
    ))

    state["detailed_guide"] = detailed_guide
    state["guide_text"] = guide_text
    state["messages"] = messages

    return state
