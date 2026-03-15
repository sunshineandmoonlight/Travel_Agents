"""
数据模型模块
"""

# 导入旅行数据模型
from .travel import (
    Base,
    User,
    TravelGuide,
    UserBookmark,
    GuideReview,
    GuideLike,
    GuideShare,
    GuideVersion,
    Attraction,
    GuideTemplate,
    GuideRecommendation,
)

__all__ = [
    "Base",
    "User",
    "TravelGuide",
    "UserBookmark",
    "GuideReview",
    "GuideLike",
    "GuideShare",
    "GuideVersion",
    "Attraction",
    "GuideTemplate",
    "GuideRecommendation",
]
