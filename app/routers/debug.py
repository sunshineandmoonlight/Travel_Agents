"""
缓存和共享数据检查工具

提供API端点和检查函数，用于查看缓存和共享数据的状态
"""

from fastapi import APIRouter
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/debug", tags=["Debug"])


@router.get("/cache/stats")
async def get_cache_stats():
    """
    获取缓存统计信息

    Returns:
        缓存统计信息，包括缓存类型（redis/memory）
    """
    try:
        from tradingagents.utils.cache_init import get_cache_stats

        stats = get_cache_stats()

        return {
            "status": "ok",
            "cache": {
                "cache_backend": stats.get("cache_backend", "memory"),
                "total_requests": stats.get("total_requests", 0),
                "hits": stats.get("hits", 0),
                "misses": stats.get("misses", 0),
                "hit_rate": stats.get("hit_rate", "0%"),
                "cache_size": stats.get("cache_size", 0),
                "default_ttl": stats.get("default_ttl", 3600)
            }
        }

    except Exception as e:
        logger.error(f"获取缓存统计失败: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/cache/clear")
async def clear_cache(tool_name: str = ""):
    """
    清空缓存

    Args:
        tool_name: 可选的工具名，如果指定则只清理匹配工具的缓存

    Returns:
        清理结果
    """
    try:
        from tradingagents.utils.cache_init import clear_cache as clear_cache_system

        count = clear_cache_system(pattern=tool_name)

        return {
            "status": "ok",
            "message": f"已清理 {count} 条缓存",
            "tool": tool_name or "all"
        }

    except Exception as e:
        logger.error(f"清空缓存失败: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/shared-data/stats")
async def get_shared_data_stats():
    """
    获取共享数据统计信息

    Returns:
        共享数据统计
    """
    try:
        from tradingagents.utils.shared_data import get_shared_data_manager

        manager = get_shared_data_manager()
        metadata = manager.get_all_metadata()

        return {
            "status": "ok",
            "shared_data": {
                "total_items": len(metadata),
                "items": metadata
            }
        }

    except Exception as e:
        logger.error(f"获取共享数据统计失败: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/shared-data/clear")
async def clear_shared_data():
    """
    清空共享数据

    Returns:
        清理结果
    """
    try:
        from tradingagents.utils.shared_data import get_shared_data_manager

        manager = get_shared_data_manager()
        manager.clear()

        return {
            "status": "ok",
            "message": "已清空所有共享数据"
        }

    except Exception as e:
        logger.error(f"清空共享数据失败: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/system/status")
async def get_system_status():
    """
    获取系统整体状态

    包括缓存、共享数据、API配置等
    """
    try:
        from tradingagents.utils.tool_cache import get_cache_manager
        from tradingagents.utils.shared_data import get_shared_data_manager
        import os

        cache_manager = get_cache_manager()
        shared_manager = get_shared_data_manager()

        cache_stats = cache_manager.get_stats()
        shared_metadata = shared_manager.get_all_metadata()

        # 检查 API 配置
        api_config = {
            "SERPAPI_KEY": bool(os.getenv("SERPAPI_KEY") and "your_" not in os.getenv("SERPAPI_KEY", "")),
            "AMAP_API_KEY": bool(os.getenv("AMAP_API_KEY") and "your_" not in os.getenv("AMAP_API_KEY", "")),
            "OPENTRIPMAP_API_KEY": bool(os.getenv("OPENTRIPMAP_API_KEY") and "your_" not in os.getenv("OPENTRIPMAP_API_KEY", "")),
            "SILICONFLOW_API_KEY": bool(os.getenv("SILICONFLOW_API_KEY") and "your_" not in os.getenv("SILICONFLOW_API_KEY", "")),
        }

        return {
            "status": "ok",
            "cache": {
                "total_requests": cache_stats["total_requests"],
                "hits": cache_stats["hits"],
                "hit_rate": cache_stats["hit_rate"],
                "cache_size": cache_stats["cache_size"]
            },
            "shared_data": {
                "total_items": len(shared_metadata),
                "items": shared_metadata
            },
            "api_config": api_config
        }

    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


__all__ = [
    "router",
    "get_cache_stats",
    "clear_cache",
    "get_shared_data_stats",
    "clear_shared_data",
    "get_system_status",
]
