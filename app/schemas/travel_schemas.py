"""
旅行系统 Pydantic 模型

用于 API 请求和响应的数据验证
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, TypeVar, Generic
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from uuid import UUID

T = TypeVar('T')


# ============================================================
# 基础模型
# ============================================================

class BaseSchema(BaseModel):
    """基础 Schema"""
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


# ============================================================
# 用户相关 Schema
# ============================================================

class UserBase(BaseSchema):
    """用户基础信息"""
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    nickname: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None


class UserCreate(UserBase):
    """用户注册"""
    password: str = Field(..., min_length=8, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserUpdate(BaseSchema):
    """用户信息更新"""
    nickname: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    """用户响应"""
    id: int
    uuid: UUID
    avatar_url: Optional[str]
    role: str
    is_verified: bool
    guides_count: int
    bookmarks_count: int
    likes_count: int
    created_at: datetime
    last_login_at: Optional[datetime]


# ============================================================
# 攻略相关 Schema
# ============================================================

class ItineraryDay(BaseSchema):
    """单日行程"""
    day: int
    theme: Optional[str] = None
    date: Optional[str] = None
    morning: Optional[Dict[str, Any]] = None
    lunch: Optional[Dict[str, Any]] = None
    afternoon: Optional[Dict[str, Any]] = None
    dinner: Optional[Dict[str, Any]] = None
    evening: Optional[Dict[str, Any]] = None


class BudgetItem(BaseSchema):
    """预算项"""
    amount: int
    description: Optional[str] = None
    cost_saving_tips: Optional[str] = None


class BudgetBreakdown(BaseSchema):
    """预算分解"""
    transportation: Optional[BudgetItem] = None
    accommodation: Optional[BudgetItem] = None
    meals: Optional[BudgetItem] = None
    attractions: Optional[BudgetItem] = None
    miscellaneous: Optional[BudgetItem] = None
    total_budget: int
    daily_average: Optional[int] = None
    per_person_average: Optional[int] = None
    budget_assessment: Optional[str] = None
    recommendations: Optional[List[str]] = None
    money_saving_tips: Optional[List[str]] = None


class AttractionInfo(BaseSchema):
    """景点信息"""
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: Optional[str] = None
    rating: Optional[float] = None
    ticket_price: Optional[int] = None
    recommended_duration: Optional[str] = None
    highlights: Optional[List[str]] = None


class TravelGuideBase(BaseSchema):
    """攻略基础信息"""
    title: str = Field(..., min_length=5, max_length=200)
    description: Optional[str] = None
    destination: str = Field(..., min_length=1, max_length=100)
    destination_type: str = Field(..., pattern=r'^(domestic|international)$')
    days: int = Field(..., ge=1, le=30)
    budget_level: Optional[str] = Field(None, pattern=r'^(low|medium|high)$')
    total_budget: Optional[int] = Field(None, ge=0)
    travelers_count: int = Field(default=2, ge=1, le=20)
    travel_style: Optional[str] = Field(None, pattern=r'^(immersive|exploration|relaxed)$')
    interest_tags: List[str] = Field(default_factory=list)


class TravelGuideCreate(TravelGuideBase):
    """创建攻略"""
    itinerary: Optional[Dict[str, Any]] = None
    budget_breakdown: Optional[Dict[str, Any]] = None
    attractions: Optional[List[Dict[str, Any]]] = None
    accommodation: Optional[Dict[str, Any]] = None
    transportation: Optional[Dict[str, Any]] = None
    cover_image: Optional[str] = None
    images: Optional[List[str]] = None
    generation_method: str = Field(default='ai')
    generation_config: Optional[Dict[str, Any]] = None
    best_seasons: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    geo_latitude: Optional[float] = None
    geo_longitude: Optional[float] = None


class TravelGuideUpdate(BaseSchema):
    """更新攻略"""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = None
    days: Optional[int] = Field(None, ge=1, le=30)
    budget_level: Optional[str] = Field(None, pattern=r'^(low|medium|high)$')
    total_budget: Optional[int] = Field(None, ge=0)
    travelers_count: Optional[int] = Field(None, ge=1, le=20)
    travel_style: Optional[str] = Field(None, pattern=r'^(immersive|exploration|relaxed)$')
    interest_tags: Optional[List[str]] = None
    itinerary: Optional[Dict[str, Any]] = None
    budget_breakdown: Optional[Dict[str, Any]] = None
    attractions: Optional[List[Dict[str, Any]]] = None
    accommodation: Optional[Dict[str, Any]] = None
    transportation: Optional[Dict[str, Any]] = None
    cover_image: Optional[str] = None
    images: Optional[List[str]] = None
    best_seasons: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None


class TravelGuideResponse(TravelGuideBase):
    """攻略响应"""
    id: int
    uuid: UUID
    city_code: Optional[str]
    country_code: Optional[str]
    itinerary: Optional[Dict[str, Any]]
    budget_breakdown: Optional[Dict[str, Any]]
    attractions: Optional[List[Dict[str, Any]]]
    accommodation: Optional[Dict[str, Any]]
    transportation: Optional[Dict[str, Any]]
    cover_image: Optional[str]
    images: List[str]
    generation_method: str
    generation_config: Optional[Dict[str, Any]]
    view_count: int
    like_count: int
    bookmark_count: int
    copy_count: int
    rating_avg: float
    rating_count: int
    status: str
    is_featured: bool
    is_editor_pick: bool
    slug: Optional[str]
    keywords: Optional[str]
    meta_description: Optional[str]
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    user_id: Optional[int]
    username: Optional[str]
    best_seasons: List[str]
    weather_info: Optional[Dict[str, Any]]
    tags: List[str]
    category: Optional[str]
    geo_latitude: Optional[float]
    geo_longitude: Optional[float]


class TravelGuideListResponse(BaseSchema):
    """攻略列表响应（简化版）"""
    id: int
    uuid: UUID
    title: str
    destination: str
    destination_type: str
    days: int
    total_budget: Optional[int]
    travel_style: Optional[str]
    cover_image: Optional[str]
    view_count: int
    like_count: int
    bookmark_count: int
    rating_avg: float
    rating_count: int
    is_featured: bool
    is_editor_pick: bool
    created_at: datetime
    published_at: Optional[datetime]
    username: Optional[str]


class TravelGuideSummary(TravelGuideListResponse):
    """攻略摘要（带作者信息）"""
    author_nickname: Optional[str] = None
    author_avatar: Optional[str] = None


# ============================================================
# 攻略生成请求 Schema
# ============================================================

class TravelPlanRequest(BaseSchema):
    """旅行规划请求"""
    destination: str = Field(..., min_length=1, max_length=100, description="目的地")
    days: int = Field(..., ge=1, le=30, description="天数")
    budget: str = Field(default='medium', pattern=r'^(low|medium|high)$', description="预算级别")
    travelers: int = Field(default=2, ge=1, le=20, description="人数")
    interest_type: Optional[str] = Field(None, description="兴趣类型")
    selected_style: Optional[str] = Field(None, description="选择的风格")
    save_as_guide: bool = Field(default=False, description="是否保存为攻略")
    guide_title: Optional[str] = Field(None, min_length=5, max_length=200, description="攻略标题")


class TravelPlanResponse(BaseSchema):
    """旅行规划响应"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    guide_id: Optional[int] = None
    guide_uuid: Optional[UUID] = None


# ============================================================
# 收藏相关 Schema
# ============================================================

class BookmarkCreate(BaseSchema):
    """创建收藏"""
    guide_id: int
    notes: Optional[str] = None
    folder_name: Optional[str] = Field(None, max_length=100)


class BookmarkResponse(BaseSchema):
    """收藏响应"""
    id: int
    user_id: int
    guide_id: int
    notes: Optional[str]
    folder_name: str
    created_at: datetime
    guide_title: Optional[str] = None
    guide_destination: Optional[str] = None


class BookmarkListResponse(BookmarkResponse):
    """收藏列表响应"""
    guide_days: Optional[int] = None
    guide_total_budget: Optional[int] = None
    guide_travel_style: Optional[str] = None
    guide_cover_image: Optional[str] = None


# ============================================================
# 评论相关 Schema
# ============================================================

class ReviewCreate(BaseSchema):
    """创建评论"""
    guide_id: int
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    content: str = Field(..., min_length=10, max_length=2000)
    images: Optional[List[str]] = None


class ReviewUpdate(BaseSchema):
    """更新评论"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None, min_length=10, max_length=2000)
    images: Optional[List[str]] = None


class ReviewResponse(BaseSchema):
    """评论响应"""
    id: int
    guide_id: int
    user_id: int
    rating: int
    title: Optional[str]
    content: str
    images: List[str]
    helpful_count: int
    not_helpful_count: int
    created_at: datetime
    updated_at: datetime
    is_visible: bool
    user_username: Optional[str] = None
    user_nickname: Optional[str] = None
    user_avatar: Optional[str] = None


# ============================================================
# 点赞相关 Schema
# ============================================================

class LikeCreate(BaseSchema):
    """创建点赞"""
    guide_id: int


class LikeResponse(BaseSchema):
    """点赞响应"""
    id: int
    guide_id: int
    user_id: int
    created_at: datetime


class LikeStatusResponse(BaseSchema):
    """点赞状态响应"""
    is_liked: bool
    like_count: int


# ============================================================
# 分享相关 Schema
# ============================================================

class ShareCreate(BaseSchema):
    """创建分享"""
    guide_id: int
    share_type: str = Field(..., pattern=r'^(wechat|weibo|link|qrcode)$')
    share_title: Optional[str] = Field(None, max_length=200)


class ShareResponse(BaseSchema):
    """分享响应"""
    id: int
    guide_id: int
    user_id: Optional[int]
    share_type: str
    share_title: Optional[str]
    click_count: int
    created_at: datetime


# ============================================================
# 搜索和过滤 Schema
# ============================================================

class GuideSearchQuery(BaseSchema):
    """攻略搜索查询"""
    keyword: Optional[str] = Field(None, description="搜索关键词")
    destination: Optional[str] = Field(None, description="目的地")
    destination_type: Optional[str] = Field(None, pattern=r'^(domestic|international)$')
    days_min: Optional[int] = Field(None, ge=1)
    days_max: Optional[int] = Field(None, le=30)
    budget_level: Optional[str] = Field(None, pattern=r'^(low|medium|high)$')
    travel_style: Optional[str] = Field(None, pattern=r'^(immersive|exploration|relaxed)$')
    interest_tags: Optional[List[str]] = None
    sort_by: str = Field(default='created_at', pattern=r'^(created_at|rating_avg|view_count|like_count)$')
    sort_order: str = Field(default='desc', pattern=r'^(asc|desc)$')
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class GuideSearchResponse(BaseSchema):
    """搜索响应"""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[TravelGuideListResponse]


# ============================================================
# 推荐相关 Schema
# ============================================================

class RecommendationResponse(BaseSchema):
    """推荐响应"""
    guide_id: int
    title: str
    destination: str
    days: int
    cover_image: Optional[str]
    rating_avg: float
    reason: str
    similarity_score: Optional[float] = None


# ============================================================
# 景点相关 Schema
# ============================================================

class AttractionBase(BaseSchema):
    """景点基础信息"""
    name: str = Field(..., min_length=1, max_length=200)
    name_en: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    category: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class AttractionResponse(AttractionBase):
    """景点响应"""
    id: int
    name_aliases: List[str]
    province: Optional[str]
    address: Optional[str]
    tags: List[str]
    interest_types: List[str]
    highlights: List[str]
    opening_hours: Optional[Dict[str, Any]]
    ticket_info: Optional[Dict[str, Any]]
    official_website: Optional[str]
    cover_image: Optional[str]
    images: List[str]
    rating_avg: Optional[float]
    review_count: int
    popularity_score: int
    recommended_duration: Optional[str]
    best_time_to_visit: Optional[str]
    tips: List[str]
    price_range: Optional[str]
    ticket_price_min: Optional[int]
    ticket_price_max: Optional[int]
    nearby_subway: List[str]
    parking_info: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    data_source: Optional[str]
    source_id: Optional[str]
    created_at: datetime


class AttractionListResponse(BaseSchema):
    """景点列表响应（简化版）"""
    id: int
    name: str
    city: Optional[str]
    category: Optional[str]
    rating_avg: Optional[float]
    cover_image: Optional[str]
    recommended_duration: Optional[str]


# ============================================================
# 模板相关 Schema
# ============================================================

class TemplateBase(BaseSchema):
    """模板基础信息"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    template_type: Optional[str] = None
    destination_type: Optional[str] = Field(None, pattern=r'^(domestic|international)$')


class TemplateCreate(TemplateBase):
    """创建模板"""
    min_days: Optional[int] = Field(None, ge=1)
    max_days: Optional[int] = Field(None, le=30)
    budget_level: Optional[List[str]] = None
    template_structure: Dict[str, Any]
    prompts: Optional[Dict[str, Any]] = None
    example_destination: Optional[str] = None
    example_output: Optional[Dict[str, Any]] = None


class TemplateResponse(TemplateBase):
    """模板响应"""
    id: int
    min_days: Optional[int]
    max_days: Optional[int]
    budget_level: List[str]
    template_structure: Dict[str, Any]
    prompts: Optional[Dict[str, Any]]
    example_destination: Optional[str]
    example_output: Optional[Dict[str, Any]]
    usage_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ============================================================
# 统计相关 Schema
# ============================================================

class GuideStatsResponse(BaseSchema):
    """攻略统计响应"""
    total_guides: int
    published_guides: int
    total_views: int
    total_likes: int
    total_bookmarks: int
    top_destinations: List[Dict[str, Any]]
    recent_guides: List[TravelGuideListResponse]


class UserStatsResponse(BaseSchema):
    """用户统计响应"""
    guides_count: int
    bookmarks_count: int
    likes_count: int
    reviews_count: int
    total_views: int


# ============================================================
# 通用响应 Schema
# ============================================================

class MessageResponse(BaseSchema):
    """通用消息响应"""
    success: bool
    message: str
    data: Optional[Any] = None


class PaginatedResponse(BaseSchema, Generic[T]):
    """分页响应基类"""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[T]


# ============================================================
# 导出所有 Schema
# ============================================================

__all__ = [
    # 用户
    'UserCreate',
    'UserUpdate',
    'UserResponse',
    # 攻略
    'TravelGuideCreate',
    'TravelGuideUpdate',
    'TravelGuideResponse',
    'TravelGuideListResponse',
    'TravelGuideSummary',
    # 行程
    'ItineraryDay',
    'BudgetItem',
    'BudgetBreakdown',
    'AttractionInfo',
    # 规划
    'TravelPlanRequest',
    'TravelPlanResponse',
    # 收藏
    'BookmarkCreate',
    'BookmarkResponse',
    'BookmarkListResponse',
    # 评论
    'ReviewCreate',
    'ReviewUpdate',
    'ReviewResponse',
    # 点赞
    'LikeCreate',
    'LikeResponse',
    'LikeStatusResponse',
    # 分享
    'ShareCreate',
    'ShareResponse',
    # 搜索
    'GuideSearchQuery',
    'GuideSearchResponse',
    # 推荐
    'RecommendationResponse',
    # 景点
    'AttractionBase',
    'AttractionResponse',
    'AttractionListResponse',
    # 模板
    'TemplateCreate',
    'TemplateResponse',
    # 统计
    'GuideStatsResponse',
    'UserStatsResponse',
    # 通用
    'MessageResponse',
]
