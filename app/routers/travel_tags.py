"""
旅行标签管理 API路由

提供旅行相关的标签管理功能：
- 攻略标签（亲子、蜜月、美食等）
- 目的地标签
- 兴趣标签
- 自定义标签
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from app.db.travel_db import get_db, DatabaseManager
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/travel/tags", tags=["旅行标签管理"])


# ============================================================
# 数据模型
# ============================================================

class TagCreate(BaseModel):
    """创建标签请求"""
    name: str = Field(..., min_length=1, max_length=30, description="标签名称")
    tag_type: str = Field(..., description="标签类型: guide/destination/interest/custom")
    color: str = Field(default="#409EFF", max_length=20, description="标签颜色")
    icon: Optional[str] = Field(None, max_length=50, description="标签图标")
    description: Optional[str] = Field(None, max_length=200, description="标签描述")
    sort_order: int = Field(default=0, description="排序顺序")


class TagUpdate(BaseModel):
    """更新标签请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=30)
    color: Optional[str] = Field(None, max_length=20)
    icon: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    sort_order: Optional[int] = None


class TagResponse(BaseModel):
    """标签响应"""
    id: int
    name: str
    tag_type: str
    color: str
    icon: Optional[str]
    description: Optional[str]
    sort_order: int
    use_count: int
    created_at: str
    updated_at: str


class TagListResponse(BaseModel):
    """标签列表响应"""
    tags: List[TagResponse]
    total: int


# ============================================================
# 数据库模型 (内联定义，避免循环导入)
# ============================================================

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TravelTag(Base):
    """旅行标签表"""
    __tablename__ = 'travel_tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    tag_type = Column(String(20), nullable=False, default='custom')  # guide/destination/interest/custom
    color = Column(String(20), default='#409EFF')
    icon = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)
    use_count = Column(Integer, default=0)  # 使用次数统计
    user_id = Column(Integer, nullable=True)  # None表示系统标签
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================
# 辅助函数
# ============================================================

def ensure_tags_table(db: Session):
    """确保标签表存在"""
    from sqlalchemy import inspect
    from app.db.travel_db import DatabaseManager

    # 获取引擎
    db_manager = DatabaseManager()
    if db_manager._engine:
        inspector = inspect(db_manager._engine)
        if 'travel_tags' not in inspector.get_table_names():
            TravelTag.__table__.create(db_manager._engine)
            logger.info("创建 travel_tags 表")
    else:
        # 如果没有引擎，尝试从session获取
        if hasattr(db, 'bind') and db.bind:
            inspector = inspect(db.bind)
            if 'travel_tags' not in inspector.get_table_names():
                TravelTag.__table__.create(db.bind)
                logger.info("创建 travel_tags 表")


def init_default_tags(db: Session):
    """初始化默认标签"""
    default_tags = [
        # 攻略类型标签
        {"name": "亲子游", "tag_type": "guide", "color": "#67C23A", "icon": "👨‍👩‍👧‍👦", "sort_order": 1},
        {"name": "蜜月旅行", "tag_type": "guide", "color": "#F56C6C", "icon": "💕", "sort_order": 2},
        {"name": "独自旅行", "tag_type": "guide", "color": "#909399", "icon": "🧳", "sort_order": 3},
        {"name": "商务旅行", "tag_type": "guide", "color": "#409EFF", "icon": "💼", "sort_order": 4},
        {"name": "毕业旅行", "tag_type": "guide", "color": "#E6A23C", "icon": "🎓", "sort_order": 5},

        # 兴趣标签
        {"name": "自然风光", "tag_type": "interest", "color": "#67C23A", "icon": "🏔️", "sort_order": 1},
        {"name": "历史文化", "tag_type": "interest", "color": "#E6A23C", "icon": "🏛️", "sort_order": 2},
        {"name": "美食探索", "tag_type": "interest", "color": "#F56C6C", "icon": "🍜", "sort_order": 3},
        {"name": "艺术文化", "tag_type": "interest", "color": "#909399", "icon": "🎨", "sort_order": 4},
        {"name": "户外运动", "tag_type": "interest", "color": "#409EFF", "icon": "🏃", "sort_order": 5},
        {"name": "购物血拼", "tag_type": "interest", "color": "#F56C6C", "icon": "🛍️", "sort_order": 6},
        {"name": "摄影打卡", "tag_type": "interest", "color": "#E6A23C", "icon": "📷", "sort_order": 7},

        # 季节标签
        {"name": "春季赏花", "tag_type": "guide", "color": "#67C23A", "icon": "🌸", "sort_order": 10},
        {"name": "夏季避暑", "tag_type": "guide", "color": "#409EFF", "icon": "🏖️", "sort_order": 11},
        {"name": "秋季赏叶", "tag_type": "guide", "color": "#E6A23C", "icon": "🍁", "sort_order": 12},
        {"name": "冬季雪景", "tag_type": "guide", "color": "#909399", "icon": "❄️", "sort_order": 13},
    ]

    for tag_data in default_tags:
        existing = db.query(TravelTag).filter(TravelTag.name == tag_data["name"]).first()
        if not existing:
            tag = TravelTag(**tag_data, user_id=None)  # 系统标签
            db.add(tag)

    db.commit()
    logger.info(f"初始化默认标签: {len(default_tags)}个")


# ============================================================
# API端点
# ============================================================

@router.get("/", response_model=TagListResponse)
async def list_tags(
    tag_type: Optional[str] = None,
    include_system: bool = True,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取标签列表

    参数：
    - tag_type: 按类型筛选 (guide/destination/interest/custom)
    - include_system: 是否包含系统标签
    - user_id: 用户ID，用于获取用户自定义标签
    """
    ensure_tags_table(db)

    # 初始化默认标签
    init_default_tags(db)

    query = db.query(TravelTag)

    # 类型筛选
    if tag_type:
        query = query.filter(TravelTag.tag_type == tag_type)

    # 系统标签筛选
    if not include_system:
        query = query.filter(TravelTag.user_id is not None)

    # 用户筛选
    if user_id is not None:
        query = query.filter(TravelTag.user_id == user_id)

    tags = query.order_by(TravelTag.sort_order, TravelTag.created_at).all()

    return TagListResponse(
        tags=[
            TagResponse(
                id=tag.id,
                name=tag.name,
                tag_type=tag.tag_type,
                color=tag.color,
                icon=tag.icon,
                description=tag.description,
                sort_order=tag.sort_order,
                use_count=tag.use_count or 0,
                created_at=tag.created_at.isoformat() if tag.created_at else "",
                updated_at=tag.updated_at.isoformat() if tag.updated_at else ""
            )
            for tag in tags
        ],
        total=len(tags)
    )


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    user_id: int = 1,  # TODO: 从JWT获取
    db: Session = Depends(get_db)
):
    """
    创建自定义标签
    """
    ensure_tags_table(db)

    # 检查名称是否重复
    existing = db.query(TravelTag).filter(TravelTag.name == tag_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"标签名称 '{tag_data.name}' 已存在"
        )

    # 创建标签
    tag = TravelTag(
        name=tag_data.name,
        tag_type=tag_data.tag_type,
        color=tag_data.color,
        icon=tag_data.icon,
        description=tag_data.description,
        sort_order=tag_data.sort_order,
        user_id=user_id
    )

    db.add(tag)
    db.commit()
    db.refresh(tag)

    logger.info(f"创建标签: {tag.name} (用户: {user_id})")

    return TagResponse(
        id=tag.id,
        name=tag.name,
        tag_type=tag.tag_type,
        color=tag.color,
        icon=tag.icon,
        description=tag.description,
        sort_order=tag.sort_order,
        use_count=tag.use_count or 0,
        created_at=tag.created_at.isoformat() if tag.created_at else "",
        updated_at=tag.updated_at.isoformat() if tag.updated_at else ""
    )


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    user_id: int = 1,  # TODO: 从JWT获取
    db: Session = Depends(get_db)
):
    """
    更新标签
    """
    ensure_tags_table(db)

    tag = db.query(TravelTag).filter(TravelTag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"标签不存在: {tag_id}"
        )

    # 检查权限（只能编辑自己的标签）
    if tag.user_id != user_id and tag.user_id is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限编辑此标签"
        )

    # 系统标签不允许修改某些字段
    if tag.user_id is None:
        if tag_data.name and tag_data.name != tag.name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="系统标签不允许修改名称"
            )

    # 更新字段
    if tag_data.name is not None:
        tag.name = tag_data.name
    if tag_data.color is not None:
        tag.color = tag_data.color
    if tag_data.icon is not None:
        tag.icon = tag_data.icon
    if tag_data.description is not None:
        tag.description = tag_data.description
    if tag_data.sort_order is not None:
        tag.sort_order = tag_data.sort_order

    tag.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(tag)

    return TagResponse(
        id=tag.id,
        name=tag.name,
        tag_type=tag.tag_type,
        color=tag.color,
        icon=tag.icon,
        description=tag.description,
        sort_order=tag.sort_order,
        use_count=tag.use_count or 0,
        created_at=tag.created_at.isoformat() if tag.created_at else "",
        updated_at=tag.updated_at.isoformat() if tag.updated_at else ""
    )


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: int,
    user_id: int = 1,  # TODO: 从JWT获取
    db: Session = Depends(get_db)
):
    """
    删除标签
    """
    ensure_tags_table(db)

    tag = db.query(TravelTag).filter(TravelTag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"标签不存在: {tag_id}"
        )

    # 检查权限
    if tag.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能删除自己的标签"
        )

    db.delete(tag)
    db.commit()

    logger.info(f"删除标签: {tag.name} (ID: {tag_id})")

    return {"success": True, "message": "标签已删除"}


@router.get("/stats")
async def get_tag_stats(db: Session = Depends(get_db)):
    """
    获取标签统计信息
    """
    ensure_tags_table(db)

    # 按类型统计
    type_stats = db.query(
        TravelTag.tag_type,
        db.func.count(TravelTag.id)
    ).group_by(TravelTag.tag_type).all()

    # 最常用标签
    popular_tags = db.query(TravelTag).order_by(
        TravelTag.use_count.desc()
    ).limit(10).all()

    return {
        "type_stats": {tag_type: count for tag_type, count in type_stats},
        "popular_tags": [
            {
                "id": tag.id,
                "name": tag.name,
                "use_count": tag.use_count or 0
            }
            for tag in popular_tags
        ],
        "total_tags": db.query(TravelTag).count()
    }


@router.post("/{tag_id}/use")
async def increment_tag_use(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """
    增加标签使用次数
    """
    ensure_tags_table(db)

    tag = db.query(TravelTag).filter(TravelTag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"标签不存在: {tag_id}"
        )

    tag.use_count = (tag.use_count or 0) + 1
    db.commit()

    return {"success": True, "use_count": tag.use_count}
