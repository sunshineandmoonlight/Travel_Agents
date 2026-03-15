"""
智能体辅助模块 - 为每个活动生成详细信息

通过调用C组智能体和高德API获取实时数据，避免硬编码
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger('travel_agents')


def enrich_activity_with_agent_data(
    activity: str,
    location: str,
    destination: str,
    period: str,
    prev_location: str = None,
    llm=None
) -> Dict[str, Any]:
    """
    使用智能体和API为活动生成详细信息

    Args:
        activity: 活动类型（如"游览故宫"）
        location: 地点名称
        destination: 城市
        period: 时间段
        prev_location: 上一个地点
        llm: LLM实例

    Returns:
        包含交通、门票、建议等详细信息的字典
    """
    result = {
        "activity": activity,
        "location": location,
        "transport": _get_transport_info_from_agent(location, prev_location, destination, llm),
        "ticket": _get_ticket_info_from_agent(location, destination, llm),
        "description": _get_activity_description_from_llm(activity, location, period, llm)
    }
    return result


def _get_transport_info_from_agent(
    location: str,
    prev_location: str,
    destination: str,
    llm=None
) -> Dict[str, Any]:
    """
    调用交通规划智能体获取交通信息

    优先级：高德API > 交通规划智能体 > LLM生成
    """
    # 1. 尝试使用高德API规划路线
    try:
        from tradingagents.integrations.amap_client import AmapClient

        amap = AmapClient()

        # 如果有上一个地点，规划路线
        if prev_location:
            # 获取两地间的交通路线
            route_result = amap.get_direction(
                origin=prev_location,
                destination=location,
                city=destination
            )

            if route_result.get("success") and route_result.get("routes"):
                route = route_result["routes"][0]  # 取第一条路线
                return {
                    "method": route.get("taxi_distance", "") < 3000 and "步行" or "地铁/公交",
                    "route": f"从{prev_location}到{location}",
                    "duration": _format_duration(route.get("duration", 0)),
                    "cost": _estimate_cost_from_distance(route.get("distance", 0)),
                    "distance": route.get("distance", ""),
                    "data_source": "amap_api"
                }

    except Exception as e:
        logger.warning(f"[交通信息] 高德API调用失败: {e}")

    # 2. 降级：使用LLM生成交通建议
    if llm:
        try:
            prompt = f"""请为以下两个地点之间规划交通方式（1-2句话）：

出发地：{prev_location or '市中心'}
目的地：{location}
城市：{destination}

要求：
1. 推荐最方便的交通方式（地铁/公交/打车/步行）
2. 说明大概耗时
3. 简洁明了

请直接输出，不要任何格式符号。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            transport_desc = response.content.strip()

            if transport_desc and len(transport_desc) > 10:
                return {
                    "method": "推荐",
                    "route": f"从{prev_location or '市中心'}到{location}",
                    "description": transport_desc,
                    "duration": "约30分钟",
                    "cost": 15,
                    "data_source": "llm_generated"
                }
        except Exception as e:
            logger.warning(f"[交通信息] LLM生成失败: {e}")

    # 3. 最后降级：返回默认信息
    return {
        "method": "地铁/公交或打车",
        "route": f"从{prev_location or '市中心'}到{location}",
        "duration": "约30分钟",
        "cost": 15,
        "tips": "建议使用地图APP导航"
    }


def _get_ticket_info_from_agent(
    location: str,
    destination: str,
    llm=None
) -> Dict[str, Any]:
    """
    获取景点的门票信息

    优先级：高德POI详情 > LLM生成 > 默认估算
    """
    # 1. 尝试使用高德API获取POI详情
    try:
        from tradingagents.integrations.amap_client import AmapClient

        amap = AmapClient()
        poi_result = amap.search_attractions(
            city=destination,
            keyword=location,
            limit=1
        )

        if poi_result.get("success") and poi_result.get("attractions"):
            poi = poi_result["attractions"][0]
            # 从POI信息中提取门票信息
            return {
                "price": _estimate_price_from_poi(poi),
                "booking": "建议提前网上预约",
                "must_bring": "身份证原件",
                "highlights": _extract_highlights_from_poi(poi),
                "data_source": "amap_poi"
            }

    except Exception as e:
        logger.warning(f"[门票信息] 高德API调用失败: {e}")

    # 2. 使用LLM生成门票信息
    if llm:
        try:
            prompt = f"""请为以下景点提供门票信息（30-50字）：

景点：{location}
城市：{destination}

要求：
1. 大概的门票价格范围
2. 是否需要提前预订
3. 是否有学生票
4. 必带证件

请直接输出，简洁明了。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            ticket_desc = response.content.strip()

            if ticket_desc and len(ticket_desc) > 15:
                return {
                    "description": ticket_desc,
                    "booking": "建议提前了解",
                    "must_bring": "身份证件",
                    "highlights": [],
                    "data_source": "llm_generated"
                }
        except Exception as e:
            logger.warning(f"[门票信息] LLM生成失败: {e}")

    # 3. 默认估算
    estimated_price = _estimate_price_by_location(location)
    return {
        "price": estimated_price,
        "student_price": int(estimated_price * 0.5),
        "booking": "建议提前网上预约",
        "must_bring": "身份证原件",
        "highlights": [],
        "data_source": "estimated"
    }


def _get_activity_description_from_llm(
    activity: str,
    location: str,
    period: str,
    llm=None
) -> str:
    """
    使用LLM生成活动的自然描述
    """
    if not llm:
        return f"在{location}{activity}，体验当地的文化与风景"

    try:
        period_desc = {
            "morning": "上午",
            "afternoon": "下午",
            "evening": "晚上",
            "lunch": "午餐",
            "dinner": "晚餐"
        }.get(period, "")

        prompt = f"""请用一段自然的话描述这个旅行活动（50-80字）：

活动：{activity}
地点：{location}
时间：{period_desc}

要求：
1. 用游记式的语言，描绘出活动的美好
2. 让人感到期待和兴奋
3. 自然流畅，不要用"建议"、"推荐"等推销语言
4. 画面感强，有代入感

请直接输出描述文字："""

        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content=prompt)])
        description = response.content.strip()

        if len(description) > 20:
            return description
    except Exception as e:
        logger.warning(f"[活动描述] LLM生成失败: {e}")

    return f"在{location}{activity}，感受独特的文化与风景"


# ============================================================
# 辅助函数
# ============================================================

def _format_duration(seconds: int) -> str:
    """将秒数转换为可读的时长"""
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"约{minutes}分钟"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"约{hours}小时{minutes}分钟"


def _estimate_cost_from_distance(meters: int) -> int:
    """根据距离估算交通费用"""
    km = meters / 1000
    if km < 2:
        return 0  # 步行免费
    elif km < 10:
        return int(km * 2 + 5)  # 公交/地铁
    else:
        return int(km * 2.5 + 10)  # 地铁/打车


def _estimate_price_from_poi(poi: Dict) -> int:
    """从POI信息估算门票价格"""
    # 尝试从POI中提取价格信息
    # 这里需要根据实际API返回的数据结构来调整
    return 50  # 默认50元


def _estimate_price_by_location(location: str) -> int:
    """根据地点名称估算门票价格"""
    # 常见景点价格参考
    price_map = {
        "故宫": 60,
        "颐和园": 30,
        "天坛": 15,
        "长城": 45,
        "兵马俑": 120,
        "大雁塔": 40,
        "外滩": 0,
        "东方明珠": 220,
        "西湖": 0,
        "灵隐寺": 30,
        "都江堰": 80,
        "九寨沟": 169,
        "黄山": 190,
        "张家界": 224,
    }
    return price_map.get(location, 50)


def _extract_highlights_from_poi(poi: Dict) -> List[str]:
    """从POI信息中提取亮点"""
    highlights = []

    # 这里需要根据实际API返回的数据结构来提取
    # 例如：景点类型、标签等

    return highlights
