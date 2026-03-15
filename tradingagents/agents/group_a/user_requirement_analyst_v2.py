"""
需求分析智能体 (Agent A1) - 通信版

分析用户需求，生成用户画像

继承自CommunicatingAgent，支持智能体间通信
"""

from typing import Dict, Any, List, Optional
import logging

from tradingagents.communication import (
    CommunicatingAgent,
    TravelAgentTypes,
    TravelCapabilities,
    TravelServices,
    TravelTopics,
    MessageType,
    AgentMessage,
    TravelMessageType
)

logger = logging.getLogger('travel_agents')


class UserRequirementAnalyst(CommunicatingAgent):
    """
    需求分析智能体

    分析用户需求，生成用户画像
    """

    def __init__(self, llm=None):
        super().__init__(
            agent_id="user_requirement_analyst",
            agent_name="UserRequirementAnalyst",
            agent_type=TravelAgentTypes.USER_REQUIREMENT_ANALYST,
            group="A"
        )
        self._llm = llm

    def get_capabilities(self) -> List[str]:
        """返回智能体能力列表"""
        return [
            TravelCapabilities.ANALYZE_REQUIREMENTS,
            "analyze_interests",
            "analyze_budget",
            "analyze_pace_preference"
        ]

    def get_services(self) -> List[str]:
        """返回智能体提供的服务列表"""
        return [TravelServices.ANALYZE_USER_REQUIREMENTS]

    def handle_request(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        处理请求消息

        Args:
            message: 请求消息

        Returns:
            响应消息
        """
        action = message.content.get("action")
        requirements = message.content.get("requirements")

        if action == "analyze_requirements":
            # 分析用户需求
            portrait = self.analyze_requirements(requirements)

            # 发布事件
            self.publish_event(
                "user_portrait_created",
                {
                    "portrait": portrait,
                    "requirements": requirements
                }
            )

            # 返回响应
            from tradingagents.communication import create_response
            return create_response(
                original_message=message,
                content={
                    "success": True,
                    "portrait": portrait
                }
            )

        return super().handle_request(message)

    def analyze_requirements(
        self,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        创建用户画像

        Args:
            requirements: 用户需求表单数据

        Returns:
            用户画像字典
        """
        logger.info(f"[需求分析] 开始分析用户需求")

        # 报告进度
        self.report_progress(25, "提取基本信息...")

        # 提取基本信息
        travel_scope = requirements.get('travel_scope', 'domestic')
        days = requirements.get('days', 5)
        adults = requirements.get('adults', 2)
        children = requirements.get('children', 0)
        budget = requirements.get('budget', 'medium')
        interests = requirements.get('interests', [])

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

        self.report_progress(50, "分析节奏偏好...")

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
        budget_level = budget_level_map.get(budget, "舒适型")

        self.report_progress(75, "生成用户画像...")

        # 使用LLM生成更详细的画像描述（如果可用）
        portrait_description = self._generate_portrait_description(
            travel_type, interests, pace_preference, budget_level
        )

        # 构建用户画像
        portrait = {
            "travel_scope": travel_scope,
            "travel_type": travel_type,
            "days": days,
            "total_travelers": total_travelers,
            "adults": adults,
            "children": children,
            "budget": budget,
            "budget_level": budget_level,
            "primary_interests": interests,
            "pace_preference": pace_preference,
            "portrait_description": portrait_description
        }

        self.report_progress(100, "需求分析完成")
        logger.info(f"[需求分析] 用户画像创建完成: {travel_type}, {pace_preference}, {budget_level}")

        return portrait

    def _generate_portrait_description(
        self,
        travel_type: str,
        interests: List[str],
        pace_preference: str,
        budget_level: str
    ) -> str:
        """
        使用LLM生成用户画像描述

        Args:
            travel_type: 旅行类型
            interests: 兴趣列表
            pace_preference: 节奏偏好
            budget_level: 预算等级

        Returns:
            画像描述
        """
        if self._llm:
            try:
                interests_text = "、".join(interests) if interests else "综合体验"

                prompt = f"""请为以下旅行者生成一段用户画像描述（100-150字）：

旅行类型：{travel_type}
主要兴趣：{interests_text}
节奏偏好：{pace_preference}
预算等级：{budget_level}

请生成一段生动的用户画像描述，突出这个旅行者的特点和偏好。

直接输出描述文字，不要标题。"""

                from langchain_core.messages import HumanMessage
                response = self._llm.invoke([HumanMessage(content=prompt)])
                description = response.content.strip()
                logger.info(f"[需求分析] LLM生成画像描述成功: {len(description)}字")
                return description

            except Exception as e:
                logger.warning(f"[需求分析] LLM生成画像描述失败: {e}")

        # 默认描述
        return f"""这是一位{travel_type}旅行者，偏好{pace_preference}的旅行节奏，对{'、'.join(interests[:3]) if interests else '各种体验'}有着浓厚的兴趣。预算方面选择{budget_level}，期待一次舒适愉快的旅行体验。"""


# ========== 保留原有函数接口以保持兼容性 ==========

def create_user_portrait(
    requirements: Dict[str, Any],
    llm=None
) -> Dict[str, Any]:
    """
    创建用户画像（兼容函数）

    Args:
        requirements: 用户需求表单数据
        llm: LLM实例（可选）

    Returns:
        用户画像字典
    """
    agent = UserRequirementAnalyst(llm=llm)
    return agent.analyze_requirements(requirements)


def user_requirement_analyst_node(state: Dict) -> Dict:
    """需求分析节点（用于LangGraph）"""
    requirements = state.get("user_requirements")
    llm = state.get("_llm")

    agent = UserRequirementAnalyst(llm=llm)
    portrait = agent.analyze_requirements(requirements)

    # 更新状态
    from langchain_core.messages import AIMessage
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"用户需求分析完成: {portrait.get('travel_type')}",
        name="UserRequirementAnalyst"
    ))

    state["user_portrait"] = portrait
    state["messages"] = messages

    return state
