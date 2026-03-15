"""
旅行服务模块

提供旅行规划、攻略管理、搜索、推荐等服务
"""

from app.services.travel_service import (
    TravelPlanService,
    GuideService,
    SearchService,
    RecommendationService,
    StatsService
)

__all__ = [
    'TravelPlanService',
    'GuideService',
    'SearchService',
    'RecommendationService',
    'StatsService',
]
