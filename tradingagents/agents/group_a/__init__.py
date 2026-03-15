"""
组A: 地区推荐智能体

包含3个智能体：
1. UserRequirementAnalyst - 需求分析智能体
2. DestinationMatcher - 地区匹配智能体
3. RankingScorer - 排序评分智能体

支持两种模式:
- 原有函数式接口（向后兼容）
- 通信式智能体类（新功能，支持智能体间通信）
"""

# ========== 原有函数式接口（向后兼容）==========
from .user_requirement_analyst import (
    create_user_portrait,
    user_requirement_analyst_node,
    analyze_user_requirements
)

from .destination_matcher import (
    match_destinations,
    destination_matcher_node,
    find_matching_destinations,
    DOMESTIC_DESTINATIONS_DB,
    INTERNATIONAL_DESTINATIONS_DB
)

from .ranking_scorer import (
    rank_and_select_top,
    ranking_scorer_node,
    rank_and_recommend,
    recommend_destinations
)

# ========== 通信式智能体类（新功能）==========
from .user_requirement_analyst_v2 import UserRequirementAnalyst
from .destination_matcher_v2 import DestinationMatcher
from .ranking_scorer_v2 import RankingScorer

__all__ = [
    # UserRequirementAnalyst
    "create_user_portrait",
    "user_requirement_analyst_node",
    "analyze_user_requirements",
    "UserRequirementAnalyst",  # 新增：通信式智能体类

    # DestinationMatcher
    "match_destinations",
    "destination_matcher_node",
    "find_matching_destinations",
    "DOMESTIC_DESTINATIONS_DB",
    "INTERNATIONAL_DESTINATIONS_DB",
    "DestinationMatcher",  # 新增：通信式智能体类

    # RankingScorer
    "rank_and_select_top",
    "ranking_scorer_node",
    "rank_and_recommend",
    "recommend_destinations",
    "RankingScorer",  # 新增：通信式智能体类
]
