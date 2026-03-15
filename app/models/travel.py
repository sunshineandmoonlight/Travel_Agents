"""
旅行系统 SQLAlchemy 模型

定义旅行攻略中心的所有数据库模型
使用传统 Column 语法确保兼容性
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Numeric,
    ForeignKey, Table, Index, CheckConstraint, UniqueConstraint,
    ARRAY, JSON, Enum as SQLEnum, event, func
)
from sqlalchemy.orm import (
    DeclarativeBase, relationship, validates
)
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY as PGArray
import uuid


# ============================================================
# Base 类
# ============================================================

class Base(DeclarativeBase):
    """所有模型的基类"""
    pass


# ============================================================
# 用户模型
# ============================================================

class User(Base):
    """用户表"""
    __tablename__ = 'users'

    # 主键
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)

    # 基本信息
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(100))
    avatar_url = Column(String(500))

    # 偏好设置 (JSONB)
    preferences = Column(JSONB, default=dict)

    # 统计
    guides_count = Column(Integer, default=0)
    bookmarks_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)

    # 权限
    role = Column(String(20), default='user')
    is_verified = Column(Boolean, default=False)

    # 时间戳
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))

    # 状态
    is_active = Column(Boolean, default=True)
    bio = Column(Text)

    # 关系
    travel_guides = relationship('TravelGuide', back_populates='user', cascade='all, delete-orphan')
    bookmarks = relationship('UserBookmark', back_populates='user', cascade='all, delete-orphan')
    reviews = relationship('GuideReview', back_populates='user', cascade='all, delete-orphan')
    likes = relationship('GuideLike', back_populates='user', cascade='all, delete-orphan')

    # 索引和约束
    __table_args__ = (
        Index('idx_users_email', 'email'),
        Index('idx_users_username', 'username'),
        Index('idx_users_role', 'role'),
        CheckConstraint("username ~* '^[a-zA-Z0-9_]{3,50}$'", name='users_username_check'),
        CheckConstraint("email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name='users_email_check'),
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


# ============================================================
# 旅行攻略模型
# ============================================================

class TravelGuide(Base):
    """旅行攻略表（核心表）"""
    __tablename__ = 'travel_guides'

    # 主键
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)

    # 基本信息
    title = Column(String(200), nullable=False)
    description = Column(Text)

    # 目的地信息
    destination = Column(String(100), nullable=False)
    destination_type = Column(String(20), nullable=False)
    city_code = Column(String(50))
    country_code = Column(String(10))

    # 行程信息
    days = Column(Integer, nullable=False)
    budget_level = Column(String(20))
    total_budget = Column(Integer)
    travelers_count = Column(Integer, default=2)

    # 风格标签
    travel_style = Column(String(50))
    interest_tags = Column(PGArray(String), default=list)

    # 详细内容 (JSONB)
    itinerary = Column(JSONB, default=dict)
    budget_breakdown = Column(JSONB, default=dict)
    attractions = Column(JSONB, default=list)
    accommodation = Column(JSONB)
    transportation = Column(JSONB)

    # 媒体资源
    cover_image = Column(String(500))
    images = Column(PGArray(String), default=list)

    # 生成信息
    generation_method = Column(String(50), default='ai')
    generation_config = Column(JSONB)

    # 统计信息
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    bookmark_count = Column(Integer, default=0)
    copy_count = Column(Integer, default=0)

    # 评分
    rating_avg = Column(Numeric(3, 2), default=0)
    rating_count = Column(Integer, default=0)

    # 状态
    status = Column(String(20), default='draft')
    is_featured = Column(Boolean, default=False)
    is_editor_pick = Column(Boolean, default=False)

    # SEO
    slug = Column(String(200), unique=True)
    keywords = Column(String(500))
    meta_description = Column(String(500))

    # 时间戳
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))

    # 作者
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    username = Column(String(100))

    # 季节性信息
    best_seasons = Column(PGArray(String), default=list)
    weather_info = Column(JSONB)

    # 标签和分类
    tags = Column(PGArray(String), default=list)
    category = Column(String(50))

    # 地理位置
    geo_latitude = Column(Numeric(10, 8))
    geo_longitude = Column(Numeric(11, 8))

    # 关系
    user = relationship('User', back_populates='travel_guides')
    bookmarks = relationship('UserBookmark', back_populates='guide', cascade='all, delete-orphan')
    reviews = relationship('GuideReview', back_populates='guide', cascade='all, delete-orphan')
    likes = relationship('GuideLike', back_populates='guide', cascade='all, delete-orphan')
    shares = relationship('GuideShare', back_populates='guide', cascade='all, delete-orphan')
    versions = relationship('GuideVersion', back_populates='guide', cascade='all, delete-orphan')

    # 索引和约束
    __table_args__ = (
        Index('idx_guides_destination', 'destination'),
        Index('idx_guides_type', 'destination_type'),
        Index('idx_guides_style', 'travel_style'),
        Index('idx_guides_status', 'status'),
        Index('idx_guides_featured', 'is_featured'),
        Index('idx_guides_editor_pick', 'is_editor_pick'),
        Index('idx_guides_user', 'user_id'),
        Index('idx_guides_created', 'created_at'),
        Index('idx_guides_rating', 'rating_avg'),
        CheckConstraint("slug ~* '^[a-z0-9-]+$'", name='travel_guides_slug_check'),
        CheckConstraint("status IN ('draft', 'published', 'archived')", name='travel_guides_status_check'),
    )

    def __repr__(self):
        return f"<TravelGuide(id={self.id}, title='{self.title}', destination='{self.destination}')>"


# ============================================================
# 攻略收藏模型
# ============================================================

class UserBookmark(Base):
    """用户收藏表"""
    __tablename__ = 'user_bookmarks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    guide_id = Column(Integer, ForeignKey('travel_guides.id', ondelete='CASCADE'), nullable=False)

    # 收藏信息
    notes = Column(Text)
    folder_name = Column(String(100), default='默认收藏夹')

    # 时间戳
    created_at = Column(DateTime(timezone=True), default=func.now())

    # 关系
    user = relationship('User', back_populates='bookmarks')
    guide = relationship('TravelGuide', back_populates='bookmarks')

    # 索引和约束
    __table_args__ = (
        UniqueConstraint('user_id', 'guide_id', name='user_bookmarks_unique'),
        Index('idx_bookmarks_user', 'user_id'),
        Index('idx_bookmarks_guide', 'guide_id'),
    )

    def __repr__(self):
        return f"<UserBookmark(user_id={self.user_id}, guide_id={self.guide_id})>"


# ============================================================
# 攻略评论模型
# ============================================================

class GuideReview(Base):
    """攻略评论表"""
    __tablename__ = 'guide_reviews'

    id = Column(Integer, primary_key=True)
    guide_id = Column(Integer, ForeignKey('travel_guides.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # 评论内容
    rating = Column(Integer)
    title = Column(String(200))
    content = Column(Text, nullable=False)

    # 图片
    images = Column(PGArray(String), default=list)

    # 统计
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)

    # 时间戳
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # 状态
    is_visible = Column(Boolean, default=True)

    # 关系
    guide = relationship('TravelGuide', back_populates='reviews')
    user = relationship('User', back_populates='reviews')

    # 索引和约束
    __table_args__ = (
        Index('idx_reviews_guide', 'guide_id'),
        Index('idx_reviews_user', 'user_id'),
        Index('idx_reviews_rating', 'rating'),
        Index('idx_reviews_created', 'created_at'),
        CheckConstraint('rating >= 1 AND rating <= 5', name='guide_reviews_rating_check'),
    )

    def __repr__(self):
        return f"<GuideReview(id={self.id}, guide_id={self.guide_id}, rating={self.rating})>"


# ============================================================
# 攻略点赞模型
# ============================================================

class GuideLike(Base):
    """攻略点赞表"""
    __tablename__ = 'guide_likes'

    id = Column(Integer, primary_key=True)
    guide_id = Column(Integer, ForeignKey('travel_guides.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # 时间戳
    created_at = Column(DateTime(timezone=True), default=func.now())

    # 关系
    guide = relationship('TravelGuide', back_populates='likes')
    user = relationship('User', back_populates='likes')

    # 约束
    __table_args__ = (
        UniqueConstraint('guide_id', 'user_id', name='guide_likes_unique'),
        Index('idx_likes_guide', 'guide_id'),
        Index('idx_likes_user', 'user_id'),
    )

    def __repr__(self):
        return f"<GuideLike(guide_id={self.guide_id}, user_id={self.user_id})>"


# ============================================================
# 攻略分享模型
# ============================================================

class GuideShare(Base):
    """攻略分享表"""
    __tablename__ = 'guide_shares'

    id = Column(Integer, primary_key=True)
    guide_id = Column(Integer, ForeignKey('travel_guides.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))

    # 分享信息
    share_type = Column(String(20), nullable=False)
    share_title = Column(String(200))

    # 统计
    click_count = Column(Integer, default=0)

    # 时间戳
    created_at = Column(DateTime(timezone=True), default=func.now())

    # 关系
    guide = relationship('TravelGuide', back_populates='shares')

    # 索引
    __table_args__ = (
        Index('idx_shares_guide', 'guide_id'),
    )

    def __repr__(self):
        return f"<GuideShare(id={self.id}, share_type='{self.share_type}')>"


# ============================================================
# 攻略版本历史模型
# ============================================================

class GuideVersion(Base):
    """攻略版本历史表"""
    __tablename__ = 'guide_versions'

    id = Column(Integer, primary_key=True)
    guide_id = Column(Integer, ForeignKey('travel_guides.id', ondelete='CASCADE'), nullable=False)

    # 版本信息
    version_number = Column(Integer, nullable=False)
    change_description = Column(Text)

    # 快照数据
    snapshot = Column(JSONB, nullable=False)

    # 操作信息
    operated_by = Column(String(100))
    operated_at = Column(DateTime(timezone=True), default=func.now())

    # 关系
    guide = relationship('TravelGuide', back_populates='versions')

    # 索引
    __table_args__ = (
        UniqueConstraint('guide_id', 'version_number', name='guide_versions_unique'),
        Index('idx_versions_guide', 'guide_id'),
    )

    def __repr__(self):
        return f"<GuideVersion(guide_id={self.guide_id}, version={self.version_number})>"


# ============================================================
# 景点数据库模型
# ============================================================

class Attraction(Base):
    """景点数据库表"""
    __tablename__ = 'attractions_database'

    id = Column(Integer, primary_key=True)

    # 基本信息
    name = Column(String(200), nullable=False)
    name_en = Column(String(200))
    name_aliases = Column(PGArray(String), default=list)

    # 地理位置
    country = Column(String(50))
    city = Column(String(100))
    province = Column(String(100))
    address = Column(Text)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))

    # 分类标签
    category = Column(String(50))
    tags = Column(PGArray(String), default=list)
    interest_types = Column(PGArray(String), default=list)

    # 详细信息
    description = Column(Text)
    highlights = Column(PGArray(String), default=list)
    opening_hours = Column(JSONB)
    ticket_info = Column(JSONB)
    official_website = Column(String(500))

    # 媒体
    cover_image = Column(String(500))
    images = Column(PGArray(String), default=list)

    # 评分
    rating_avg = Column(Numeric(3, 2))
    review_count = Column(Integer, default=0)
    popularity_score = Column(Integer, default=0)

    # 实用信息
    recommended_duration = Column(String(50))
    best_time_to_visit = Column(String(100))
    tips = Column(PGArray(String), default=list)

    # 价格信息
    price_range = Column(String(50))
    ticket_price_min = Column(Integer)
    ticket_price_max = Column(Integer)

    # 交通信息
    nearby_subway = Column(PGArray(String), default=list)
    parking_info = Column(Text)

    # 联系信息
    phone = Column(String(50))
    email = Column(String(100))

    # 数据来源
    data_source = Column(String(50))
    source_id = Column(String(100))
    last_verified_at = Column(DateTime(timezone=True))

    # 时间戳
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # 索引
    __table_args__ = (
        Index('idx_attractions_city', 'city'),
        Index('idx_attractions_category', 'category'),
        Index('idx_attractions_rating', 'rating_avg'),
    )

    def __repr__(self):
        return f"<Attraction(id={self.id}, name='{self.name}', city='{self.city}')>"


# ============================================================
# 攻略模板模型
# ============================================================

class GuideTemplate(Base):
    """攻略模板表"""
    __tablename__ = 'guide_templates'

    id = Column(Integer, primary_key=True)

    # 基本信息
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # 模板类型
    template_type = Column(String(50))
    destination_type = Column(String(20))

    # 推荐天数
    min_days = Column(Integer)
    max_days = Column(Integer)

    # 预算范围
    budget_level = Column(PGArray(String), default=list)

    # 模板内容
    template_structure = Column(JSONB, nullable=False)
    prompts = Column(JSONB)

    # 样例数据
    example_destination = Column(String(100))
    example_output = Column(JSONB)

    # 使用统计
    usage_count = Column(Integer, default=0)

    # 状态
    is_active = Column(Boolean, default=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<GuideTemplate(id={self.id}, name='{self.name}')>"


# ============================================================
# 攻略推荐关系模型
# ============================================================

class GuideRecommendation(Base):
    """攻略推荐关系表"""
    __tablename__ = 'guide_recommendations'

    id = Column(Integer, primary_key=True)

    # 推荐关系
    source_guide_id = Column(Integer, ForeignKey('travel_guides.id'))
    target_guide_id = Column(Integer, ForeignKey('travel_guides.id'))

    # 推荐理由
    reason = Column(Text)
    similarity_score = Column(Numeric(3, 2))

    # 推荐类型
    recommendation_type = Column(String(50))
    position = Column(Integer)

    # 时间戳
    created_at = Column(DateTime(timezone=True), default=func.now())

    # 约束
    __table_args__ = (
        UniqueConstraint('source_guide_id', 'target_guide_id', 'recommendation_type',
                        name='guide_recommendations_unique'),
        Index('idx_recommendations_source', 'source_guide_id'),
        Index('idx_recommendations_target', 'target_guide_id'),
    )

    def __repr__(self):
        return f"<GuideRecommendation(source={self.source_guide_id}, target={self.target_guide_id})>"


# ============================================================
# 辅助函数
# ============================================================

def update_rating_counts(mapper, connection, target):
    """
    当评论变更时更新攻略的评分统计

    这个函数会在 GuideReview 变更时自动调用
    """
    if target.guide_id:
        from sqlalchemy import select, func as sql_func

        # 计算新的平均评分
        stmt = select(
            sql_func.avg(GuideReview.rating).label('avg_rating'),
            sql_func.count(GuideReview.id).label('count')
        ).where(
            GuideReview.guide_id == target.guide_id,
            GuideReview.is_visible == True
        )

        result = connection.execute(stmt).fetchone()
        if result and result.count > 0:
            connection.execute(
                f"""
                UPDATE travel_guides
                SET rating_avg = {result.avg_rating},
                    rating_count = {result.count}
                WHERE id = {target.guide_id}
                """
            )


# 注册事件监听器
event.listen(GuideReview, 'after_insert', update_rating_counts)
event.listen(GuideReview, 'after_update', update_rating_counts)
event.listen(GuideReview, 'after_delete', update_rating_counts)


# ============================================================
# 导出列表
# ============================================================

__all__ = [
    'Base',
    'User',
    'TravelGuide',
    'UserBookmark',
    'GuideReview',
    'GuideLike',
    'GuideShare',
    'GuideVersion',
    'Attraction',
    'GuideTemplate',
    'GuideRecommendation',
]
