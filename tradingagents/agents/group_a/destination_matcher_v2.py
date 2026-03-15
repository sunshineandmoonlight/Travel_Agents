"""
地区匹配智能体 (Agent A2) - 通信版

根据用户画像匹配目的地数据库

继承自CommunicatingAgent，支持智能体间通信
"""

from typing import Dict, Any, List, Optional
import logging

from tradingagents.communication import (
    CommunicatingAgent,
    TravelAgentTypes,
    TravelCapabilities,
    TravelServices,
    MessageType,
    AgentMessage,
    create_response
)

logger = logging.getLogger('travel_agents')


class DestinationMatcher(CommunicatingAgent):
    """
    地区匹配智能体

    根据用户画像匹配目的地数据库
    """

    def __init__(self, llm=None):
        super().__init__(
            agent_id="destination_matcher",
            agent_name="DestinationMatcher",
            agent_type=TravelAgentTypes.DESTINATION_MATCHER,
            group="A"
        )
        self._llm = llm

        # 导入数据库
        from tradingagents.agents.group_a.destination_matcher import (
            DOMESTIC_DESTINATIONS_DB,
            INTERNATIONAL_DESTINATIONS_DB
        )
        self._domestic_db = DOMESTIC_DESTINATIONS_DB
        self._international_db = INTERNATIONAL_DESTINATIONS_DB

    def get_capabilities(self) -> List[str]:
        """返回智能体能力列表"""
        return [
            TravelCapabilities.MATCH_DESTINATION,
            "match_by_interests",
            "match_by_budget",
            "match_by_pace"
        ]

    def get_services(self) -> List[str]:
        """返回智能体提供的服务列表"""
        return [TravelServices.FIND_DESTINATIONS]

    def handle_request(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        处理请求消息

        Args:
            message: 请求消息

        Returns:
            响应消息
        """
        action = message.content.get("action")

        if action == "match_destinations":
            user_portrait = message.content.get("user_portrait")
            travel_scope = message.content.get("travel_scope", "domestic")

            # 匹配目的地
            candidates = self.match_destinations(user_portrait, travel_scope)

            # 发布事件
            self.publish_event(
                "destinations_matched",
                {
                    "count": len(candidates),
                    "candidates": candidates[:5]  # 只发送前5个
                }
            )

            return create_response(
                original_message=message,
                content={
                    "success": True,
                    "candidates": candidates,
                    "count": len(candidates)
                }
            )

        return super().handle_request(message)

    def match_destinations(
        self,
        user_portrait: Dict[str, Any],
        travel_scope: str = "domestic"
    ) -> List[Dict[str, Any]]:
        """
        匹配目的地

        Args:
            user_portrait: 用户画像
            travel_scope: 旅行范围（domestic/international）

        Returns:
            匹配的目的地列表
        """
        logger.info(f"[地区匹配] 开始匹配目的地")

        self.report_progress(25, "筛选旅行范围...")

        # 根据旅行范围筛选数据库
        if travel_scope == "domestic":
            destinations = self._domestic_db
        else:
            destinations = self._international_db

        if not destinations:
            logger.warning(f"[地区匹配] 未找到{travel_scope}目的地")
            return []

        self.report_progress(50, "计算匹配分数...")

        # 计算每个目的地的匹配分数
        candidates = []
        for dest_name, dest_data in destinations.items():
            match_score = self._calculate_match_score(dest_data, user_portrait)
            estimated_budget = self._estimate_budget(dest_name, dest_data, user_portrait)

            candidates.append({
                "destination": dest_name,
                "match_score": match_score,
                "estimated_budget": estimated_budget,
                "tags": dest_data.get("tags", []),
                "highlights": dest_data.get("highlights", [])[:3]
            })

        # 按匹配分数排序
        candidates.sort(key=lambda x: x["match_score"], reverse=True)

        # 取前20个
        candidates = candidates[:20]

        self.report_progress(100, f"匹配完成，找到{len(candidates)}个目的地")
        logger.info(f"[地区匹配] 匹配完成，找到{len(candidates)}个目的地")

        return candidates

    def _calculate_match_score(
        self,
        dest_data: Dict[str, Any],
        user_portrait: Dict[str, Any]
    ) -> int:
        """
        计算目的地匹配分数

        Args:
            dest_data: 目的地数据
            user_portrait: 用户画像

        Returns:
            匹配分数 (0-100)
        """
        score = 50  # 基础分

        # 兴趣匹配
        user_interests = user_portrait.get("primary_interests", [])
        dest_tags = dest_data.get("tags", [])

        matched_interests = set(user_interests) & set(dest_tags)
        interest_bonus = len(matched_interests) * 10
        score += min(interest_bonus, 30)  # 最多加30分

        # 预算匹配
        user_budget = user_portrait.get("budget", "medium")
        budget_level = dest_data.get("budget_level", {})

        if user_budget in budget_level:
            score += 10

        # 节奏偏好匹配
        pace_preference = user_portrait.get("pace_preference", "均衡型")
        if pace_preference == "松弛型" and "休闲度假" in dest_tags:
            score += 10
        elif pace_preference == "探索型" and "户外探险" in dest_tags:
            score += 10
        elif pace_preference == "沉浸型" and "历史文化" in dest_tags:
            score += 10

        return min(score, 100)

    def _estimate_budget(
        self,
        dest_name: str,
        dest_data: Dict[str, Any],
        user_portrait: Dict[str, Any]
    ) -> int:
        """
        估算旅行预算

        Args:
            dest_name: 目的地名称
            dest_data: 目的地数据
            user_portrait: 用户画像

        Returns:
            预估预算（元）
        """
        user_budget = user_portrait.get("budget", "medium")
        days = user_portrait.get("days", 5)
        travelers = user_portrait.get("total_travelers", 2)

        budget_level = dest_data.get("budget_level", {})
        daily_budget = budget_level.get(user_budget, 500)

        total_budget = daily_budget * days * travelers

        return total_budget


# ========== 保留原有函数接口以保持兼容性 ==========

def match_destinations(
    user_portrait: Dict[str, Any],
    travel_scope: str = "domestic",
    llm=None
) -> List[Dict[str, Any]]:
    """
    匹配目的地（兼容函数）

    Args:
        user_portrait: 用户画像
        travel_scope: 旅行范围
        llm: LLM实例

    Returns:
        匹配的目的地列表
    """
    agent = DestinationMatcher(llm=llm)
    return agent.match_destinations(user_portrait, travel_scope)


def destination_matcher_node(state: Dict) -> Dict:
    """地区匹配节点（用于LangGraph）"""
    user_portrait = state.get("user_portrait")
    travel_scope = state.get("travel_scope", "domestic")
    llm = state.get("_llm")

    agent = DestinationMatcher(llm=llm)
    candidates = agent.match_destinations(user_portrait, travel_scope)

    # 更新状态
    from langchain_core.messages import AIMessage
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"地区匹配完成: 找到{len(candidates)}个目的地",
        name="DestinationMatcher"
    ))

    state["matched_destinations"] = candidates
    state["messages"] = messages

    return state
