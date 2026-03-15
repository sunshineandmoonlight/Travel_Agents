"""
沉浸式方案设计师 (Agent B1)

设计理念: 少而精，深度体验，慢节奏感受

特点:
- 每日2-3个景点
- 深度游览，留足体验时间
- 住下来感受当地生活
- 适合文化、历史爱好者
- 使用SerpAPI和OpenTripMap获取实时数据
- 使用LLM生成个性化描述
"""

from typing import Dict, Any, List
import logging
import asyncio
import os

logger = logging.getLogger('travel_agents')


def _generate_llm_description(
    destination: str,
    days: int,
    attractions: List[str],
    user_portrait: Dict[str, Any],
    llm=None
) -> str:
    """
    使用LLM生成沉浸式方案的自然语言描述

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
            interests_text = "、".join(interests) if interests else "深度体验"

            prompt = f"""请为以下沉浸式旅行方案生成一段吸引人的描述（约150-200字）：

目的地：{destination}
旅行天数：{days}天
旅行类型：{travel_type}
用户兴趣：{interests_text}
核心景点：{', '.join(attractions[:5])}

方案特点：
- 深度体验，每个景点停留3-4小时
- 慢节奏，拒绝走马观花
- 专注于文化、历史、艺术的沉浸式感受
- 住下来感受当地生活

请生成一段能吸引喜欢深度体验的旅行者的描述，突出这种旅行方式的独特魅力。

直接输出描述文字，不要标题。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            description = response.content.strip()
            logger.info(f"[沉浸式设计师] LLM生成描述成功: {len(description)}字")
            return description

        except Exception as e:
            logger.warning(f"[沉浸式设计师] LLM生成描述失败: {e}")

    # 默认描述
    return f"""这是一场深度文化之旅，在{destination}的{days}天里，您将以沉浸式的方式体验这座城市的灵魂。不同于走马观花的打卡式旅行，我们精心挑选了最具代表性的文化景点，每天只安排2-3个深度游览点，让您有充足时间去感受历史的厚重与艺术的精妙。在{', '.join(attractions[:3])}等经典地标，您将放慢脚步，细细品味每一处细节，让旅行的意义不再在于"来过"，而在于"感受"。"""


def _get_real_attractions(destination: str, days: int, keywords: str, style: str = "immersive") -> List[Dict[str, Any]]:
    """
    使用新的API工具获取实时景点数据

    Args:
        destination: 目的地名称
        days: 天数
        keywords: 搜索关键词
        style: 旅行风格

    Returns:
        景点列表
    """
    all_attractions = []

    # 优先使用SerpAPI
    if os.getenv("SERPAPI_KEY") and os.getenv("SERPAPI_KEY") != "your_serpapi_key_here":
        try:
            from .api_tools.serpapi_tool import SerpAPITool

            serpapi_tool = SerpAPITool()
            serp_results = asyncio.run(serpapi_tool.search_attractions(
                destination=destination,
                keywords=keywords,
                days=days,
                style=style
            ))

            if serp_results:
                all_attractions.extend(serp_results)
                logger.info(f"[沉浸式设计师] SerpAPI搜索到 {len(serp_results)} 个景点")
        except Exception as e:
            logger.warning(f"[沉浸式设计师] SerpAPI搜索失败: {e}")

    # 补充OpenTripMap数据
    if os.getenv("OPENTRIPMAP_API_KEY") and os.getenv("OPENTRIPMAP_API_KEY") != "your_opentripmap_key_here":
        try:
            from .api_tools.opentripmap_tool import OpenTripMapTool

            opentripmap_tool = OpenTripMapTool()
            otm_results = asyncio.run(opentripmap_tool.search_attractions(
                destination=destination,
                keywords=keywords,
                days=days,
                style=style
            ))

            if otm_results:
                # 去重（基于名称）
                existing_names = {a.get("name", "") for a in all_attractions}
                for otm_attr in otm_results:
                    if otm_attr.get("name", "") not in existing_names:
                        all_attractions.append(otm_attr)

                logger.info(f"[沉浸式设计师] OpenTripMap搜索到 {len(otm_results)} 个景点")
        except Exception as e:
            logger.warning(f"[沉浸式设计师] OpenTripMap搜索失败: {e}")

    if all_attractions:
        logger.info(f"[沉浸式设计师] 总共获取 {len(all_attractions)} 个实时景点")
    else:
        logger.warning("[沉浸式设计师] 未获取到实时景点数据")

    return all_attractions


def _filter_cultural_attractions(attractions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """筛选适合深度体验的文化景点"""
    cultural_keywords = ["博物馆", "文化", "历史", "遗址", "古迹", "寺庙", "宫殿", "故居", "艺术"]
    filtered = []

    for attr in attractions:
        name = attr.get("name", "")
        type_str = attr.get("type", "")

        # 检查是否包含文化关键词
        if any(keyword in name or keyword in type_str for keyword in cultural_keywords):
            filtered.append(attr)

    # 如果筛选后太少，返回原列表
    if len(filtered) < len(attractions) // 2:
        return attractions

    return filtered


def design_immersive_style(
    destination: str,
    dest_data: Dict[str, Any],
    user_portrait: Dict[str, Any],
    days: int,
    llm=None
) -> Dict[str, Any]:
    """
    设计沉浸式旅行方案 (增强版)

    使用SerpAPI和OpenTripMap获取实时数据，使用LLM生成个性化描述

    Args:
        destination: 目的地名称
        dest_data: 目的地数据
        user_portrait: 用户画像
        days: 旅行天数
        llm: LLM实例（可选）

    Returns:
        沉浸式风格方案
    """
    logger.info(f"[沉浸式设计师] 为{destination}设计{days}天沉浸式方案")

    tags = dest_data.get("tags", [])
    user_interests = user_portrait.get("primary_interests", [])

    # 1. 使用API工具获取实时景点
    real_attractions = []
    data_source = "fallback"
    api_sources_used = []

    # 根据用户兴趣确定搜索关键词
    search_keywords = "博物馆 文化遗址 历史景点"
    if "美食" in user_interests:
        search_keywords = "美食街 特色餐厅 老字号"
    elif "自然" in user_interests:
        search_keywords = "公园 景区 自然风光"

    try:
        all_attractions = _get_real_attractions(destination, days, search_keywords, "immersive")

        if all_attractions:
            # 筛选适合深度游览的景点
            if "文化" in user_interests or "历史" in user_interests:
                real_attractions = _filter_cultural_attractions(all_attractions)
            else:
                real_attractions = all_attractions

            data_source = "realtime_api"
            api_sources_used = list(set(a.get("source", "unknown") for a in real_attractions))
            logger.info(f"[沉浸式设计师] 使用实时API数据: {len(real_attractions)}个景点，来源: {api_sources_used}")
    except Exception as e:
        logger.warning(f"[沉浸式设计师] 实时数据获取失败: {e}")

    # 2. 降级：使用数据库highlights
    if not real_attractions:
        logger.info(f"[沉浸式设计师] 使用数据库highlights")
        highlights = dest_data.get("highlights", [])
        real_attractions = [{"name": h, "type": "景点", "location": {}} for h in highlights]
        data_source = "fallback"

    # 3. 每天分配2-3个景点，深度游览
    daily_itinerary = []
    attractions_per_day = max(2, len(real_attractions) // days)

    for day in range(1, days + 1):
        start_idx = (day - 1) * attractions_per_day
        end_idx = min(start_idx + attractions_per_day + 1, len(real_attractions))
        day_attractions_data = real_attractions[start_idx:end_idx]
        day_attractions = [a.get("name", a) for a in day_attractions_data]

        # 生成活动安排（深度体验）
        activities = []
        for i, attr in enumerate(day_attractions[:2]):
            activities.append({
                "time": "上午" if len(activities) == 0 else "下午",
                "activity": f"深度游览{attr}",
                "description": f"细细品味{attr}的文化与历史",
                "attraction_id": attr
            })
            if len(activities) == 1:
                activities.append({
                    "time": "下午",
                    "activity": f"{attr}周边探索",
                    "description": "发现隐藏的小巷和故事",
                    "attraction_id": attr
                })

        # 添加特色体验
        if "美食" in str(tags) or "小吃" in str(tags):
            activities.append({
                "time": "晚上",
                "activity": "当地美食探店",
                "description": "寻找本地人推荐的特色餐厅"
            })
        elif "文化" in str(tags) or "历史" in str(tags):
            activities.append({
                "time": "晚上",
                "activity": "文化体验活动",
                "description": "观看传统表演或参与文化活动"
            })
        else:
            activities.append({
                "time": "晚上",
                "activity": "自由漫步",
                "description": "在老街古巷中感受当地夜晚"
            })

        daily_itinerary.append({
            "day": day,
            "title": f"第{day}天：{day_attractions[0] if day_attractions else destination}深度体验",
            "activities": activities,
            "attractions": day_attractions,
            "pace": "慢节奏"
        })

    # 生成亮点
    highlights_desc = [
        "深度体验，每个地方停留更长时间",
        "住下来，慢慢感受当地生活",
        "与当地人交流，了解真实的文化"
    ]

    if "历史文化" in tags or "古迹" in tags:
        highlights_desc.append("专注历史文化，细细品味古韵")

    if "美食" in tags:
        highlights_desc.append("寻找巷子里的老味道")

    # 计算费用（沉浸式通常稍高，因为更注重品质）
    budget = dest_data.get("budget_level", {}).get("medium", 500)
    total_budget = budget * days * user_portrait.get("total_travelers", 2)

    # 获取实际使用的景点名称
    used_attractions = []
    for day_plan in daily_itinerary:
        used_attractions.extend(day_plan.get("attractions", []))

    # 使用LLM生成方案描述
    llm_description = _generate_llm_description(
        destination,
        days,
        used_attractions[:5] if len(used_attractions) > 5 else used_attractions,
        user_portrait,
        llm
    )

    return {
        "style_name": "沉浸式",
        "style_icon": "🎭",
        "style_type": "immersive",
        "style_description": "深度体验，慢节奏感受当地文化历史",
        "daily_pace": "慢节奏，每日2-3个景点深度游览",
        "intensity_level": 2,
        "preview_itinerary": [
            {"day": 1, "title": f"{used_attractions[0] if used_attractions else destination}深度游", "attractions": used_attractions[:2]},
            {"day": 2, "title": f"{used_attractions[2] if len(used_attractions) > 2 else destination}体验", "attractions": used_attractions[2:4]}
        ],
        "estimated_cost": total_budget,
        "best_for": "喜欢深度了解文化历史的人",
        "highlights": highlights_desc[:5],
        "daily_itinerary": daily_itinerary,
        "data_source": data_source,
        "api_sources_used": api_sources_used,
        "llm_description": llm_description,
        "agent_info": {
            "name_cn": "沉浸式设计师",
            "name_en": "ImmersiveDesigner",
            "icon": "🎭",
            "group": "B",
            "llm_enabled": llm is not None
        }
    }


def immersive_designer_node(state: Dict) -> Dict:
    """沉浸式设计师节点（用于LangGraph）"""
    destination = state.get("selected_destination")
    dest_data = state.get("selected_destination_data", {})
    user_portrait = state.get("user_portrait")
    days = state.get("days", 5)
    llm = state.get("_llm")

    if not destination or not user_portrait:
        logger.error("[沉浸式设计师] 缺少必要数据")
        return state

    # 设计方案
    proposal = design_immersive_style(destination, dest_data, user_portrait, days, llm)

    # 更新状态
    from langchain_core.messages import AIMessage
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"沉浸式方案设计完成: {days}天深度体验",
        name="ImmersiveDesigner"
    ))

    if "style_proposals" not in state:
        state["style_proposals"] = []
    state["style_proposals"].append(proposal)
    state["messages"] = messages

    return state


# ============================================================
# 独立调用函数
# ============================================================

def create_immersive_proposal(
    destination: str,
    dest_data: Dict[str, Any],
    user_portrait: Dict[str, Any],
    days: int,
    llm=None
) -> Dict[str, Any]:
    """创建沉浸式方案（独立调用）"""
    proposal = design_immersive_style(destination, dest_data, user_portrait, days, llm)

    return {
        "success": True,
        "proposal": proposal,
        "agent_info": {
            "name": "ImmersiveDesigner",
            "icon": "🎭",
            "description": "沉浸式方案设计师"
        }
    }
