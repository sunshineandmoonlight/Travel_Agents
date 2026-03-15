"""
旅行规划系统 API

提供旅行攻略的完整功能：
- AI 生成旅行规划
- 攻略 CRUD 操作
- 收藏、点赞、评论、分享
- 攻略搜索和推荐
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks, Response
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from pydantic import BaseModel, Field

from app.db.travel_db import get_db
from app.models.travel import (
    User, TravelGuide, UserBookmark, GuideReview,
    GuideLike, GuideShare, GuideVersion, Attraction
)
from app.schemas.travel_schemas import (
    # 请求模型
    TravelPlanRequest,
    TravelGuideCreate,
    TravelGuideUpdate,
    BookmarkCreate,
    ReviewCreate,
    ReviewUpdate,
    LikeCreate,
    ShareCreate,
    GuideSearchQuery,
    # 响应模型
    TravelPlanResponse,
    TravelGuideResponse,
    TravelGuideListResponse,
    BookmarkResponse,
    ReviewResponse,
    LikeStatusResponse,
    ShareResponse,
    GuideSearchResponse,
    MessageResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/travel", tags=["travel"])


# ============================================================
# 辅助函数
# ============================================================

def get_current_user_id(user_id: Optional[int] = None) -> int:
    """获取当前用户ID（简化版，实际应从JWT token获取）"""
    # TODO: 实现真实的用户认证
    return user_id or 1


def slugify(title: str) -> str:
    """生成URL友好的slug"""
    import re
    # 转换为小写，替换空格和特殊字符
    slug = re.sub(r'[^\w\u4e00-\u9fff]+', '-', title.lower())
    slug = slug.strip('-')
    return slug


# ============================================================
# 旅行规划 API
# ============================================================

@router.post("/plan", response_model=TravelPlanResponse)
async def create_travel_plan(
    request: TravelPlanRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    AI 生成旅行规划

    根据用户输入的目的地、天数、预算等信息，使用多Agent系统生成详细的旅行规划。

    参数：
    - destination: 目的地
    - days: 天数
    - budget: 预算级别 (low/medium/high)
    - travelers: 人数
    - interest_type: 兴趣类型（历史、美食、自然等）
    - selected_style: 选择的风格
    - save_as_guide: 是否保存为攻略
    - guide_title: 攻略标题
    """
    logger.info(f"[旅行规划] 开始规划: {request.destination}, {request.days}天")

    try:
        # 调用旅行规划图
        from tradingagents.graph.travel_graph_with_llm import create_travel_graph_with_llm

        graph = create_travel_graph_with_llm(
            llm_provider="deepseek",
            llm_model="deepseek-chat"
        )

        # 生成旅行规划
        result = graph.plan(
            destination=request.destination,
            days=request.days,
            budget=request.budget,
            travelers=request.travelers,
            interest_type=request.interest_type or "",
            selected_style=request.selected_style or ""
        )

        # 获取目的地情报（新增）
        destination_intelligence = None
        try:
            from tradingagents.agents.analysts.destination_intelligence import analyze_destination
            import os

            # 检查是否启用目的地情报（默认启用）
            enable_intelligence = os.getenv("ENABLE_DESTINATION_INTELLIGENCE", "true").lower() == "true"

            if enable_intelligence:
                logger.info(f"[旅行规划] 正在获取 {request.destination} 的目的地情报...")

                # 计算旅行日期（默认使用7天后）
                from datetime import datetime, timedelta
                travel_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

                intelligence = await analyze_destination(request.destination, travel_date)

                # 提取关键情报信息
                destination_intelligence = {
                    "risk_level": intelligence.get("risk_assessment", {}).get("risk_level", 1),
                    "risk_text": intelligence.get("risk_assessment", {}).get("overall_risk_text", ""),
                    "risk_recommendation": intelligence.get("risk_assessment", {}).get("recommendation", ""),
                    "news_count": len(intelligence.get("news", [])),
                    "latest_news": intelligence.get("news", [])[:3],  # 最多3条最新新闻
                    "events": intelligence.get("events", [])[:5],  # 最多5个活动
                    "recommendations": intelligence.get("recommendations", [])[:5],  # 最多5条建议
                    "generated_at": intelligence.get("generated_at")
                }

                logger.info(f"[旅行规划] 目的地情报获取完成 - 风险等级: {destination_intelligence['risk_level']}/5")

        except ImportError as e:
            logger.warning(f"[旅行规划] 目的地情报智能体不可用: {e}")
        except Exception as e:
            logger.error(f"[旅行规划] 获取目的地情报失败: {e}")

        # 构建响应数据
        plan_data = {
            "destination": result.get("destination"),
            "destination_type": result.get("destination_type"),
            "days": request.days,
            "budget": request.budget,
            "travelers": request.travelers,
            "travel_style": request.selected_style or "exploration",
            "interest_tags": [request.interest_type] if request.interest_type else [],
            "itinerary": result.get("detailed_itinerary", {}),
            "budget_breakdown": result.get("budget_breakdown", {}),
            "attractions": result.get("attractions", {}).get("recommended", []),
            "weather_forecast": result.get("weather_forecast", {}),
            "transport_info": result.get("transport_info", {}),
            "destination_intelligence": destination_intelligence  # 新增：目的地情报
        }

        # 如果需要保存为攻略
        guide_id = None
        guide_uuid = None

        if request.save_as_guide:
            guide = TravelGuide(
                title=request.guide_title or f"{request.destination}{request.days}日游",
                description=f"AI生成的{request.destination}{request.days}天旅行规划",
                destination=request.destination,
                destination_type=result.get("destination_type", "domestic"),
                days=request.days,
                budget_level=request.budget,
                total_budget=plan_data["budget_breakdown"].get("total_budget"),
                travelers_count=request.travelers,
                travel_style=request.selected_style,
                interest_tags=plan_data["interest_tags"],
                itinerary=plan_data["itinerary"],
                budget_breakdown=plan_data["budget_breakdown"],
                attractions=plan_data["attractions"],
                generation_method="ai",
                generation_config={
                    "llm_provider": "deepseek",
                    "interest_type": request.interest_type
                },
                user_id=current_user_id,
                username=f"user_{current_user_id}",
                status="draft"
            )

            db.add(guide)
            db.commit()
            db.refresh(guide)

            guide_id = guide.id
            guide_uuid = guide.uuid

            logger.info(f"[旅行规划] 攻略已保存: ID={guide_id}")

        return TravelPlanResponse(
            success=True,
            message="旅行规划生成成功",
            data=plan_data,
            guide_id=guide_id,
            guide_uuid=guide_uuid
        )

    except Exception as e:
        logger.error(f"[旅行规划] 生成失败: {e}")
        return TravelPlanResponse(
            success=False,
            message=f"生成失败: {str(e)}",
            data=None
        )


# ============================================================
# 攻略 CRUD API
# ============================================================

@router.get("/guides", response_model=GuideSearchResponse)
async def get_guides(
    destination: Optional[str] = Query(None, description="目的地筛选"),
    destination_type: Optional[str] = Query(None, description="类型: domestic/international"),
    days_min: Optional[int] = Query(None, ge=1, description="最小天数"),
    days_max: Optional[int] = Query(None, le=30, description="最大天数"),
    budget_level: Optional[str] = Query(None, description="预算级别"),
    travel_style: Optional[str] = Query(None, description="旅行风格"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取攻略列表

    支持按目的地、天数、预算、风格等条件筛选和排序
    """
    # 构建查询
    query = db.query(TravelGuide).filter(TravelGuide.status == "published")

    # 应用筛选条件
    if destination:
        query = query.filter(TravelGuide.destination.ilike(f"%{destination}%"))
    if destination_type:
        query = query.filter(TravelGuide.destination_type == destination_type)
    if days_min:
        query = query.filter(TravelGuide.days >= days_min)
    if days_max:
        query = query.filter(TravelGuide.days <= days_max)
    if budget_level:
        query = query.filter(TravelGuide.budget_level == budget_level)
    if travel_style:
        query = query.filter(TravelGuide.travel_style == travel_style)

    # 排序
    order_column = getattr(TravelGuide, sort_by, TravelGuide.created_at)
    if sort_order == "desc":
        query = query.order_by(desc(order_column))
    else:
        query = query.order_by(order_column)

    # 分页
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    return GuideSearchResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=[TravelGuideListResponse.model_validate(g) for g in items]
    )


@router.get("/guides/{guide_id}", response_model=TravelGuideResponse)
async def get_guide(
    guide_id: int,
    db: Session = Depends(get_db)
):
    """获取攻略详情"""
    guide = db.query(TravelGuide).filter(TravelGuide.id == guide_id).first()

    if not guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="攻略不存在"
        )

    # 增加浏览量
    guide.view_count += 1
    db.commit()

    return TravelGuideResponse.model_validate(guide)


@router.get("/guides/uuid/{guide_uuid}", response_model=TravelGuideResponse)
async def get_guide_by_uuid(
    guide_uuid: str,
    db: Session = Depends(get_db)
):
    """通过UUID获取攻略详情"""
    try:
        guide_uuid_parsed = uuid.UUID(guide_uuid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的UUID格式"
        )

    guide = db.query(TravelGuide).filter(TravelGuide.uuid == guide_uuid_parsed).first()

    if not guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="攻略不存在"
        )

    # 增加浏览量
    guide.view_count += 1
    db.commit()

    return TravelGuideResponse.model_validate(guide)


@router.post("/guides", response_model=TravelGuideResponse, status_code=status.HTTP_201_CREATED)
async def create_guide(
    guide_data: TravelGuideCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """创建新攻略"""
    # 生成 slug
    slug = slugify(guide_data.title)

    # 检查 slug 是否已存在
    existing = db.query(TravelGuide).filter(TravelGuide.slug == slug).first()
    if existing:
        slug = f"{slug}-{uuid.uuid4().hex[:8]}"

    guide = TravelGuide(
        **guide_data.model_dump(),
        slug=slug,
        user_id=current_user_id,
        username=f"user_{current_user_id}",
        status="draft"
    )

    db.add(guide)
    db.commit()
    db.refresh(guide)

    return TravelGuideResponse.model_validate(guide)


@router.put("/guides/{guide_id}", response_model=TravelGuideResponse)
async def update_guide(
    guide_id: int,
    guide_data: TravelGuideUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """更新攻略"""
    guide = db.query(TravelGuide).filter(TravelGuide.id == guide_id).first()

    if not guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="攻略不存在"
        )

    # 检查权限
    if guide.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限修改此攻略"
        )

    # 更新字段
    update_data = guide_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(guide, field, value)

    # 保存版本历史
    if guide.status == "published":
        version = GuideVersion(
            guide_id=guide.id,
            version_number=1,  # TODO: 实际应查询当前最大版本号+1
            snapshot=guide_data.model_dump(),
            operated_by=f"user_{current_user_id}"
        )
        db.add(version)

    db.commit()
    db.refresh(guide)

    return TravelGuideResponse.model_validate(guide)


@router.post("/guides/{guide_id}/publish", response_model=TravelGuideResponse)
async def publish_guide(
    guide_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """发布攻略"""
    guide = db.query(TravelGuide).filter(TravelGuide.id == guide_id).first()

    if not guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="攻略不存在"
        )

    if guide.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限发布此攻略"
        )

    guide.status = "published"
    guide.published_at = datetime.utcnow()

    # 生成 slug（如果还没有）
    if not guide.slug:
        guide.slug = slugify(guide.title)

    db.commit()
    db.refresh(guide)

    return TravelGuideResponse.model_validate(guide)


@router.delete("/guides/{guide_id}", response_model=MessageResponse)
async def delete_guide(
    guide_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """删除攻略"""
    guide = db.query(TravelGuide).filter(TravelGuide.id == guide_id).first()

    if not guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="攻略不存在"
        )

    if guide.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除此攻略"
        )

    db.delete(guide)
    db.commit()

    return MessageResponse(success=True, message="攻略已删除")


# ============================================================
# 收藏 API
# ============================================================

@router.post("/guides/{guide_id}/bookmark", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    guide_id: int,
    bookmark_data: Optional[BookmarkCreate] = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """收藏攻略"""
    # 检查攻略是否存在
    guide = db.query(TravelGuide).filter(TravelGuide.id == guide_id).first()
    if not guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="攻略不存在"
        )

    # 检查是否已收藏
    existing = db.query(UserBookmark).filter(
        and_(UserBookmark.user_id == current_user_id, UserBookmark.guide_id == guide_id)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已收藏此攻略"
        )

    # 创建收藏
    bookmark = UserBookmark(
        user_id=current_user_id,
        guide_id=guide_id,
        notes=bookmark_data.notes if bookmark_data else None,
        folder_name=bookmark_data.folder_name if bookmark_data else "默认收藏夹"
    )

    db.add(bookmark)

    # 更新收藏计数
    guide.bookmark_count += 1

    db.commit()
    db.refresh(bookmark)

    return BookmarkResponse(
        id=bookmark.id,
        user_id=bookmark.user_id,
        guide_id=bookmark.guide_id,
        notes=bookmark.notes,
        folder_name=bookmark.folder_name,
        created_at=bookmark.created_at,
        guide_title=guide.title,
        guide_destination=guide.destination
    )


@router.delete("/guides/{guide_id}/bookmark", response_model=MessageResponse)
async def delete_bookmark(
    guide_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """取消收藏"""
    bookmark = db.query(UserBookmark).filter(
        and_(UserBookmark.user_id == current_user_id, UserBookmark.guide_id == guide_id)
    ).first()

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未收藏此攻略"
        )

    # 更新收藏计数
    guide = db.query(TravelGuide).filter(TravelGuide.id == guide_id).first()
    if guide:
        guide.bookmark_count = max(0, guide.bookmark_count - 1)

    db.delete(bookmark)
    db.commit()

    return MessageResponse(success=True, message="取消收藏成功")


@router.get("/bookmarks", response_model=List[BookmarkResponse])
async def get_bookmarks(
    folder_name: Optional[str] = Query(None, description="收藏夹名称"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取收藏列表"""
    query = db.query(UserBookmark).filter(UserBookmark.user_id == current_user_id)

    if folder_name:
        query = query.filter(UserBookmark.folder_name == folder_name)

    bookmarks = query.order_by(desc(UserBookmark.created_at)).all()

    # 获取关联的攻略信息
    result = []
    for bookmark in bookmarks:
        guide = db.query(TravelGuide).filter(TravelGuide.id == bookmark.guide_id).first()
        result.append(BookmarkResponse(
            id=bookmark.id,
            user_id=bookmark.user_id,
            guide_id=bookmark.guide_id,
            notes=bookmark.notes,
            folder_name=bookmark.folder_name,
            created_at=bookmark.created_at,
            guide_title=guide.title if guide else None,
            guide_destination=guide.destination if guide else None
        ))

    return result


# ============================================================
# 点赞 API
# ============================================================

@router.post("/guides/{guide_id}/like", response_model=LikeStatusResponse)
async def like_guide(
    guide_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """点赞攻略"""
    # 检查攻略是否存在
    guide = db.query(TravelGuide).filter(TravelGuide.id == guide_id).first()
    if not guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="攻略不存在"
        )

    # 检查是否已点赞
    existing = db.query(GuideLike).filter(
        and_(GuideLike.user_id == current_user_id, GuideLike.guide_id == guide_id)
    ).first()

    if existing:
        # 取消点赞
        db.delete(existing)
        guide.like_count = max(0, guide.like_count - 1)
        db.commit()

        return LikeStatusResponse(is_liked=False, like_count=guide.like_count)
    else:
        # 添加点赞
        like = GuideLike(user_id=current_user_id, guide_id=guide_id)
        db.add(like)
        guide.like_count += 1
        db.commit()

        return LikeStatusResponse(is_liked=True, like_count=guide.like_count)


@router.get("/guides/{guide_id}/like/status", response_model=LikeStatusResponse)
async def get_like_status(
    guide_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取点赞状态"""
    guide = db.query(TravelGuide).filter(TravelGuide.id == guide_id).first()
    if not guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="攻略不存在"
        )

    like = db.query(GuideLike).filter(
        and_(GuideLike.user_id == current_user_id, GuideLike.guide_id == guide_id)
    ).first()

    return LikeStatusResponse(
        is_liked=like is not None,
        like_count=guide.like_count
    )


@router.post("/guides/{guide_id}/copy", response_model=TravelGuideResponse)
async def copy_guide(
    guide_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    复制攻略

    创建一个现有攻略的副本，包括所有内容和数据。
    用户可以对副本进行编辑而不影响原攻略。
    """
    # 获取原攻略
    original_guide = db.query(TravelGuide).filter(TravelGuide.id == guide_id).first()

    if not original_guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="攻略不存在"
        )

    # 检查权限（可以复制任何已发布的攻略，或者自己的草稿）
    if original_guide.user_id != current_user_id and original_guide.status != 'published':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限复制此攻略"
        )

    # 生成新的唯一slug
    base_slug = f"{original_guide.slug}-copy" if original_guide.slug else slugify(f"{original_guide.title}-copy")
    unique_slug = base_slug
    counter = 1
    while db.query(TravelGuide).filter(TravelGuide.slug == unique_slug).first():
        unique_slug = f"{base_slug}-{counter}"
        counter += 1

    # 创建副本
    copied_guide = TravelGuide(
        title=f"{original_guide.title} (副本)",
        description=original_guide.description,

        # 目的地信息
        destination=original_guide.destination,
        destination_type=original_guide.destination_type,
        city_code=original_guide.city_code,
        country_code=original_guide.country_code,

        # 行程信息
        days=original_guide.days,
        budget_level=original_guide.budget_level,
        total_budget=original_guide.total_budget,
        travelers_count=original_guide.travelers_count,
        travel_style=original_guide.travel_style,
        interest_tags=original_guide.interest_tags,

        # 详细内容（深拷贝）
        itinerary=original_guide.itinerary.copy() if original_guide.itinerary else {},
        budget_breakdown=original_guide.budget_breakdown.copy() if original_guide.budget_breakdown else {},
        attractions=original_guide.attractions.copy() if original_guide.attractions else [],
        accommodation=original_guide.accommodation.copy() if original_guide.accommodation else None,
        transportation=original_guide.transportation.copy() if original_guide.transportation else None,

        # 媒体资源
        cover_image=original_guide.cover_image,
        images=original_guide.images.copy() if original_guide.images else [],

        # 生成信息
        generation_method="copy",
        generation_config={
            "original_guide_id": guide_id,
            "original_title": original_guide.title,
            "original_author": original_guide.username,
            "copied_at": datetime.utcnow().isoformat()
        },

        # 统计信息重置
        view_count=0,
        like_count=0,
        bookmark_count=0,
        copy_count=0,
        rating_avg=0,
        rating_count=0,

        # 状态
        status="draft",
        is_featured=False,
        is_editor_pick=False,

        # SEO
        slug=unique_slug,
        keywords=original_guide.keywords,
        meta_description=original_guide.meta_description,

        # 作者信息
        user_id=current_user_id,
        username=f"user_{current_user_id}",

        # 季节性信息
        best_seasons=original_guide.best_seasons.copy() if original_guide.best_seasons else [],
        weather_info=original_guide.weather_info.copy() if original_guide.weather_info else None,

        # 标签和分类
        tags=original_guide.tags.copy() if original_guide.tags else [],
        category=original_guide.category,

        # 地理位置
        geo_latitude=original_guide.geo_latitude,
        geo_longitude=original_guide.geo_longitude
    )

    db.add(copied_guide)
    db.commit()
    db.refresh(copied_guide)

    # 增加原攻略的复制计数
    original_guide.copy_count = (original_guide.copy_count or 0) + 1

    # 保存版本历史（如果是复制的攻略被再次复制）
    version = GuideVersion(
        guide_id=copied_guide.id,
        version_number=1,
        change_description=f"复制自攻略: {original_guide.title} (ID: {guide_id})",
        snapshot={
            "source_guide_id": guide_id,
            "source_title": original_guide.title
        },
        operated_by=f"user_{current_user_id}"
    )
    db.add(version)

    db.commit()

    logger.info(f"[复制攻略] 用户{current_user_id}复制攻略 {guide_id} -> {copied_guide.id}")

    return TravelGuideResponse.model_validate(copied_guide)


@router.get("/guides/{guide_id}/export")
async def export_guide_to_pdf(
    guide_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    导出攻略为PDF

    将攻略导出为精美的PDF文件，适合打印和分享。
    PDF包含完整的攻略信息：标题、目的地、行程、预算、景点推荐等。
    """
    from app.utils.pdf_generator import get_pdf_generator

    # 获取攻略
    guide = db.query(TravelGuide).filter(TravelGuide.id == guide_id).first()

    if not guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="攻略不存在"
        )

    # 构建攻略数据字典
    guide_dict = {
        "id": guide.id,
        "uuid": str(guide.uuid) if guide.uuid else "",
        "title": guide.title,
        "description": guide.description or "",
        "destination": guide.destination,
        "destination_type": guide.destination_type or "",
        "days": guide.days,
        "budget_level": guide.budget_level or "",
        "travel_style": guide.travel_style or "",
        "travelers_count": guide.travelers_count or 2,
        "cover_image": guide.cover_image or "",
        "interest_tags": guide.interest_tags or [],
        "itinerary": guide.itinerary or {},
        "budget_breakdown": guide.budget_breakdown or {},
        "attractions": guide.attractions or [],
        "accommodation": guide.accommodation or {},
        "transportation": guide.transportation or {},
        "best_seasons": guide.best_seasons or [],
        "weather_info": guide.weather_info or {},
        "created_at": guide.created_at.isoformat() if guide.created_at else "",
        "username": guide.username or "",
        "rating_avg": guide.rating_avg or 0,
        "rating_count": guide.rating_count or 0,
        "view_count": guide.view_count or 0
    }

    # 作者信息
    author_info = {
        "username": guide.username or "",
        "user_id": guide.user_id
    }

    try:
        # 生成PDF
        generator = get_pdf_generator()
        pdf_bytes = generator.generate_pdf(guide_dict, author_info)

        # 生成安全的文件名
        safe_title = guide.title.replace(" ", "_").replace("/", "-")
        filename = f"{safe_title}.pdf"

        # 更新导出统计
        # 可以在表中添加 export_count 字段来追踪

        logger.info(f"[导出PDF] 用户{current_user_id}导出攻略 {guide_id}")

        # 返回PDF文件
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}",
                "Content-Length": str(len(pdf_bytes)),
                "X-Guide-ID": str(guide_id),
                "X-Export-Time": datetime.utcnow().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"[导出PDF] 失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF生成失败: {str(e)}"
        )


# ============================================================
# 评论 API
# ============================================================

@router.post("/guides/{guide_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    guide_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """创建评论"""
    # 检查攻略是否存在
    guide = db.query(TravelGuide).filter(TravelGuide.id == guide_id).first()
    if not guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="攻略不存在"
        )

    # 检查是否已评论
    existing = db.query(GuideReview).filter(
        and_(GuideReview.user_id == current_user_id, GuideReview.guide_id == guide_id)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已评论过此攻略"
        )

    # 创建评论
    review = GuideReview(
        guide_id=guide_id,
        user_id=current_user_id,
        rating=review_data.rating,
        title=review_data.title,
        content=review_data.content,
        images=review_data.images or []
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return ReviewResponse.model_validate(review)


@router.get("/guides/{guide_id}/reviews", response_model=List[ReviewResponse])
async def get_reviews(
    guide_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """获取攻略评论列表"""
    # 检查攻略是否存在
    guide = db.query(TravelGuide).filter(TravelGuide.id == guide_id).first()
    if not guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="攻略不存在"
        )

    # 获取评论
    query = db.query(GuideReview).filter(
        and_(GuideReview.guide_id == guide_id, GuideReview.is_visible == True)
    ).order_by(desc(GuideReview.created_at))

    offset = (page - 1) * page_size
    reviews = query.offset(offset).limit(page_size).all()

    return [ReviewResponse.model_validate(r) for r in reviews]


# ============================================================
# 分享 API
# ============================================================

@router.post("/guides/{guide_id}/share", response_model=ShareResponse, status_code=status.HTTP_201_CREATED)
async def create_share(
    guide_id: int,
    share_data: ShareCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """创建分享记录"""
    # 检查攻略是否存在
    guide = db.query(TravelGuide).filter(TravelGuide.id == guide_id).first()
    if not guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="攻略不存在"
        )

    # 创建分享记录
    share = GuideShare(
        guide_id=guide_id,
        user_id=current_user_id,
        share_type=share_data.share_type,
        share_title=share_data.share_title
    )

    db.add(share)
    db.commit()
    db.refresh(share)

    return ShareResponse.model_validate(share)


# ============================================================
# 搜索 API
# ============================================================

@router.get("/guides/search/fulltext", response_model=GuideSearchResponse)
async def search_guides_fulltext(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    全文搜索攻略

    使用 PostgreSQL 全文搜索功能搜索攻略标题和描述
    """
    # 使用全文搜索
    query = db.query(TravelGuide).filter(
        and_(
            TravelGuide.status == "published",
            or_(
                TravelGuide.title.ilike(f"%{keyword}%"),
                TravelGuide.description.ilike(f"%{keyword}%"),
                TravelGuide.destination.ilike(f"%{keyword}%")
            )
        )
    ).order_by(desc(TravelGuide.created_at))

    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    return GuideSearchResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=[TravelGuideListResponse.model_validate(g) for g in items]
    )


# ============================================================
# 推荐 API
# ============================================================

@router.get("/guides/{guide_id}/recommendations", response_model=List[TravelGuideListResponse])
async def get_guide_recommendations(
    guide_id: int,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    获取相似攻略推荐

    基于目的地、天数、预算等条件推荐相似攻略
    """
    guide = db.query(TravelGuide).filter(TravelGuide.id == guide_id).first()
    if not guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="攻略不存在"
        )

    # 查找相似攻略
    query = db.query(TravelGuide).filter(
        and_(
            TravelGuide.id != guide_id,
            TravelGuide.status == "published",
            or_(
                TravelGuide.destination == guide.destination,
                TravelGuide.days == guide.days,
                TravelGuide.budget_level == guide.budget_level
            )
        )
    ).order_by(desc(TravelGuide.rating_avg))

    recommendations = query.limit(limit).all()

    return [TravelGuideListResponse.model_validate(g) for g in recommendations]


# ============================================================
# 统计 API
# ============================================================

@router.get("/stats", response_model=Dict[str, Any])
async def get_travel_stats(db: Session = Depends(get_db)):
    """获取旅行系统统计数据"""
    total_guides = db.query(TravelGuide).count()
    published_guides = db.query(TravelGuide).filter(TravelGuide.status == "published").count()

    # 热门目的地
    top_destinations = db.query(
        TravelGuide.destination,
        func.count(TravelGuide.id).label('count')
    ).filter(
        TravelGuide.status == "published"
    ).group_by(
        TravelGuide.destination
    ).order_by(
        desc('count')
    ).limit(10).all()

    # 最新攻略
    recent_guides = db.query(TravelGuide).filter(
        TravelGuide.status == "published"
    ).order_by(
        desc(TravelGuide.created_at)
    ).limit(5).all()

    return {
        "total_guides": total_guides,
        "published_guides": published_guides,
        "total_views": db.query(func.sum(TravelGuide.view_count)).scalar() or 0,
        "total_likes": db.query(func.sum(TravelGuide.like_count)).scalar() or 0,
        "top_destinations": [
            {"destination": d[0], "count": d[1]} for d in top_destinations
        ],
        "recent_guides": [
            TravelGuideListResponse.model_validate(g) for g in recent_guides
        ]
    }


# ============================================================
# 我的攻略 API
# ============================================================

@router.get("/my/guides", response_model=List[TravelGuideListResponse])
async def get_my_guides(
    status: Optional[str] = Query(None, description="状态筛选"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取我创建的攻略"""
    query = db.query(TravelGuide).filter(TravelGuide.user_id == current_user_id)

    if status:
        query = query.filter(TravelGuide.status == status)

    guides = query.order_by(desc(TravelGuide.created_at)).all()

    return [TravelGuideListResponse.model_validate(g) for g in guides]


@router.get("/my/stats", response_model=Dict[str, Any])
async def get_my_stats(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取我的统计数据"""
    user = db.query(User).filter(User.id == current_user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 计算统计数据
    guides_count = db.query(TravelGuide).filter(TravelGuide.user_id == current_user_id).count()
    bookmarks_count = db.query(UserBookmark).filter(UserBookmark.user_id == current_user_id).count()
    likes_count = db.query(GuideLike).filter(GuideLike.user_id == current_user_id).count()
    reviews_count = db.query(GuideReview).filter(GuideReview.user_id == current_user_id).count()

    # 获取我的攻略的总浏览量
    total_views = db.query(func.sum(TravelGuide.view_count)).filter(
        TravelGuide.user_id == current_user_id
    ).scalar() or 0

    return {
        "guides_count": guides_count,
        "bookmarks_count": bookmarks_count,
        "likes_count": likes_count,
        "reviews_count": reviews_count,
        "total_views": total_views
    }


# ============================================================
# 详细攻略生成 API (多智能体系统)
# ============================================================

class DetailedGuideRequest(BaseModel):
    """详细攻略生成请求"""
    guide_data: Dict = Field(..., description="基础攻略数据")


@router.post("/guides/generate-detailed")
async def generate_detailed_guide(
    request: DetailedGuideRequest,
    db: Session = Depends(get_db)
):
    """
    生成详细旅行攻略

    使用多智能体系统逐天、逐项生成详细内容：
    - 景点详情生成智能体
    - 餐厅推荐智能体
    - 交通规划智能体
    """
    try:
        guide_data = request.guide_data
        destination = guide_data.get("destination", "")

        logger.info(f"[详细攻略生成] 开始为 {destination} 生成详细攻略")
        logger.info(f"[详细攻略生成] 输入数据: days={guide_data.get('total_days')}, daily_itineraries数量={len(guide_data.get('daily_itinerary', guide_data.get('daily_itineraries', [])))}")

        # 创建LLM实例
        try:
            from tradingagents.graph.trading_graph import create_llm_by_provider
            from tradingagents.core.config_manager import config_service
            llm_provider = config_service.get("llm_provider", "openai")
            llm_config = config_service.get("quick_think_llm", {})
            llm = create_llm_by_provider(llm_provider, llm_config)
            logger.info(f"[详细攻略生成] LLM初始化成功: {llm_provider}")
        except Exception as e:
            logger.warning(f"[详细攻略生成] LLM初始化失败: {e}，使用智能推荐库")
            llm = None

        # 创建增强版详细攻略生成器（真正调用智能体生成内容）
        from tradingagents.services.enhanced_guide_generator import create_enhanced_guide_generator
        generator = create_enhanced_guide_generator(llm)

        # 生成详细攻略
        detailed_guide = generator.generate_detailed_guide(guide_data)

        logger.info(f"[详细攻略生成] 详细攻略生成完成！共 {len(detailed_guide.get('daily_itineraries', []))} 天")

        # 确保返回的数据包含 schedule 信息
        # 使用 detailed_days 作为主要键，同时保留 daily_itineraries 兼容性
        result_guide = {
            "destination": detailed_guide.get("destination"),
            "total_days": detailed_guide.get("total_days"),
            "detailed_days": detailed_guide.get("daily_itineraries", []),  # 前端期望的键
            "daily_itineraries": detailed_guide.get("daily_itineraries", [])  # 兼容性保留
        }

        # 添加总体贴士
        if detailed_guide.get('overall_tips'):
            result_guide['overall_tips'] = detailed_guide['overall_tips']

        # 打印第一天的第一个项目作为示例
        if detailed_guide.get('daily_itineraries'):
            first_day = detailed_guide['daily_itineraries'][0]
            logger.info(f"[详细攻略生成] 第一天数据: day={first_day.get('day')}, schedule数量={len(first_day.get('schedule', []))}")
            if first_day.get('schedule'):
                first_item = first_day['schedule'][0]
                logger.info(f"[详细攻略生成] 第一个项目: activity={first_item.get('activity')}, has_details={first_item.get('has_details')}, has_recommendations={bool(first_item.get('recommendations'))}")

        return {
            "success": True,
            "detailed_guide": result_guide,
            "message": "详细攻略生成成功"
        }

    except Exception as e:
        logger.error(f"[详细攻略生成] 生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/guides/enhance-with-details")
async def enhance_guide_with_details(
    request: DetailedGuideRequest,
    db: Session = Depends(get_db)
):
    """
    增强现有攻略的详细信息

    为已有的基础攻略添加详细的景点、餐厅、交通信息
    """
    try:
        guide_data = request.guide_data

        # 使用详细攻略生成器
        from tradingagents.services.detailed_guide_generator import create_detailed_guide_generator

        generator = create_detailed_guide_generator(None)  # 暂时不使用LLM
        detailed_guide = generator.generate_detailed_guide(guide_data)

        return {
            "success": True,
            "enhanced_guide": detailed_guide,
            "message": "攻略增强完成"
        }

    except Exception as e:
        logger.error(f"[攻略增强] 增强失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/guides/generate-detailed-stream")
async def generate_detailed_guide_stream(
    request: DetailedGuideRequest,
    db: Session = Depends(get_db)
):
    """
    流式生成详细攻略（SSE）

    逐步返回每个智能体的生成进度，前端可以实时显示：
    - 当前执行的步骤
    - 每个智能体的输出结果
    - 进度百分比
    """
    from fastapi.responses import StreamingResponse
    import asyncio
    import json

    async def event_generator():
        try:
            guide_data = request.guide_data
            destination = guide_data.get("destination", "")
            days = guide_data.get("total_days", 5)

            # 支持两种数据格式
            daily_itinerary = guide_data.get("daily_itinerary") or guide_data.get("daily_itineraries") or []

            # 发送开始事件
            yield f"data: {json.dumps({'type': 'start', 'destination': destination, 'days': days}, ensure_ascii=False)}\n\n"

            # 使用增强版攻略生成器
            from tradingagents.services.enhanced_guide_generator import create_enhanced_guide_generator
            generator = create_enhanced_guide_generator(None)

            # 生成详细攻略
            detailed_guide = generator.generate_detailed_guide(guide_data)

            # 逐天发送进度和结果
            total_days = len(detailed_guide.get("daily_itineraries", []))
            current_step = 0
            total_steps = total_days * 4

            for day_info in detailed_guide.get("daily_itineraries", []):
                day_number = day_info.get("day", 1)
                schedule = day_info.get("schedule", [])

                # 开始第N天
                current_step += 1
                progress = int((current_step / total_steps) * 100)
                yield f"data: {json.dumps({'type': 'progress', 'step': f'开始生成第{day_number}天攻略', 'day': day_number, 'progress': progress, 'agent': '协调器'}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.2)

                # 处理每个活动
                for item in schedule:
                    period = item.get("period", "")
                    activity = item.get("activity", "")

                    if period in ["lunch", "dinner"] and item.get("recommendations"):
                        # 餐厅推荐
                        current_step += 1
                        progress = int((current_step / total_steps) * 100)
                        recommendations = item.get("recommendations", {})
                        restaurant_name = recommendations.get("restaurant", "推荐餐厅")

                        yield f"data: {json.dumps({'type': 'progress', 'step': f'第{day_number}天{period}推荐餐厅', 'day': day_number, 'progress': progress, 'agent': '餐厅推荐智能体'}, ensure_ascii=False)}\n\n"
                        await asyncio.sleep(0.3)

                        yield f"data: {json.dumps({'type': 'step_result', 'step': f'第{day_number}天{period}餐厅推荐', 'day': day_number, 'period': period, 'data': recommendations, 'summary': f'已推荐{restaurant_name}，包含招牌菜品和人均消费', 'progress': progress, 'agent': '餐厅推荐智能体'}, ensure_ascii=False)}\n\n"

                    elif period in ["morning", "afternoon", "evening"] and activity:
                        # 景点详情
                        current_step += 1
                        progress = int((current_step / total_steps) * 100)
                        location = item.get("location", activity)

                        yield f"data: {json.dumps({'type': 'progress', 'step': f'第{day_number}天{activity}详情生成', 'day': day_number, 'progress': progress, 'agent': '景点详情智能体'}, ensure_ascii=False)}\n\n"
                        await asyncio.sleep(0.3)

                        # 提取景点详情
                        detail_data = {
                            "description": item.get("description", ""),
                            "highlights": item.get("highlights", []),
                            "suggested_route": item.get("suggested_route", ""),
                            "tickets": item.get("tickets", {}),
                            "tips": item.get("tips", []),
                            "transport": item.get("transport", {})
                        }

                        yield f"data: {json.dumps({'type': 'step_result', 'step': f'第{day_number}天{activity}详细攻略', 'day': day_number, 'activity': activity, 'data': detail_data, 'summary': f'已生成{location}详细攻略，包含必看亮点、游览路线和拍照建议', 'progress': progress, 'agent': '景点详情智能体'}, ensure_ascii=False)}\n\n"

            # 完成 - 返回完整的详细攻略
            yield f"data: {json.dumps({'type': 'complete', 'progress': 100, 'message': '详细攻略生成完成！', 'detailed_guide': detailed_guide}, ensure_ascii=False)}\n\n"

        except Exception as e:
            logger.error(f"流式生成失败: {e}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


def _extract_schedule_from_day(day_info: dict) -> list:
    """从天数信息中提取行程安排"""
    schedule = []
    periods = ["morning", "lunch", "afternoon", "dinner", "evening"]

    for period in periods:
        if period in day_info and day_info[period]:
            period_data = day_info[period]
            schedule.append({
                "period": period,
                "time_range": period_data.get("time", ""),
                "activity": period_data.get("activity", ""),
                "location": period_data.get("attraction", period_data.get("activity", ""))
            })

    return schedule
