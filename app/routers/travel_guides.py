"""
旅行攻略保存和管理API
使用MongoDB持久化存储
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import Response, FileResponse
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId
import logging
from enum import Enum

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/guides-center", tags=["旅行攻略"])


class GuideStatus(str, Enum):
    """攻略状态"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class SaveGuideRequest(BaseModel):
    """保存攻略请求"""
    user_id: str = Field(..., description="用户ID")
    title: str = Field(..., description="攻略标题")
    destination: str = Field(..., description="目的地")
    total_days: int = Field(..., description="总天数")
    guide_data: dict = Field(..., description="完整攻略数据")
    budget: int = Field(..., description="总预算")
    tags: List[str] = Field(default_factory=list, description="标签")
    is_public: bool = Field(False, description="是否公开")


class UpdateGuideRequest(BaseModel):
    """更新攻略请求"""
    guide_id: str
    title: Optional[str] = None
    guide_data: Optional[dict] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    status: Optional[GuideStatus] = None


class GuideListItem(BaseModel):
    """攻略列表项"""
    id: str
    title: str
    destination: str
    total_days: int
    budget: int
    tags: List[str]
    status: GuideStatus
    created_at: datetime
    updated_at: datetime
    thumbnail_url: Optional[str] = None


class GuideDetail(BaseModel):
    """攻略详情"""
    id: str
    user_id: str
    title: str
    destination: str
    total_days: int
    budget: int
    tags: List[str]
    status: GuideStatus
    is_public: bool
    guide_data: dict
    thumbnail_url: Optional[str] = None
    view_count: int = 0
    like_count: int = 0
    created_at: datetime
    updated_at: datetime


# MongoDB集合名称
COLLECTION_NAME = "travel_guides"


async def _get_guides_collection():
    """获取攻略集合（使用异步MongoDB）"""
    try:
        from app.core.database import get_mongo_db
        return get_mongo_db()[COLLECTION_NAME]
    except Exception as e:
        logger.error(f"获取MongoDB连接失败: {e}")
        return None


def _generate_guide_id() -> str:
    """生成唯一的攻略ID"""
    import random
    import string
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"guide_{timestamp}_{random_str}"


async def _ensure_indexes():
    """确保集合索引存在"""
    try:
        collection = await _get_guides_collection()
        if collection is None:
            return

        # 创建索引
        indexes = [
            [("user_id", 1), ("created_at", -1)],
            [("destination", 1), ("created_at", -1)],
            [("is_public", 1), ("status", 1), ("created_at", -1)],
            [("created_at", -1)],
            [("view_count", -1)],
            [("like_count", -1)]
        ]

        existing_indexes = await collection.index_information()
        for index_spec in indexes:
            index_key = index_spec
            index_name = f"_idx_{'_'.join([f'{k}_{v}' for k, v in index_spec])}"

            # 检查索引是否已存在
            already_exists = any(
                idx == index_key or idx.get('key') == index_key
                for idx in existing_indexes.values()
            )

            if not already_exists:
                try:
                    await collection.create_index([(k, v) for k, v in index_spec], name=index_name[:-10])
                    logger.info(f"创建索引: {index_name}")
                except Exception as e:
                    logger.warning(f"创建索引失败 {index_name}: {e}")

    except Exception as e:
        logger.warning(f"确保索引失败: {e}")


@router.on_event("startup")
async def startup_event():
    """路由启动时初始化索引"""
    await _ensure_indexes()


@router.post("/save", response_model=dict)
async def save_guide(request: SaveGuideRequest):
    """
    保存攻略

    保存新的旅行攻略到MongoDB
    """
    try:
        collection = await _get_guides_collection()
        if collection is None:
            raise HTTPException(status_code=500, detail="数据库连接失败")

        # 生成新的攻略ID
        guide_id = _generate_guide_id()

        # 检查ID是否已存在，如果存在则重新生成
        while await collection.find_one({"id": guide_id}):
            guide_id = _generate_guide_id()

        # 获取目的地图片作为缩略图
        thumbnail_url = None
        try:
            from tradingagents.services.attraction_image_service import get_attraction_image
            thumbnail_url = get_attraction_image(request.destination, request.destination, 800, 600)

            # 确保返回有效URL，如果是None则使用LoremFlickr直接生成
            if not thumbnail_url or "placehold.co" in thumbnail_url:
                logger.warning(f"图片服务返回占位图，直接使用LoremFlickr")
                # 直接使用LoremFlickr生成
                from urllib.parse import quote
                city_en = _get_city_english_name(request.destination)
                seed = _generate_seed(request.destination)
                thumbnail_url = f"https://loremflickr.com/800/600/{city_en},travel,landscape?lock={seed}"
                logger.info(f"使用LoremFlickr: {thumbnail_url}")
        except Exception as e:
            logger.warning(f"获取缩略图失败，使用默认图片: {e}")
            # 使用可靠的默认图片源
            from urllib.parse import quote
            city_en = _get_city_english_name(request.destination)
            seed = _generate_seed(request.destination)
            thumbnail_url = f"https://loremflickr.com/800/600/{city_en},travel,landscape?lock={seed}"
            logger.info(f"使用默认LoremFlickr: {thumbnail_url}")

        # 创建攻略记录
        now = datetime.now()
        guide_record = {
            "id": guide_id,
            "user_id": request.user_id,
            "title": request.title,
            "destination": request.destination,
            "total_days": request.total_days,
            "budget": request.budget,
            "tags": request.tags,
            "status": GuideStatus.PUBLISHED.value,
            "is_public": request.is_public,
            "guide_data": request.guide_data,
            "thumbnail_url": thumbnail_url,
            "view_count": 0,
            "like_count": 0,
            "created_at": now,
            "updated_at": now
        }

        # 保存到MongoDB
        await collection.insert_one(guide_record)

        logger.info(f"攻略保存成功: {guide_id} - {request.title}")

        return {
            "success": True,
            "guide_id": guide_id,
            "message": "攻略保存成功"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"保存攻略失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/public", response_model=List[GuideListItem])
async def get_public_guides(
    destination: Optional[str] = Query(None, description="目的地筛选"),
    limit: int = Query(20, description="返回数量"),
    offset: int = Query(0, description="偏移量")
):
    """
    获取公开的攻略列表（攻略中心）
    """
    try:
        collection = await _get_guides_collection()
        if collection is None:
            raise HTTPException(status_code=500, detail="数据库连接失败")

        # 构建查询条件
        query = {
            "is_public": True,
            "status": GuideStatus.PUBLISHED.value
        }

        if destination:
            query["destination"] = destination

        # 查询公开的攻略
        cursor = collection.find(query).sort("created_at", -1).skip(offset).limit(limit)
        documents = await cursor.to_list(length=limit)

        public_guides = []
        for doc in documents:
            # 转换ObjectId为字符串
            doc["id"] = doc.get("id", str(doc.get("_id", "")))
            public_guides.append(GuideListItem(**doc))

        return public_guides

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取公开攻略失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/destinations", response_model=List[str])
async def get_popular_destinations():
    """
    获取热门目的地列表（用于筛选）
    """
    try:
        collection = await _get_guides_collection()
        if collection is None:
            raise HTTPException(status_code=500, detail="数据库连接失败")

        # 聚合查询获取所有不同的目的地
        pipeline = [
            {"$group": {"_id": "$destination", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 50}
        ]

        cursor = collection.aggregate(pipeline)
        documents = await cursor.to_list(length=50)

        destinations = [doc["_id"] for doc in documents]
        return sorted(destinations)

    except Exception as e:
        logger.error(f"获取目的地列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=List[GuideListItem])
async def get_user_guides(
    user_id: str = Query(..., description="用户ID"),
    status: Optional[GuideStatus] = Query(None, description="筛选状态"),
    limit: int = Query(20, description="返回数量"),
    offset: int = Query(0, description="偏移量")
):
    """
    获取用户的攻略列表
    """
    try:
        collection = await _get_guides_collection()
        if collection is None:
            raise HTTPException(status_code=500, detail="数据库连接失败")

        # 构建查询条件
        query = {"user_id": user_id}
        if status:
            query["status"] = status.value

        # 查询用户的攻略
        cursor = collection.find(query).sort("created_at", -1).skip(offset).limit(limit)
        documents = await cursor.to_list(length=limit)

        user_guides = []
        for doc in documents:
            doc["id"] = doc.get("id", str(doc.get("_id", "")))
            user_guides.append(GuideListItem(**doc))

        return user_guides

    except Exception as e:
        logger.error(f"获取攻略列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/guide/{guide_id}", response_model=GuideDetail)
async def get_guide_detail(guide_id: str):
    """
    获取攻略详情
    """
    try:
        collection = await _get_guides_collection()
        if collection is None:
            raise HTTPException(status_code=500, detail="数据库连接失败")

        guide = await collection.find_one({"id": guide_id})
        if not guide:
            raise HTTPException(status_code=404, detail="攻略不存在")

        # 增加浏览次数
        await collection.update_one(
            {"id": guide_id},
            {"$inc": {"view_count": 1}}
        )
        guide["view_count"] = guide.get("view_count", 0) + 1

        # 转换为响应模型
        guide["id"] = guide.get("id", str(guide.get("_id", "")))

        return GuideDetail(**guide)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取攻略详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update", response_model=dict)
async def update_guide(request: UpdateGuideRequest):
    """
    更新攻略
    """
    try:
        collection = await _get_guides_collection()
        if collection is None:
            raise HTTPException(status_code=500, detail="数据库连接失败")

        # 检查攻略是否存在
        existing = await collection.find_one({"id": request.guide_id})
        if not existing:
            raise HTTPException(status_code=404, detail="攻略不存在")

        # 构建更新数据
        update_data = {"updated_at": datetime.now()}

        if request.title is not None:
            update_data["title"] = request.title
        if request.guide_data is not None:
            update_data["guide_data"] = request.guide_data
        if request.tags is not None:
            update_data["tags"] = request.tags
        if request.is_public is not None:
            update_data["is_public"] = request.is_public
        if request.status is not None:
            update_data["status"] = request.status.value

        # 更新攻略
        await collection.update_one(
            {"id": request.guide_id},
            {"$set": update_data}
        )

        logger.info(f"攻略更新成功: {request.guide_id}")

        return {
            "success": True,
            "message": "攻略更新成功"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新攻略失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/guide/{guide_id}", response_model=dict)
async def delete_guide(guide_id: str, user_id: str = Query(..., description="用户ID")):
    """
    删除攻略
    """
    try:
        collection = await _get_guides_collection()
        if collection is None:
            raise HTTPException(status_code=500, detail="数据库连接失败")

        # 检查攻略是否存在
        guide = await collection.find_one({"id": guide_id})
        if not guide:
            raise HTTPException(status_code=404, detail="攻略不存在")

        # 验证权限
        if guide.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="无权删除此攻略")

        # 删除攻略
        await collection.delete_one({"id": guide_id})

        logger.info(f"攻略删除成功: {guide_id}")

        return {
            "success": True,
            "message": "攻略删除成功"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除攻略失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/guide/{guide_id}/like", response_model=dict)
async def like_guide(guide_id: str):
    """
    点赞攻略
    """
    try:
        collection = await _get_guides_collection()
        if collection is None:
            raise HTTPException(status_code=500, detail="数据库连接失败")

        # 检查攻略是否存在
        guide = await collection.find_one({"id": guide_id})
        if not guide:
            raise HTTPException(status_code=404, detail="攻略不存在")

        # 增加点赞数
        await collection.update_one(
            {"id": guide_id},
            {"$inc": {"like_count": 1}}
        )

        # 获取更新后的点赞数
        updated = await collection.find_one({"id": guide_id})
        like_count = updated.get("like_count", 0)

        return {
            "success": True,
            "like_count": like_count
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"点赞攻略失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/guide/{guide_id}/export/pdf")
async def export_guide_pdf(guide_id: str):
    """
    导出攻略为PDF

    生成并下载攻略的PDF文件
    """
    try:
        collection = await _get_guides_collection()
        if collection is None:
            raise HTTPException(status_code=500, detail="数据库连接失败")

        guide = await collection.find_one({"id": guide_id})
        if not guide:
            raise HTTPException(status_code=404, detail="攻略不存在")

        # 生成PDF
        from app.utils.pdf_generator import get_pdf_generator
        from datetime import datetime
        from pathlib import Path

        generator = get_pdf_generator()

        # 准备攻略数据
        guide_data = guide.get("guide_data", {})

        # 添加额外的元数据
        guide_data["id"] = guide_id
        guide_data["title"] = guide.get("title", "旅行攻略")

        # 生成PDF字节
        pdf_bytes = generator.generate_pdf(guide_data)

        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        destination = guide_data.get('destination', 'guide')
        safe_destination = _sanitize_filename(destination)
        filename = f"{safe_destination}_攻略_{timestamp}.pdf"

        # 返回PDF文件
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}.pdf"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出PDF失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _sanitize_filename(filename: str) -> str:
    """清理文件名"""
    from urllib.parse import quote
    illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in illegal_chars:
        filename = filename.replace(char, '_')
    if len(filename) > 50:
        filename = filename[:50]
    return filename.strip()


def _get_city_english_name(city: str) -> str:
    """获取城市的英文名称（用于图片搜索）"""
    city_map = {
        # 中国城市
        "北京": "beijing", "上海": "shanghai", "广州": "guangzhou", "深圳": "shenzhen",
        "成都": "chengdu", "重庆": "chongqing", "西安": "xian", "杭州": "hangzhou",
        "南京": "nanjing", "苏州": "suzhou", "武汉": "wuhan", "厦门": "xiamen",
        "青岛": "qingdao", "大连": "dalian", "桂林": "guilin", "丽江": "lijiang",
        "大理": "dali", "三亚": "sanya", "拉萨": "lhasa", "香港": "hong+kong",
        # 东南亚
        "曼谷": "bangkok", "清迈": "chiang+mai", "普吉岛": "phuket",
        "新加坡": "singapore", "吉隆坡": "kuala+lumpur", "巴厘岛": "bali",
        "河内": "hanoi", "胡志明市": "ho+chi+minh",
        # 日本韩国
        "东京": "tokyo", "京都": "kyoto", "大阪": "osaka",
        "首尔": "seoul", "釜山": "busan", "济州岛": "jeju",
        # 欧洲
        "巴黎": "paris", "伦敦": "london", "罗马": "rome",
        "巴塞罗那": "barcelona", "阿姆斯特丹": "amsterdam", "雅典": "athens",
        # 美国其他
        "纽约": "new+york", "洛杉矶": "los+angeles", "旧金山": "san+francisco",
        # 澳大利亚
        "悉尼": "sydney", "墨尔本": "melbourne",
        # 其他
        "迪拜": "dubai"
    }
    return city_map.get(city, city.lower().replace(" ", "+").replace("-", "+"))


def _generate_seed(destination: str) -> str:
    """生成一致的种子（用于相同目的地返回相同图片）"""
    import hashlib
    normalized = destination.lower().replace(" ", "").replace("-", "")
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()[:10]
