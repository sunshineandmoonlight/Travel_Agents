"""
需求分析智能体 (Agent A1)

分析用户需求，生成用户画像

阶段3: 推荐地区
"""

from typing import Dict, Any, List
from langchain_core.messages import AIMessage
import logging

logger = logging.getLogger('travel_agents')


def create_user_portrait(
    requirements: Dict[str, Any],
    llm=None
) -> Dict[str, Any]:
    """
    创建用户画像

    Args:
        requirements: 用户需求表单数据
        llm: LLM实例（可选）

    Returns:
        用户画像字典
    """
    logger.info(f"[需求分析] 开始分析用户需求")

    # 提取基本信息
    travel_scope = requirements.get('travel_scope', 'domestic')
    days = requirements.get('days', 5)
    adults = requirements.get('adults', 2)
    children = requirements.get('children', 0)
    budget = requirements.get('budget', 'medium')
    interests = requirements.get('interests', [])

    # 🔥 新增：提取特殊需求
    special_requests = requirements.get('special_requests', '')
    if special_requests:
        logger.info(f"[需求分析] 用户特殊需求: {special_requests}")

    total_travelers = adults + children

    # 分析旅行类型
    if children > 0:
        travel_type = "亲子游"
    elif total_travelers == 2:
        travel_type = "情侣游"
    elif total_travelers >= 3:
        travel_type = "团队游"
    else:
        travel_type = "个人游"

    # 分析节奏偏好（基于兴趣）
    pace_map = {
        "历史文化": "慢",
        "自然风光": "中等",
        "美食体验": "慢",
        "休闲度假": "最慢",
        "户外探险": "快",
        "购物娱乐": "中等",
        "网红打卡": "快",
        "摄影": "慢",
        "小众秘境": "中等"
    }

    pace_scores = []
    for interest in interests:
        pace = pace_map.get(interest, "中等")
        if pace == "最慢":
            pace_scores.append(1)
        elif pace == "慢":
            pace_scores.append(2)
        elif pace == "中等":
            pace_scores.append(3)
        elif pace == "快":
            pace_scores.append(4)

    if pace_scores:
        avg_pace = sum(pace_scores) / len(pace_scores)
        if avg_pace <= 1.5:
            pace_preference = "松弛型"
        elif avg_pace <= 2.5:
            pace_preference = "沉浸型"
        elif avg_pace <= 3.5:
            pace_preference = "均衡型"
        else:
            pace_preference = "探索型"
    else:
        pace_preference = "均衡型"

    # 分析预算等级
    budget_level_map = {
        "economy": "经济型",
        "medium": "舒适型",
        "luxury": "品质型"
    }

    # 如果有LLM，使用LLM生成更详细的画像描述
    if llm:
        try:
            portrait_prompt = f"""
根据以下用户需求，生成一个简洁的用户画像描述（50字以内）：

旅行范围: {travel_scope}
天数: {days}天
人数: {total_travelers}人（成人{adults}人，儿童{children}人）
预算: {budget_level_map[budget]}
兴趣: {', '.join(interests) if interests else '未指定'}

请用简洁的语言描述这个用户的旅行特征。
"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=portrait_prompt)])
            portrait_description = response.content.strip()
        except Exception as e:
            logger.warning(f"[需求分析] LLM生成画像失败: {e}")
            portrait_description = _generate_simple_description(
                travel_type, interests, pace_preference
            )
    else:
        portrait_description = _generate_simple_description(
            travel_type, interests, pace_preference
        )

    # 生成详细的LLM描述文本
    llm_description = _generate_detailed_portrait_description(
        travel_type, interests, pace_preference, budget_level_map[budget],
        days, total_travelers, llm
    )

    # 构建用户画像
    user_portrait = {
        "travel_type": travel_type,
        "travel_scope": travel_scope,
        "total_travelers": total_travelers,
        "adults": adults,
        "children": children,
        "days": days,
        "budget": budget,
        "budget_level": budget_level_map[budget],
        "primary_interests": interests[:5] if interests else [],
        "pace_preference": pace_preference,
        "description": portrait_description,
        "llm_description": llm_description,  # 新增：详细的LLM描述
        "special_requests": special_requests,  # 🔥 新增：特殊需求（用于城市优先推荐）

        # 用于匹配的权重
        "matching_weights": {
            "history": 3 if "历史文化" in interests else 1,
            "nature": 3 if "自然风光" in interests else 1,
            "food": 3 if "美食体验" in interests else 1,
            "relaxation": 3 if "休闲度假" in interests else 1,
            "adventure": 3 if "户外探险" in interests else 1,
            "shopping": 3 if "购物娱乐" in interests else 1,
        },

        # 智能体信息
        "agent_info": {
            "name_cn": "需求分析专家",
            "name_en": "UserRequirementAnalyst",
            "icon": "👤",
            "group": "A"
        }
    }

    logger.info(f"[需求分析] 用户画像: {travel_type}, {pace_preference}, {budget_level_map[budget]}")

    return user_portrait


def _generate_simple_description(
    travel_type: str,
    interests: List[str],
    pace_preference: str
) -> str:
    """生成简单的画像描述"""
    parts = [travel_type]

    if interests:
        parts.append(f"喜欢{','.join(interests[:3])}")

    parts.append(f"{pace_preference}节奏")

    return "、".join(parts) + "的旅行者"


def _generate_detailed_portrait_description(
    travel_type: str,
    interests: List[str],
    pace_preference: str,
    budget_level: str,
    days: int,
    travelers: int,
    llm=None
) -> str:
    """
    生成详细的用户画像描述

    Args:
        travel_type: 旅行类型
        interests: 兴趣列表
        pace_preference: 节奏偏好
        budget_level: 预算等级
        days: 天数
        travelers: 人数
        llm: LLM实例

    Returns:
        LLM生成的描述文本
    """
    interests_text = '、'.join(interests[:5]) if interests else "文化、美食、休闲"

    # 如果有LLM，使用LLM生成详细描述
    if llm:
        try:
            prompt = f"""请为以下旅行者生成一段详细的画像描述（约150-200字）：

旅行类型：{travel_type}
旅行天数：{days}天
出行人数：{travelers}人
预算等级：{budget_level}
兴趣偏好：{interests_text}
节奏偏好：{pace_preference}

描述要求：
1. 用亲切自然的语气，像在介绍一位朋友
2. 描述这位旅行者的特点和偏好
3. 推荐适合他们的旅行方式
4. 给出个性化的旅行建议
5. 语言要生动有趣，有画面感

请直接输出描述文字，不要标题和格式符号。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            description = response.content.strip()
            logger.info(f"[需求分析专家] LLM生成详细描述成功: {len(description)}字")
            return description
        except Exception as e:
            logger.warning(f"[需求分析专家] LLM生成详细描述失败: {e}，使用默认描述")

    # 默认描述
    pace_desc = {
        "松弛型": "喜欢悠闲自在的旅行节奏",
        "沉浸型": "喜欢深度体验当地文化",
        "均衡型": "喜欢劳逸结合的旅行方式",
        "探索型": "喜欢紧凑高效的行程安排"
    }.get(pace_preference, "喜欢舒适愉快的旅行")

    description = f"""根据您提供的信息，我们为您生成了个性化旅行画像：

🧑‍🤝‍🧑 您的旅行类型：{travel_type}，{travelers}人同行{children_info(travel_type)}
📅 行程天数：{days}天
💰 预算偏好：{budget_level}
❤️ 兴趣偏好：{interests_text}
🚶 节奏偏好：{pace_desc}

💡 个性化建议：
• 基于您的兴趣，我们推荐匹配度最高的目的地和景点
• 行程安排会考虑您的节奏偏好，确保旅行舒适度
• 餐饮和住宿选择会根据您的预算进行优化

我们已为您分析完成，接下来将为您推荐最适合的目的地！✨"""

    return description


def children_info(travel_type: str) -> str:
    """获取儿童相关描述"""
    if travel_type == "亲子游":
        return "，包括可爱的宝贝"
    return ""


def user_requirement_analyst_node(state: Dict) -> Dict:
    """
    需求分析智能体节点（用于LangGraph）

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    requirements = state.get("user_requirements")
    llm = state.get("_llm")

    if not requirements:
        logger.error("[需求分析] 缺少用户需求数据")
        state["error"] = "缺少用户需求数据"
        return state

    # 创建用户画像
    user_portrait = create_user_portrait(requirements, llm)

    # 更新状态
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"需求分析完成: {user_portrait['description']}",
        name="UserRequirementAnalyst"
    ))

    state["user_portrait"] = user_portrait
    state["messages"] = messages
    state["current_stage"] = "requirement_analyzed"

    return state


# ============================================================
# 独立调用函数（用于API）
# ============================================================

def analyze_user_requirements(
    requirements: Dict[str, Any],
    llm=None
) -> Dict[str, Any]:
    """
    分析用户需求（独立调用）

    Args:
        requirements: 用户需求表单数据
        llm: LLM实例（可选）

    Returns:
        包含用户画像的响应
    """
    user_portrait = create_user_portrait(requirements, llm)

    return {
        "success": True,
        "user_portrait": user_portrait,
        "agent_info": {
            "name": "UserRequirementAnalyst",
            "icon": "👤",
            "description": "分析用户需求，生成画像"
        }
    }
