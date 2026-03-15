"""
旅行图片API路由

提供景点图片获取接口
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["旅行图片"])


class AttractionImageRequest(BaseModel):
    """景点图片请求"""
    attraction_name: str
    city: str
    width: int = 800
    height: int = 600


class BatchImageRequest(BaseModel):
    """批量图片请求"""
    attractions: list[dict]


@router.get("/attraction")
async def get_attraction_image(
    attraction_name: str = Query(..., description="景点名称"),
    city: str = Query(..., description="城市"),
    width: int = Query(800, description="图片宽度"),
    height: int = Query(600, description="图片高度")
):
    """
    获取景点图片URL

    Args:
        attraction_name: 景点名称（支持中文和英文）
        city: 城市
        width: 图片宽度
        height: 图片高度

    Returns:
        {
            "url": "图片URL",
            "source": "图片来源 (unsplash/pexels/public/placeholder)",
            "attraction_name": "景点名称",
            "city": "城市"
        }
    """
    try:
        from tradingagents.services.attraction_image_service import get_attraction_image

        # 获取图片URL
        url = get_attraction_image(attraction_name, city, width, height)

        # 判断图片来源
        if "unsplash.com" in url:
            source = "unsplash"
        elif "pexels.com" in url:
            source = "pexels"
        elif "picsum.photos" in url:
            source = "picsum"
        elif "loremflickr.com" in url:
            source = "public"
        elif "placehold.co" in url:
            source = "placeholder"
        else:
            source = "unknown"

        return {
            "url": url,
            "source": source,
            "attraction_name": attraction_name,
            "city": city,
            "width": width,
            "height": height
        }

    except Exception as e:
        logger.error(f"获取景点图片失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/attraction")
async def get_attraction_image_post(request: AttractionImageRequest):
    """
    获取景点图片URL (POST方式)

    适用于需要JSON请求体的场景
    """
    return await get_attraction_image(
        attraction_name=request.attraction_name,
        city=request.city,
        width=request.width,
        height=request.height
    )


@router.post("/batch")
async def get_batch_images(request: BatchImageRequest):
    """
    批量获取景点图片URL

    Args:
        attractions: 景点列表 [{"name": "景点名", "city": "城市"}]

    Returns:
        {
            "images": {
                "景点名": {"url": "...", "source": "..."}
            }
        }
    """
    try:
        from tradingagents.services.attraction_image_service import get_attraction_image

        results = {}
        for item in request.attractions:
            name = item.get("name", "")
            city = item.get("city", "")

            if name:
                url = get_attraction_image(name, city, 800, 600)

                # 判断图片来源
                if "unsplash.com" in url:
                    source = "unsplash"
                elif "pexels.com" in url:
                    source = "pexels"
                elif "loremflickr.com" in url:
                    source = "public"
                elif "placehold.co" in url:
                    source = "placeholder"
                else:
                    source = "unknown"

                results[name] = {
                    "url": url,
                    "source": source,
                    "city": city
                }

        return {"images": results}

    except Exception as e:
        logger.error(f"批量获取景点图片失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/destination/{city}")
async def get_destination_image(
    city: str,
    width: int = Query(1200, description="图片宽度"),
    height: int = Query(600, description="图片高度")
):
    """
    获取目的地城市图片

    用于目的地卡片展示
    优先从缓存读取，缓存未命中时调用API
    """
    try:
        from tradingagents.services.attraction_image_service import get_attraction_image
        from tradingagents.services.destination_image_cache import get_destination_image_cache

        # 先尝试从缓存获取
        cache = get_destination_image_cache()
        cached = cache.get(city)

        if cached:
            logger.info(f"缓存命中: {city}")
            return {
                "url": cached["url"],
                "source": cached["source"],
                "city": city,
                "width": width,
                "height": height,
                "cached": True
            }

        # 缓存未命中，调用API获取
        logger.info(f"缓存未命中: {city}，调用API")
        import traceback
        logger.info(f"调用栈: {''.join(traceback.format_stack()[-3:])}")
        url = get_attraction_image(city, city, width, height)
        logger.info(f"API返回URL: {url}")

        # 判断图片来源
        if "unsplash.com" in url:
            source = "unsplash"
        elif "pexels.com" in url:
            source = "pexels"
        elif "picsum.photos" in url:
            source = "picsum"
        elif "loremflickr.com" in url:
            source = "public"
        elif "placehold.co" in url:
            source = "placeholder"
        else:
            source = "unknown"

        # 存入缓存
        cache.set(city, url, source)

        return {
            "url": url,
            "source": source,
            "city": city,
            "width": width,
            "height": height,
            "cached": False
        }

    except Exception as e:
        logger.error(f"获取目的地图片失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-direct")
async def test_direct_call(city: str = Query("测试", description="城市")):
    """测试直接调用函数"""
    from tradingagents.services.attraction_image_service import get_attraction_image
    import inspect
    import traceback

    # 获取函数信息
    func = get_attraction_image
    source_file = inspect.getsourcefile(func)
    source_lines = inspect.getsourcelines(func)[0][:20]

    # 调用函数
    url = func(city, city, 600, 400)

    return {
        "url": url,
        "function_name": func.__name__,
        "module": func.__module__,
        "source_file": source_file,
        "source_preview": "".join(source_lines),
        "is_picsum": "picsum.photos" in url,
        "is_unsplash": "unsplash.com" in url
    }


@router.get("/status")
async def get_image_service_status():
    """
    获取图片服务状态

    返回所有图片API的配置和状态
    """
    try:
        from tradingagents.services.attraction_image_service import get_image_service

        service = get_image_service()
        status = service.check_api_status()

        return {
            "status": "ok",
            "services": status
        }

    except Exception as e:
        logger.error(f"获取图片服务状态失败: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/preload/popular")
async def get_popular_destinations_images(
    limit: int = Query(20, description="返回数量"),
    region: str = Query(None, description="地区筛选")
):
    """
    获取热门城市图片URL列表（用于前端预加载）

    批量返回热门城市的图片URL，前端可以在页面加载后
    静默预加载这些图片到浏览器缓存

    Args:
        limit: 返回数量限制（默认20个）
        region: 地区筛选 (china, southeast_asia, east_asia, europe, americas, oceania, middle_east)

    Returns:
        {
            "destinations": [
                {"city": "三亚", "url": "...", "source": "unsplash"},
                {"city": "曼谷", "url": "...", "source": "pexels"},
                ...
            ],
            "total": 20
        }
    """
    try:
        from tradingagents.config.popular_destinations import get_popular_destinations
        from tradingagents.services.attraction_image_service import get_attraction_image

        # 获取热门城市列表
        cities = get_popular_destinations(limit=limit, region=region)

        # 批量获取图片URL
        destinations = []
        for city in cities:
            try:
                url = get_attraction_image(city, city, 600, 400)

                # 判断图片来源
                if "unsplash.com" in url:
                    source = "unsplash"
                elif "pexels.com" in url:
                    source = "pexels"
                elif "loremflickr.com" in url:
                    source = "public"
                elif "placehold.co" in url:
                    source = "placeholder"
                else:
                    source = "unknown"

                destinations.append({
                    "city": city,
                    "url": url,
                    "source": source,
                    "width": 600,
                    "height": 400
                })
            except Exception as e:
                logger.warning(f"获取 {city} 图片失败: {e}")
                # 使用占位图
                destinations.append({
                    "city": city,
                    "url": f"https://placehold.co/600x400?text={city}",
                    "source": "placeholder",
                    "width": 600,
                    "height": 400
                })

        logger.info(f"返回热门城市图片URL: {len(destinations)}个")

        return {
            "destinations": destinations,
            "total": len(destinations)
        }

    except Exception as e:
        logger.error(f"获取热门城市图片失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preload/top")
async def get_top_destinations_images(
    limit: int = Query(20, description="返回数量")
):
    """
    获取TOP热门城市图片URL列表

    返回最受欢迎的旅行目的地图片，用于首页预加载
    优先从缓存读取
    """
    try:
        from tradingagents.config.popular_destinations import get_top_destinations
        from tradingagents.services.attraction_image_service import get_attraction_image
        from tradingagents.services.destination_image_cache import get_destination_image_cache

        # 获取TOP城市列表
        cities = get_top_destinations(limit=limit)
        cache = get_destination_image_cache()

        # 批量获取图片URL（优先从缓存）
        destinations = []
        cache_hits = 0

        for city in cities:
            try:
                # 先尝试从缓存获取
                cached = cache.get(city)

                if cached:
                    url = cached["url"]
                    source = cached["source"]
                    cache_hits += 1
                else:
                    # 缓存未命中，调用API
                    url = get_attraction_image(city, city, 600, 400)

                    if "unsplash.com" in url:
                        source = "unsplash"
                    elif "pexels.com" in url:
                        source = "pexels"
                    elif "loremflickr.com" in url:
                        source = "public"
                    elif "placehold.co" in url:
                        source = "placeholder"
                    else:
                        source = "unknown"

                    # 存入缓存
                    cache.set(city, url, source)

                destinations.append({
                    "city": city,
                    "url": url,
                    "source": source,
                    "width": 600,
                    "height": 400
                })
            except Exception as e:
                logger.warning(f"获取 {city} 图片失败: {e}")
                destinations.append({
                    "city": city,
                    "url": f"https://placehold.co/600x400?text={city}",
                    "source": "placeholder",
                    "width": 600,
                    "height": 400
                })

        logger.info(f"返回TOP热门城市图片URL: {len(destinations)}个 (缓存命中: {cache_hits})")

        return {
            "destinations": destinations,
            "total": len(destinations),
            "cache_hits": cache_hits,
            "cache_hit_rate": f"{cache_hits/len(cities)*100:.1f}%"
        }

    except Exception as e:
        logger.error(f"获取TOP热门城市图片失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/destinations/list")
async def get_destinations_list(
    region: str = Query(None, description="地区筛选")
):
    """
    获取热门城市列表（不含图片）

    返回所有热门目的地的城市名称
    """
    try:
        from tradingagents.config.popular_destinations import get_popular_destinations, POPULAR_DESTINATIONS

        if region:
            cities = POPULAR_DESTINATIONS.get(region, [])
            return {
                "region": region,
                "destinations": cities,
                "total": len(cities)
            }
        else:
            cities = get_popular_destinations()
            return {
                "destinations": cities,
                "total": len(cities),
                "regions": list(POPULAR_DESTINATIONS.keys())
            }

    except Exception as e:
        logger.error(f"获取城市列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 缓存管理API ====================

@router.get("/cache/stats")
async def get_cache_stats():
    """
    获取缓存统计信息

    返回缓存命中率、大小、刷新时间等统计信息
    """
    try:
        from tradingagents.services.destination_image_cache import get_destination_image_cache

        cache = get_destination_image_cache()
        stats = cache.get_stats()

        return {
            "status": "ok",
            "cache": stats
        }

    except Exception as e:
        logger.error(f"获取缓存统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/list")
async def get_cache_list(
    limit: int = Query(50, description="返回数量")
):
    """
    获取缓存列表

    返回当前缓存的所有城市和图片URL
    """
    try:
        from tradingagents.services.destination_image_cache import get_destination_image_cache

        cache = get_destination_image_cache()
        all_cache = cache.get_all()

        # 按更新时间排序
        sorted_items = sorted(
            all_cache.items(),
            key=lambda x: x[1]["updated_at"],
            reverse=True
        )

        # 限制返回数量
        items = sorted_items[:limit]

        result = []
        for city, data in items:
            result.append({
                "city": city,
                "url": data["url"],
                "source": data["source"],
                "updated_at": data["updated_at"]
            })

        return {
            "total": len(all_cache),
            "returned": len(result),
            "items": result
        }

    except Exception as e:
        logger.error(f"获取缓存列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/refresh")
async def refresh_cache(
    force: bool = Query(False, description="是否强制刷新（忽略TTL检查）")
):
    """
    刷新缓存

    重新加载所有热门城市的图片URL到缓存
    """
    try:
        from tradingagents.services.destination_image_cache import initialize_popular_destinations_cache

        logger.info(f"手动刷新缓存 (force={force})")

        # 异步刷新
        result = await initialize_popular_destinations_cache()

        return {
            "status": "success",
            "message": "缓存刷新完成",
            "result": result
        }

    except Exception as e:
        logger.error(f"刷新缓存失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cache")
async def clear_cache():
    """
    清空缓存

    删除所有缓存的图片URL
    """
    try:
        from tradingagents.services.destination_image_cache import get_destination_image_cache

        cache = get_destination_image_cache()
        count = cache.clear()

        logger.info(f"缓存已清空: {count}条")

        return {
            "status": "success",
            "message": f"已清空{count}条缓存",
            "cleared": count
        }

    except Exception as e:
        logger.error(f"清空缓存失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cache/{city}")
async def delete_cache_item(city: str):
    """
    删除指定城市的缓存

    删除单个城市的图片URL缓存
    """
    try:
        from tradingagents.services.destination_image_cache import get_destination_image_cache

        cache = get_destination_image_cache()
        success = cache.delete(city)

        if success:
            return {
                "status": "success",
                "message": f"已删除 {city} 的缓存",
                "city": city
            }
        else:
            raise HTTPException(status_code=404, detail=f"{city} 不在缓存中")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除缓存失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

