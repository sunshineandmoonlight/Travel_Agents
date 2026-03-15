"""
松弛式方案设计师 (Agent B3)

设计理念: 休闲为主，轻松节奏，主打放松

特点:
- 每日1-2个景点
- 大量留白时间
- 不赶时间，累了就休息
- 适合度假为主、拒绝赶路的旅行者
- 使用SerpAPI和OpenTripMap获取实时数据
- 使用LLM生成个性化描述
"""

from typing import Dict, Any, List
import logging
import asyncio
import os

logger = logging.getLogger('travel_agents')

# 导入API工具
from .api_tools.serpapi_tool import SerpAPITool
from .api_tools.opentripmap_tool import OpenTripMapTool


def _get_relaxing_attractions(destination: str, days: int) -> List[Dict[str, Any]]:
    """
    使用新的API工具获取适合放松的景点数据

    松弛式关注公园、海滩、咖啡厅等休闲场所

    Args:
        destination: 目的地名称
        days: 天数

    Returns:
        景点列表
    """
    all_attractions = []

    # 优先使用SerpAPI搜索休闲景点
    if os.getenv("SERPAPI_KEY") and os.getenv("SERPAPI_KEY") != "your_serpapi_key_here":
        try:
            serpapi_tool = SerpAPITool()

            # 搜索适合放松的景点
            relax_keywords = ["公园", "海滩", "湖", "温泉", "咖啡", "广场", "步行街"]

            for keywords in relax_keywords[:3]:  # 限制搜索次数
                serp_results = asyncio.run(serpapi_tool.search_attractions(
                    destination=destination,
                    keywords=keywords,
                    days=days,
                    style="relaxation"
                ))

                if serp_results:
                    all_attractions.extend(serp_results)

            # 去重
            seen_names = set()
            unique_attractions = []
            for attr in all_attractions:
                name = attr.get("name", "")
                if name and name not in seen_names:
                    seen_names.add(name)
                    unique_attractions.append(attr)

            if unique_attractions:
                logger.info(f"[松弛式设计师] SerpAPI搜索到 {len(unique_attractions)} 个休闲景点")
                return unique_attractions[:days * 2]  # 每天最多2个

        except Exception as e:
            logger.warning(f"[松弛式设计师] SerpAPI搜索失败: {e}")

    # 补充OpenTripMap数据
    if len(all_attractions) < days * 2 and os.getenv("OPENTRIPMAP_API_KEY") and os.getenv("OPENTRIPMAP_API_KEY") != "your_opentripmap_key_here":
        try:
            opentripmap_tool = OpenTripMapTool()
            otm_results = asyncio.run(opentripmap_tool.search_attractions(
                destination=destination,
                keywords="parks",
                days=days,
                style="relaxation"
            ))

            if otm_results:
                # 去重
                existing_names = {a.get("name", "") for a in all_attractions}
                for otm_attr in otm_results:
                    if otm_attr.get("name", "") not in existing_names:
                        all_attractions.append(otm_attr)

                logger.info(f"[松弛式设计师] OpenTripMap补充 {len(otm_results)} 个景点")
        except Exception as e:
            logger.warning(f"[松弛式设计师] OpenTripMap搜索失败: {e}")

    if all_attractions:
        logger.info(f"[松弛式设计师] 总共获取 {len(all_attractions)} 个实时景点")
        # 返回前 days*2 个
        seen_names = set()
        unique_attractions = []
        for attr in all_attractions:
            name = attr.get("name", "")
            if name and name not in seen_names:
                seen_names.add(name)
                unique_attractions.append(attr)
                if len(unique_attractions) >= days * 2:
                    break
        return unique_attractions
    else:
        logger.warning("[松弛式设计师] 未获取到实时景点数据")
        return []


def design_relaxation_style(
    destination: str,
    dest_data: Dict[str, Any],
    user_portrait: Dict[str, Any],
    days: int,
    llm=None
) -> Dict[str, Any]:
    """
    设计松弛式旅行方案

    优先调用工具API获取实时景点数据，失败时使用数据库数据

    Args:
        destination: 目的地名称
        dest_data: 目的地数据
        user_portrait: 用户画像
        days: 旅行天数
        llm: LLM实例（可选）

    Returns:
        松弛式风格方案
    """
    logger.info(f"[松弛式设计师] 为{destination}设计{days}天松弛式方案")

    tags = dest_data.get("tags", [])
    user_interests = user_portrait.get("primary_interests", [])

    # 1. 优先调用工具API获取实时休闲景点
    real_attractions = []
    data_source = "fallback"

    try:
        all_attractions = _get_relaxing_attractions(destination, days)

        if all_attractions and len(all_attractions) > 0:
            real_attractions = all_attractions
            data_source = "realtime_api"
            logger.info(f"[松弛式设计师] 使用实时API数据: {len(real_attractions)}个景点")
    except Exception as e:
        logger.warning(f"[松弛式设计师] 实时数据获取失败: {e}")

    # 2. 降级：使用数据库highlights
    if not real_attractions:
        logger.info(f"[松弛式设计师] 使用数据库highlights")
        highlights = dest_data.get("highlights", [])
        real_attractions = [{"name": h, "type": "景点", "location": {}} for h in highlights]
        data_source = "fallback"

    # 3. 每天只安排1-2个景点，大量留白
    daily_itinerary = []
    attractions_per_day = max(1, len(real_attractions) // days)

    for day in range(1, days + 1):
        start_idx = (day - 1) * attractions_per_day
        end_idx = min(start_idx + attractions_per_day + 1, len(real_attractions))
        day_attractions_data = real_attractions[start_idx:end_idx]
        day_attractions = [a.get("name", a) for a in day_attractions_data]

        # 生成活动安排（轻松节奏）
        activities = []

        # 只安排一个主要景点
        if day_attractions:
            activities.append({
                "time": "上午晚些时候",
                "activity": f"悠闲游览{day_attractions[0]}",
                "description": "睡到自然醒，不赶时间",
                "attraction_id": day_attractions[0]
            })

        # 下午留白
        if "自然" in str(tags) or "海滨" in str(tags):
            activities.append({
                "time": "下午",
                "activity": "自由活动时间",
                "description": "找个咖啡厅发呆，或公园散步"
            })
        elif "购物" in str(tags):
            activities.append({
                "time": "下午",
                "activity": "逛街购物",
                "description": "随意逛逛，看到喜欢的就买"
            })
        else:
            activities.append({
                "time": "下午",
                "activity": "午休时间",
                "description": "回酒店休息，或找个地方发呆"
            })

        # 晚上安排
        if "美食" in str(tags):
            activities.append({
                "time": "晚上",
                "activity": "美食探索",
                "description": "慢慢找家好吃的餐厅"
            })
        else:
            activities.append({
                "time": "晚上",
                "activity": "自由活动",
                "description": "看心情决定去哪里"
            })

        daily_itinerary.append({
            "day": day,
            "title": f"第{day}天：{'悠闲' if day_attractions else '自由'}探索{destination}",
            "activities": activities,
            "attractions": day_attractions,
            "pace": "最慢节奏"
        })

    # 生成亮点
    highlights_desc = [
        "休闲为主，轻松节奏",
        "大量留白时间",
        "不赶时间，累了就休息"
    ]

    if "海滨" in tags or "温泉" in tags:
        highlights_desc.append("度假村酒店享受")

    if "美食" in tags:
        highlights_desc.append("悠闲品味美食")

    # 计算费用（松弛式通常较低，因为不赶景点）
    budget = dest_data.get("budget_level", {}).get("economy", 300)
    total_budget = budget * days * user_portrait.get("total_travelers", 2)

    # 获取实际使用的景点名称
    used_attractions = []
    for day_plan in daily_itinerary:
        used_attractions.extend(day_plan.get("attractions", []))

    # 跟踪API来源
    api_sources_used = []
    if data_source == "realtime_api":
        if os.getenv("SERPAPI_KEY") and os.getenv("SERPAPI_KEY") != "your_serpapi_key_here":
            api_sources_used.append("serpapi")
        if os.getenv("OPENTRIPMAP_API_KEY") and os.getenv("OPENTRIPMAP_API_KEY") != "your_opentripmap_key_here":
            api_sources_used.append("opentripmap")

    # 使用LLM生成方案描述
    llm_description = _generate_llm_description(
        destination,
        days,
        used_attractions[:5] if len(used_attractions) > 5 else used_attractions,
        user_portrait,
        llm
    )

    return {
        "style_name": "松弛式",
        "style_icon": "🌿",
        "style_type": "relaxation",
        "style_description": "休闲为主，轻松节奏，主打放松",
        "daily_pace": "最慢节奏，每日1-2个景点，大量自由时间",
        "intensity_level": 1,
        "preview_itinerary": [
            {"day": 1, "title": f"{destination}轻松抵达", "attractions": used_attractions[:1]},
            {"day": 2, "title": "悠闲探索", "attractions": used_attractions[1:3] if len(used_attractions) > 1 else used_attractions}
        ],
        "estimated_cost": total_budget,
        "best_for": "度假为主，拒绝赶路的旅行者",
        "highlights": highlights_desc[:5],
        "daily_itinerary": daily_itinerary,
        "data_source": data_source,
        "api_sources_used": api_sources_used,
        "llm_description": llm_description,
        "agent_info": {
            "name_cn": "松弛式设计师",
            "name_en": "RelaxationDesigner",
            "icon": "🌿",
            "group": "B",
            "llm_enabled": llm is not None
        }
    }


def relaxation_designer_node(state: Dict) -> Dict:
    """松弛式设计师节点（用于LangGraph）"""
    destination = state.get("selected_destination")
    dest_data = state.get("selected_destination_data", {})
    user_portrait = state.get("user_portrait")
    days = state.get("days", 5)
    llm = state.get("_llm")

    if not destination or not user_portrait:
        logger.error("[松弛式设计师] 缺少必要数据")
        return state

    # 设计方案
    proposal = design_relaxation_style(destination, dest_data, user_portrait, days, llm)

    # 更新状态
    from langchain_core.messages import AIMessage
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"松弛式方案设计完成: {days}天轻松度假",
        name="RelaxationDesigner"
    ))

    if "style_proposals" not in state:
        state["style_proposals"] = []
    state["style_proposals"].append(proposal)
    state["messages"] = messages

    return state


def create_relaxation_proposal(
    destination: str,
    dest_data: Dict[str, Any],
    user_portrait: Dict[str, Any],
    days: int,
    llm=None
) -> Dict[str, Any]:
    """创建松弛式方案（独立调用）"""
    proposal = design_relaxation_style(destination, dest_data, user_portrait, days, llm)

    return {
        "success": True,
        "proposal": proposal,
        "agent_info": {
            "name": "RelaxationDesigner",
            "icon": "🌿",
            "description": "松弛式方案设计师"
        }
    }


def _generate_llm_description(
    destination: str,
    days: int,
    attractions: List[str],
    user_portrait: Dict[str, Any],
    llm=None
) -> str:
    """
    使用LLM生成松弛式方案的自然语言描述

    Args:
        destination: 目的地
        days: 天数
        attractions: 主要景点列表
        user_portrait: 用户画像
        llm: LLM实例

    Returns:
        LLM生成的描述文本
    """
    if llm:
        try:
            travel_type = user_portrait.get("travel_type", "")
            interests = user_portrait.get("primary_interests", [])
            interests_text = "、".join(interests) if interests else "休闲放松"

            prompt = f"""请为以下松弛式旅行方案生成一段吸引人的描述（约150-200字）：

目的地：{destination}
旅行天数：{days}天
旅行类型：{travel_type}
用户兴趣：{interests_text}
核心景点：{', '.join(attractions[:5])}

方案特点：
- 每天只安排1-2个景点
- 大量留白时间，不赶行程
- 睡到自然醒，累了就休息
- 适合度假为主的旅行方式

请生成一段能吸引向往慢节奏旅行的描述，突出松弛式旅行的放松和惬意。

直接输出描述文字，不要标题。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            description = response.content.strip()
            logger.info(f"[RelaxationDesigner] LLM生成描述成功: {len(description)}字")
            return description

        except Exception as e:
            logger.warning(f"[RelaxationDesigner] LLM生成描述失败: {e}")

    # 默认描述
    return f"""这是一场悠闲的松弛式之旅，在{destination}的{days}天里，您将彻底远离快节奏的生活。不同于匆忙的观光旅行，松弛式之旅注重内心感受和放松，每个景点都值得您慢慢品味。在{', '.join(attractions[:3])}等精选景点，您将放慢脚步，享受美食、自然和文化，让旅行真正成为一次充电和放松。"""
