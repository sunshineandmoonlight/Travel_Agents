"""
智能体增强方案 - 为所有智能体添加LLM自然语言描述

让每个智能体的输出都包含：
1. 结构化数据（用于程序处理）
2. LLM生成的解释/描述（用于用户阅读）
"""

from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage

# ============================================================
# 增强函数：为智能体添加LLM描述
# ============================================================

def add_llm_explanation_to_destination_matcher(
    destination: str,
    user_portrait: Dict[str, Any],
    match_score: int,
    tags: List[str],
    llm
) -> str:
    """为地区匹配添加LLM解释说明"""

    system_prompt = """你是一位旅行规划顾问。请用简洁温暖的语言，
解释为什么推荐这个目的地给用户。"""

    user_message = f"""我推荐目的地：{destination}

匹配分：{match_score}/100
目的地特色：{', '.join(tags[:5])}

用户画像：
- 旅行类型：{user_portrait.get('travel_type')}
- 兴趣：{', '.join(user_portrait.get('primary_interests', []))}
- 预算偏好：{user_portrait.get('budget_level')}
- 节奏偏好：{user_portrait.get('pace_preference')}

请用2-3句话解释为什么推荐这个目的地。"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        return response.content
    except:
        return f"{destination}完美契合您的{user_portrait.get('travel_type')}需求，"
              f"这里有丰富的{', '.join(user_portrait.get('primary_interests', []))}等待您探索。"


def add_llm_explanation_to_ranking_scorer(
    destination: str,
    user_portrait: Dict[str, Any],
    final_score: float,
    match_score: int,
    budget_score: float,
    llm
) -> str:
    """为排名打分添加LLM解释说明"""

    system_prompt = """你是一位旅行规划顾问。请解释为什么这个目的地排名靠前。"""

    user_message = f"""目的地：{destination}

综合得分：{final_score:.1f}/100
- 匹配分：{match_score}/100
- 预算适配度：{budget_score:.1f}/100

用户画像：
- 预算：{user_portrait.get('budget')}
- 兴趣：{', '.join(user_portrait.get('primary_interests', []))}

请用2-3句话解释为什么这个目的地排名靠前。"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        return response.content
    except:
        return f"{destination}在综合评分中表现优秀，"
              f"各项指标都符合您的需求标准。"


def add_llm_explanation_to_transport_plan(
    method: str,
    from_loc: str,
    to_loc: str,
    cost: int,
    duration: str,
    llm
) -> str:
    """为交通规划添加LLM解释说明"""

    system_prompt = """你是一位旅行顾问。请解释为什么推荐这种交通方式。"""

    user_message = f"""交通路线：{from_loc} → {to_loc}

推荐方式：{method}
费用：{cost}元
耗时：{duration}

请用一句话解释为什么推荐这种方式（考虑便捷性、经济性等）。"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        return response.content
    except:
        return f"选择{method}是因为它便捷经济，性价比高。"


def add_llm_explanation_to_dining_recommendation(
    restaurant_name: str,
    cuisine_type: str,
    price_range: str,
    location: str,
    llm
) -> str:
    """为餐饮推荐添加LLM解释说明"""

    system_prompt = """你是一位美食顾问。请介绍这家餐厅的推荐理由。"""

    user_message = f"""餐厅：{restaurant_name}
菜系：{cuisine_type}
价位：{price_range}
位置：{location}

请用2-3句话介绍为什么推荐这家餐厅。"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        return response.content
    except:
        return f"{restaurant_name}是当地人推荐的{cuisine_type}餐厅，"
              f"口味正宗，性价比高。"


def add_llm_explanation_to_accommodation_recommendation(
    area: str,
    price_range: str,
    highlights: List[str],
    destination: str,
    llm
) -> str:
    """为住宿推荐添加LLM解释说明"""

    system_prompt = """你是一位旅行顾问。请介绍为什么推荐这个住宿区域。"""

    user_message = f"""住宿区域：{area}
价位：{price_range}
特色：{', '.join(highlights[:3])}
目的地：{destination}

请用2-3句话介绍为什么推荐住在这个区域。"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        return response.content
    except:
        return f"{area}交通便利，周边设施齐全，"
              f"是住宿的优质选择。"


# ============================================================
# 增强版智能体输出格式
# ============================================================

class EnhancedAgentOutput:
    """增强版智能体输出格式"""

    def __init__(self, structured_data: Dict[str, Any], llm_explanation: str):
        self.structured_data = structured_data
        self.llm_explanation = llm_explanation

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            **self.structured_data,
            "ai_explanation": self.llm_explanation
        }


# ============================================================
# 使用示例
# ============================================================

def example_enhanced_destination_matching(llm) -> Dict[str, Any]:
    """示例：增强版地区匹配"""

    # 原始结构化数据
    structured_data = {
        "destination": "西安",
        "match_score": 90,
        "estimated_budget": 4000,
        "tags": ["历史文化", "美食", "古迹"]
    }

    # 用户画像
    user_portrait = {
        "travel_type": "情侣游",
        "primary_interests": ["历史文化", "美食"],
        "budget_level": "中等预算"
    }

    # LLM解释
    llm_explanation = add_llm_explanation_to_destination_matcher(
        structured_data["destination"],
        user_portrait,
        structured_data["match_score"],
        structured_data["tags"],
        llm
    )

    # 合并输出
    return {
        **structured_data,
        "ai_explanation": llm_explanation
    }


def example_enhanced_transport_plan(llm) -> Dict[str, Any]:
    """示例：增强版交通规划"""

    # 原始结构化数据
    structured_data = {
        "from": "酒店",
        "to": "回民街",
        "method": "地铁",
        "cost": 5,
        "duration": "约30分钟"
    }

    # LLM解释
    llm_explanation = add_llm_explanation_to_transport_plan(
        structured_data["method"],
        structured_data["from"],
        structured_data["to"],
        structured_data["cost"],
        structured_data["duration"],
        llm
    )

    # 合并输出
    return {
        **structured_data,
        "ai_explanation": llm_explanation
    }


# ============================================================
# 批量增强所有智能体的输出
# ============================================================

def enhance_agent_output(
    agent_type: str,
    structured_output: Dict[str, Any],
    user_context: Dict[str, Any],
    llm
) -> Dict[str, Any]:
    """
    为任意智能体的输出添加LLM解释

    Args:
        agent_type: 智能体类型 (destination_matcher, ranking_scorer,
                     transport_planner, dining_recommender, accommodation_advisor)
        structured_output: 结构化输出
        user_context: 用户上下文
        llm: LLM实例

    Returns:
        增强后的输出（包含ai_explanation字段）
    """

    if agent_type == "destination_matcher":
        structured_output["ai_explanation"] = add_llm_explanation_to_destination_matcher(
            structured_output["destination"],
            user_context,
            structured_output["match_score"],
            structured_output["tags"],
            llm
        )

    elif agent_type == "ranking_scorer":
        structured_output["ai_explanation"] = add_llm_explanation_to_ranking_scorer(
            structured_output["destination"],
            user_context,
            structured_output.get("final_score", 0),
            structured_output["match_score"],
            structured_output.get("budget_score", 0),
            llm
        )

    elif agent_type == "transport_planner":
        # 为每个交通路段添加解释
        for segment in structured_output.get("transport_segments", []):
            segment["ai_explanation"] = add_llm_explanation_to_transport_plan(
                segment["method"],
                segment["from"],
                segment["to"],
                segment["cost"],
                segment["duration"],
                llm
            )

    elif agent_type == "dining_recommender":
        # 为每个餐厅推荐添加解释
        for day_dining in structured_output.get("daily_dining", []):
            for meal in day_dining.get("meals", []):
                restaurant = meal.get("recommended_restaurant", {})
                if isinstance(restaurant, dict):
                    restaurant["ai_explanation"] = add_llm_explanation_to_dining_recommendation(
                        restaurant.get("name", ""),
                        restaurant.get("cuisine_type", ""),
                        restaurant.get("price_range", ""),
                        restaurant.get("location", ""),
                        llm
                    )

    elif agent_type == "accommodation_advisor":
        # 为每个住宿区域添加解释
        for accom in structured_output.get("accommodations", []):
            accom["ai_explanation"] = add_llm_explanation_to_accommodation_recommendation(
                accom.get("area", ""),
                accom.get("price_range", ""),
                accom.get("highlights", []),
                user_context.get("destination", ""),
                llm
            )

    return structured_output
