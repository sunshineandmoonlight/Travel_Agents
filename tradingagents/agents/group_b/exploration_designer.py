"""
探索式方案设计师 (Agent B2)

设计理念: 多元打卡，丰富行程，不断惊喜

特点:
- 每日4-5个景点
- 高效游览，丰富体验
- 每天不同区域，新鲜感满满
- 适合好奇心强、怕无聊的旅行者
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


def _get_diverse_attractions(destination: str, days: int) -> List[Dict[str, Any]]:
    """
    使用新的API工具获取多样化的景点数据

    探索式需要更多类型的景点，包括热门、文化、自然、商业等

    Args:
        destination: 目的地名称
        days: 天数

    Returns:
        景点列表
    """
    all_attractions = []

    # 优先使用SerpAPI搜索多种类型
    if os.getenv("SERPAPI_KEY") and os.getenv("SERPAPI_KEY") != "your_serpapi_key_here":
        try:
            serpapi_tool = SerpAPITool()

            # 搜索多种类型的景点
            search_keywords_list = ["景点", "博物馆", "公园", "商业街", "地标", "文化"]

            for keywords in search_keywords_list:
                serp_results = asyncio.run(serpapi_tool.search_attractions(
                    destination=destination,
                    keywords=keywords,
                    days=days,
                    style="exploration"
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
                logger.info(f"[探索式设计师] SerpAPI搜索到 {len(unique_attractions)} 个景点")
                return unique_attractions[:days * 5]  # 每天最多5个

        except Exception as e:
            logger.warning(f"[探索式设计师] SerpAPI搜索失败: {e}")

    # 补充OpenTripMap数据
    if len(all_attractions) < days * 3 and os.getenv("OPENTRIPMAP_API_KEY") and os.getenv("OPENTRIPMAP_API_KEY") != "your_opentripmap_key_here":
        try:
            opentripmap_tool = OpenTripMapTool()
            otm_results = asyncio.run(opentripmap_tool.search_attractions(
                destination=destination,
                keywords="view_points",
                days=days,
                style="exploration"
            ))

            if otm_results:
                # 去重
                existing_names = {a.get("name", "") for a in all_attractions}
                for otm_attr in otm_results:
                    if otm_attr.get("name", "") not in existing_names:
                        all_attractions.append(otm_attr)

                logger.info(f"[探索式设计师] OpenTripMap补充 {len(otm_results)} 个景点")
        except Exception as e:
            logger.warning(f"[探索式设计师] OpenTripMap搜索失败: {e}")

    if all_attractions:
        logger.info(f"[探索式设计师] 总共获取 {len(all_attractions)} 个实时景点")
        # 返回前 days*5 个
        seen_names = set()
        unique_attractions = []
        for attr in all_attractions:
            name = attr.get("name", "")
            if name and name not in seen_names:
                seen_names.add(name)
                unique_attractions.append(attr)
                if len(unique_attractions) >= days * 5:
                    break
        return unique_attractions
    else:
        logger.warning("[探索式设计师] 未获取到实时景点数据")
        return []


def design_exploration_style(
    destination: str,
    dest_data: Dict[str, Any],
    user_portrait: Dict[str, Any],
    days: int,
    llm=None
) -> Dict[str, Any]:
    """
    设计探索式旅行方案

    优先调用工具API获取实时景点数据，失败时使用数据库数据

    Args:
        destination: 目的地名称
        dest_data: 目的地数据
        user_portrait: 用户画像
        days: 旅行天数
        llm: LLM实例（可选）

    Returns:
        探索式风格方案
    """
    logger.info(f"[探索式设计师] 为{destination}设计{days}天探索式方案")

    tags = dest_data.get("tags", [])
    user_interests = user_portrait.get("primary_interests", [])

    # 1. 优先调用工具API获取实时景点（探索式需要更多景点）
    real_attractions = []
    data_source = "fallback"

    try:
        all_attractions = _get_diverse_attractions(destination, days)

        if all_attractions and len(all_attractions) > 0:
            real_attractions = all_attractions
            data_source = "realtime_api"
            logger.info(f"[探索式设计师] 使用实时API数据: {len(real_attractions)}个景点")
    except Exception as e:
        logger.warning(f"[探索式设计师] 实时数据获取失败: {e}")

    # 2. 降级：使用数据库highlights
    if not real_attractions:
        logger.info(f"[探索式设计师] 使用数据库highlights")
        highlights = dest_data.get("highlights", [])
        real_attractions = [{"name": h, "type": "景点", "location": {}} for h in highlights]
        data_source = "fallback"

    # 3. 每天分配3个景点，高效游览
    daily_itinerary = []
    attractions_per_day = max(3, len(real_attractions) // days)

    for day in range(1, days + 1):
        start_idx = (day - 1) * attractions_per_day
        end_idx = min(start_idx + attractions_per_day + 1, len(real_attractions))
        day_attractions_data = real_attractions[start_idx:end_idx]
        day_attractions = [a.get("name", a) for a in day_attractions_data]

        # 生成活动安排（高效打卡）
        activities = []
        time_slots = ["上午", "中午前", "下午", "傍晚", "晚上"]

        for i, attr in enumerate(day_attractions[:3]):
            if i < len(time_slots):
                time = time_slots[i]
                activities.append({
                    "time": time,
                    "activity": f"游览{attr}",
                    "description": f"打卡{attr}精华景点",
                    "attraction_id": attr
                })

        # 添加特色活动
        if day == 1 and "购物" in str(tags):
            activities.append({
                "time": "晚上",
                "activity": "商业街区探索",
                "description": "感受当地商业文化"
            })
        elif "美食" in str(tags):
            activities.append({
                "time": "晚上",
                "activity": "夜市或美食街",
                "description": "品尝各种当地小吃"
            })
        else:
            activities.append({
                "time": "晚上",
                "activity": "观景台或地标打卡",
                "description": "夜景摄影"
            })

        daily_itinerary.append({
            "day": day,
            "title": f"第{day}天：{'、'.join(day_attractions[:2])}探索之旅",
            "activities": activities[:3],
            "attractions": day_attractions,
            "pace": "快节奏"
        })

    # 生成亮点
    highlights_desc = [
        "多元打卡，丰富体验",
        "每天不同区域，新鲜感满满",
        "高效游览，绝不无聊"
    ]

    if "购物" in tags:
        highlights_desc.append("购物+景点双重体验")

    if "美食" in tags:
        highlights_desc.append("吃遍当地特色美食")

    # 计算费用（探索式通常中等，注重效率）
    budget = dest_data.get("budget_level", {}).get("medium", 500)
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

    # 【数据共享】保存 Group B 搜索结果供后续使用
    if data_source == "realtime_api" and real_attractions:
        try:
            from tradingagents.utils.shared_data import save_group_b_search_results

            save_group_b_search_results(
                attractions=real_attractions,
                api_sources=api_sources_used,
                destination_data={
                    "destination": destination,
                    "days": days,
                    "style": "exploration"
                }
            )
            logger.info("[探索式设计师] 已保存搜索结果到共享数据")
        except Exception as e:
            logger.warning(f"[探索式设计师] 保存共享数据失败: {e}")

    # 使用LLM生成方案描述
    llm_description = _generate_llm_description(
        destination,
        days,
        used_attractions[:5] if len(used_attractions) > 5 else used_attractions,
        user_portrait,
        llm
    )

    return {
        "style_name": "探索式",
        "style_icon": "🧭",
        "style_type": "exploration",
        "style_description": "多元打卡，丰富行程，不断惊喜",
        "daily_pace": "快节奏，每日3个景点高效游览",
        "intensity_level": 3,
        "preview_itinerary": [
            {"day": 1, "title": f"{used_attractions[0] if used_attractions else destination}、{used_attractions[1] if len(used_attractions) > 1 else '周边'}打卡", "attractions": used_attractions[:3]},
            {"day": 2, "title": f"{used_attractions[2] if len(used_attractions) > 2 else destination}、{used_attractions[3] if len(used_attractions) > 3 else '周边'}探索", "attractions": used_attractions[2:5] if len(used_attractions) > 2 else used_attractions}
        ],
        "estimated_cost": total_budget,
        "best_for": "好奇心宝宝，怕无聊的旅行者",
        "highlights": highlights_desc[:5],
        "daily_itinerary": daily_itinerary,
        "data_source": data_source,
        "api_sources_used": api_sources_used,
        "llm_description": llm_description,
        "agent_info": {
            "name_cn": "探索式设计师",
            "name_en": "ExplorationDesigner",
            "icon": "🧭",
            "group": "B",
            "llm_enabled": llm is not None
        }
    }


def exploration_designer_node(state: Dict) -> Dict:
    """探索式设计师节点（用于LangGraph）"""
    destination = state.get("selected_destination")
    dest_data = state.get("selected_destination_data", {})
    user_portrait = state.get("user_portrait")
    days = state.get("days", 5)
    llm = state.get("_llm")

    if not destination or not user_portrait:
        logger.error("[探索式设计师] 缺少必要数据")
        return state

    # 设计方案
    proposal = design_exploration_style(destination, dest_data, user_portrait, days, llm)

    # 更新状态
    from langchain_core.messages import AIMessage
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"探索式方案设计完成: {days}天丰富行程",
        name="ExplorationDesigner"
    ))

    if "style_proposals" not in state:
        state["style_proposals"] = []
    state["style_proposals"].append(proposal)
    state["messages"] = messages

    return state


def create_exploration_proposal(
    destination: str,
    dest_data: Dict[str, Any],
    user_portrait: Dict[str, Any],
    days: int,
    llm=None
) -> Dict[str, Any]:
    """创建探索式方案（独立调用）"""
    proposal = design_exploration_style(destination, dest_data, user_portrait, days, llm)

    return {
        "success": True,
        "proposal": proposal,
        "agent_info": {
            "name": "ExplorationDesigner",
            "icon": "🧭",
            "description": "探索式方案设计师"
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
    使用LLM生成探索式方案的自然语言描述

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
            interests_text = "、".join(interests) if interests else "多元探索"

            prompt = f"""请为以下探索式旅行方案生成一段吸引人的描述（约150-200字）：

目的地：{destination}
旅行天数：{days}天
旅行类型：{travel_type}
用户兴趣：{interests_text}
核心景点：{', '.join(attractions[:5])}

方案特点：
- 每天安排4-5个景点
- 多元打卡，丰富体验
- 高效游览，绝不无聊
- 每天不同区域，新鲜感满满

请生成一段能吸引向往丰富多样旅行体验的旅行者，突出探索式旅行的多样性和惊喜。

直接输出描述文字，不要标题。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            description = response.content.strip()
            logger.info(f"[ExplorationDesigner] LLM生成描述成功: {len(description)}字")
            return description

        except Exception as e:
            logger.warning(f"[ExplorationDesigner] LLM生成描述失败: {e}")

    # 默认描述
    return f"""这是一场精彩的探索式之旅，在{destination}的{days}天里，您将体验最丰富多样的旅行方式。不同于慢节奏的观光旅行，探索式之旅注重高效和多样性，在{', '.join(attractions[:3])}等经典地标，您将每天打卡4-5个景点，涵盖文化、自然、美食、购物等多个方面。让旅行成为一次不断发现惊喜的精彩旅程。"""
