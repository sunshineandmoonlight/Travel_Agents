"""
排名打分智能体 (Agent A3) - 通信版

对匹配的目的地进行排名和筛选，选出Top N

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


class RankingScorer(CommunicatingAgent):
    """
    排名打分智能体

    对匹配的目的地进行排名和筛选
    """

    def __init__(self, llm=None):
        super().__init__(
            agent_id="ranking_scorer",
            agent_name="RankingScorer",
            agent_type=TravelAgentTypes.RANKING_SCORER,
            group="A"
        )
        self._llm = llm

    def get_capabilities(self) -> List[str]:
        """返回智能体能力列表"""
        return [
            TravelCapabilities.RANK_DESTINATIONS,
            "score_destinations",
            "filter_top_n"
        ]

    def get_services(self) -> List[str]:
        """返回智能体提供的服务列表"""
        return [TravelServices.RANK_DESTINATIONS]

    def handle_request(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        处理请求消息

        Args:
            message: 请求消息

        Returns:
            响应消息
        """
        action = message.content.get("action")

        if action == "rank_and_select":
            candidates = message.content.get("candidates", [])
            user_portrait = message.content.get("user_portrait")
            top_n = message.content.get("top_n", 4)

            # 排名并选择Top N
            ranked = self.rank_and_select_top(candidates, user_portrait, top_n)

            # 发布事件
            self.publish_event(
                "destinations_ranked",
                {
                    "count": len(ranked),
                    "ranked": ranked
                }
            )

            return create_response(
                original_message=message,
                content={
                    "success": True,
                    "ranked_destinations": ranked,
                    "count": len(ranked)
                }
            )

        return super().handle_request(message)

    def rank_and_select_top(
        self,
        candidates: List[Dict[str, Any]],
        user_portrait: Dict[str, Any],
        top_n: int = 4
    ) -> List[Dict[str, Any]]:
        """
        对候选目的地进行排名，选择Top N

        Args:
            candidates: 候选目的地列表
            user_portrait: 用户画像
            top_n: 选择数量

        Returns:
            排名后的Top N目的地
        """
        logger.info(f"[排名打分] 开始对{len(candidates)}个目的地排名")

        self.report_progress(25, "计算综合得分...")

        # 为每个目的地计算综合得分
        for candidate in candidates:
            candidate["final_score"] = self._calculate_final_score(
                candidate, user_portrait
            )

        # 按综合得分排序
        candidates.sort(key=lambda x: x["final_score"], reverse=True)

        # 选择Top N
        top_destinations = candidates[:top_n]

        self.report_progress(100, f"排名完成，选择Top {len(top_destinations)}")
        logger.info(f"[排名打分] 完成，选择Top {len(top_destinations)}目的地")

        return top_destinations

    def _calculate_final_score(
        self,
        candidate: Dict[str, Any],
        user_portrait: Dict[str, Any]
    ) -> float:
        """
        计算综合得分

        Args:
            candidate: 候选目的地
            user_portrait: 用户画像

        Returns:
            综合得分 (0-100)
        """
        # 基础匹配分占60%
        match_score = candidate.get("match_score", 50)
        weighted_score = match_score * 0.6

        # 预算适配度占20%
        user_budget = user_portrait.get("budget", "medium")
        estimated_budget = candidate.get("estimated_budget", 3000)
        user_days = user_portrait.get("days", 5)

        # 简单的预算适配度计算
        expected_budgets = {
            "economy": 300 * user_days,
            "medium": 500 * user_days,
            "luxury": 800 * user_days
        }
        expected = expected_budgets.get(user_budget, 500 * user_days)
        budget_diff = abs(estimated_budget - expected)
        budget_score = max(0, 100 - budget_diff / expected * 100)

        weighted_score += budget_score * 0.2

        # 兴趣匹配度占20%
        user_interests = user_portrait.get("primary_interests", [])
        candidate_tags = candidate.get("tags", [])
        matched = len(set(user_interests) & set(candidate_tags))
        interest_score = (matched / max(len(user_interests), 1)) * 100
        weighted_score += interest_score * 0.2

        return min(weighted_score, 100)


# ========== 保留原有函数接口以保持兼容性 ==========

def rank_and_select_top(
    candidates: List[Dict[str, Any]],
    user_portrait: Dict[str, Any],
    top_n: int = 4,
    llm=None
) -> List[Dict[str, Any]]:
    """
    排名并选择Top N（兼容函数）

    Args:
        candidates: 候选目的地列表
        user_portrait: 用户画像
        top_n: 选择数量
        llm: LLM实例

    Returns:
        排名后的Top N目的地
    """
    agent = RankingScorer(llm=llm)
    return agent.rank_and_select_top(candidates, user_portrait, top_n)


def ranking_scorer_node(state: Dict) -> Dict:
    """排名打分节点（用于LangGraph）"""
    candidates = state.get("matched_destinations", [])
    user_portrait = state.get("user_portrait")
    llm = state.get("_llm")

    agent = RankingScorer(llm=llm)
    ranked = agent.rank_and_select_top(candidates, user_portrait, 4)

    # 更新状态
    from langchain_core.messages import AIMessage
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"排名打分完成: 选择Top {len(ranked)}目的地",
        name="RankingScorer"
    ))

    state["ranked_destinations"] = ranked
    state["messages"] = messages

    return state


def create_ranking_scorer_proposal(
    candidates: List[Dict[str, Any]],
    user_portrait: Dict[str, Any],
    top_n: int = 4,
    llm=None
) -> Dict[str, Any]:
    """创建排名方案（独立调用）"""
    agent = RankingScorer(llm=llm)
    ranked = agent.rank_and_select_top(candidates, user_portrait, top_n)

    return {
        "success": True,
        "ranked_destinations": ranked,
        "count": len(ranked),
        "agent_info": {
            "name": "RankingScorer",
            "description": "排名打分智能体"
        }
    }
