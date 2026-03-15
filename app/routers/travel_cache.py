"""
旅行缓存管理 API路由

管理旅行数据的缓存：
- 景点数据缓存
- 天气数据缓存
- 搜索结果缓存
- 攻略内容缓存
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging
import os
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/travel/cache", tags=["旅行缓存管理"])


# ============================================================
# 数据模型
# ============================================================

class CacheStatsResponse(BaseModel):
    """缓存统计响应"""
    total_entries: int
    total_size_bytes: int
    total_size_mb: float
    max_size_mb: float
    usage_percent: float
    by_type: Dict[str, Any]
    last_cleanup: str


class CacheEntry(BaseModel):
    """缓存条目"""
    key: str
    type: str
    size_bytes: int
    created_at: str
    expires_at: Optional[str]
    access_count: int
    last_accessed: str


# ============================================================
# 简单的内存缓存实现
# ============================================================

class TravelCache:
    """旅行数据缓存"""

    def __init__(self):
        self._cache = {}  # {key: {value, created_at, expires_at, access_count, last_accessed}}
        self._max_size = 100 * 1024 * 1024  # 100MB
        self._last_cleanup = None

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key not in self._cache:
            return None

        entry = self._cache[key]

        # 检查是否过期
        if entry.get("expires_at"):
            if datetime.fromisoformat(entry["expires_at"]) < datetime.utcnow():
                del self._cache[key]
                return None

        # 更新访问信息
        entry["access_count"] = entry.get("access_count", 0) + 1
        entry["last_accessed"] = datetime.utcnow().isoformat()

        return entry["value"]

    def set(self, key: str, value: Any, ttl: int = 3600):
        """设置缓存值"""
        import sys

        # 计算大小
        size = sys.getsizeof(value)

        # 检查容量
        if self._get_total_size() + size > self._max_size:
            self._evict_old_entries()

        expires_at = None
        if ttl > 0:
            expires_at = (datetime.utcnow() + timedelta(seconds=ttl)).isoformat()

        self._cache[key] = {
            "value": value,
            "size": size,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at,
            "access_count": 0,
            "last_accessed": datetime.utcnow().isoformat()
        }

    def delete(self, key: str) -> bool:
        """删除缓存"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self):
        """清空所有缓存"""
        self._cache.clear()

    def _get_total_size(self) -> int:
        """获取总大小"""
        return sum(entry.get("size", 0) for entry in self._cache.values())

    def _evict_old_entries(self):
        """清理旧条目"""
        # 按最后访问时间排序，删除最旧的20%
        entries = list(self._cache.items())
        entries.sort(key=lambda x: x[1].get("last_accessed", ""))

        to_remove = len(entries) // 5
        for key, _ in entries[:to_remove]:
            del self._cache[key]

    def cleanup_expired(self):
        """清理过期条目"""
        now = datetime.utcnow()
        expired_keys = []

        for key, entry in self._cache.items():
            if entry.get("expires_at"):
                if datetime.fromisoformat(entry["expires_at"]) < now:
                    expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]

        self._last_cleanup = datetime.utcnow().isoformat()
        return len(expired_keys)

    def get_stats(self) -> dict:
        """获取统计信息"""
        total_entries = len(self._cache)
        total_size = self._get_total_size()

        # 按类型统计
        by_type = {}
        for key, entry in self._cache.items():
            key_parts = key.split(":")
            cache_type = key_parts[0] if key_parts else "unknown"
            by_type[cache_type] = by_type.get(cache_type, 0) + 1

        return {
            "total_entries": total_entries,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "max_size_mb": self._max_size / (1024 * 1024),
            "usage_percent": (total_size / self._max_size) * 100 if self._max_size > 0 else 0,
            "by_type": by_type,
            "last_cleanup": self._last_cleanup or "从未清理"
        }

    def get_entries(self, limit: int = 50) -> list:
        """获取缓存条目列表"""
        entries = []
        for key, entry in self._cache.items():
            entries.append({
                "key": key,
                "type": key.split(":")[0] if ":" in key else "unknown",
                "size_bytes": entry.get("size", 0),
                "created_at": entry.get("created_at", ""),
                "expires_at": entry.get("expires_at"),
                "access_count": entry.get("access_count", 0),
                "last_accessed": entry.get("last_accessed", "")
            })

        entries.sort(key=lambda x: x["last_accessed"], reverse=True)
        return entries[:limit]


# 全局缓存实例
_cache = TravelCache()


# ============================================================
# API端点
# ============================================================

@router.get("/stats", response_model=CacheStatsResponse)
async def get_cache_stats():
    """获取缓存统计"""
    stats = _cache.get_stats()
    return CacheStatsResponse(**stats)


@router.get("/entries")
async def get_cache_entries(
    cache_type: Optional[str] = Query(None, description="按类型筛选"),
    limit: int = Query(50, ge=1, le=200)
):
    """获取缓存条目列表"""
    entries = _cache.get_entries(limit)

    if cache_type:
        entries = [e for e in entries if e.get("type") == cache_type]

    return {
        "entries": entries,
        "total": len(entries)
    }


@router.delete("/clear")
async def clear_all_cache():
    """清空所有缓存"""
    _cache.clear()
    logger.info("清空所有缓存")

    return {
        "success": True,
        "message": "已清空所有缓存"
    }


@router.delete("/cleanup")
async def cleanup_expired_cache(
    ttl: int = Query(3600, ge=60, description="清理多少秒未访问的缓存")
):
    """清理过期缓存"""
    from datetime import timedelta

    cutoff_time = datetime.utcnow() - timedelta(seconds=ttl)
    removed_count = 0

    keys_to_remove = []
    for key, entry in _cache._cache.items():
        last_accessed = entry.get("last_accessed", "")
        if last_accessed:
            try:
                if datetime.fromisoformat(last_accessed) < cutoff_time:
                    keys_to_remove.append(key)
            except:
                pass

    for key in keys_to_remove:
        _cache.delete(key)
        removed_count += 1

    # 同时清理过期条目
    expired_count = _cache.cleanup_expired()

    total_removed = removed_count + expired_count

    return {
        "success": True,
        "message": f"已清理 {total_removed} 个缓存条目",
        "removed_count": total_removed
    }


@router.delete("/key/{cache_key}")
async def delete_cache_key(cache_key: str):
    """删除指定缓存"""
    success = _cache.delete(cache_key)

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"缓存不存在: {cache_key}"
        )

    return {
        "success": True,
        "message": f"已删除缓存: {cache_key}"
    }


@router.get("/key/{cache_key}")
async def get_cache_value(cache_key: str):
    """获取缓存值"""
    value = _cache.get(cache_key)

    if value is None:
        raise HTTPException(
            status_code=404,
            detail=f"缓存不存在: {cache_key}"
        )

    return {
        "key": cache_key,
        "value": value
    }


@router.post("/key/{cache_key}")
async def set_cache_value(
    cache_key: str,
    value: Any = None,
    ttl: int = Query(3600, ge=0, description="过期时间(秒)")
):
    """设置缓存值"""
    _cache.set(cache_key, value, ttl)

    return {
        "success": True,
        "message": f"已设置缓存: {cache_key}",
        "ttl": ttl
    }


# ============================================================
# 便捷函数：操作各类缓存
# ============================================================

def cache_attraction_data(destination: str, data: dict, ttl: int = 7200):
    """缓存景点数据"""
    key = f"attractions:{destination}"
    _cache.set(key, data, ttl)
    logger.info(f"缓存景点数据: {destination}")


def get_attraction_data(destination: str) -> Optional[dict]:
    """获取景点数据缓存"""
    key = f"attractions:{destination}"
    return _cache.get(key)


def cache_weather_data(destination: str, data: dict, ttl: int = 3600):
    """缓存天气数据"""
    key = f"weather:{destination}"
    _cache.set(key, data, ttl)
    logger.info(f"缓存天气数据: {destination}")


def get_weather_data(destination: str) -> Optional[dict]:
    """获取天气数据缓存"""
    key = f"weather:{destination}"
    return _cache.get(key)


def cache_search_results(keyword: str, results: list, ttl: int = 1800):
    """缓存搜索结果"""
    import hashlib
    key_hash = hashlib.md5(keyword.encode()).hexdigest()[:8]
    key = f"search:{key_hash}"
    _cache.set(key, results, ttl)
    logger.info(f"缓存搜索结果: {keyword}")


def get_search_results(keyword: str) -> Optional[list]:
    """获取搜索结果缓存"""
    import hashlib
    key_hash = hashlib.md5(keyword.encode()).hexdigest()[:8]
    key = f"search:{key_hash}"
    return _cache.get(key)


def cache_guide_content(guide_id: int, content: dict, ttl: int = 3600):
    """缓存攻略内容"""
    key = f"guide:{guide_id}"
    _cache.set(key, content, ttl)
    logger.info(f"缓存攻略内容: {guide_id}")


def get_guide_content(guide_id: int) -> Optional[dict]:
    """获取攻略内容缓存"""
    key = f"guide:{guide_id}"
    return _cache.get(key)


def clear_destination_cache(destination: str):
    """清除指定目的地的所有缓存"""
    removed = 0
    for key in list(_cache._cache.keys()):
        if destination in key:
            _cache.delete(key)
            removed += 1

    logger.info(f"清除 {destination} 的缓存: {removed}个")
    return removed


# 导出函数
__all__ = [
    "cache_attraction_data",
    "get_attraction_data",
    "cache_weather_data",
    "get_weather_data",
    "cache_search_results",
    "get_search_results",
    "cache_guide_content",
    "get_guide_content",
    "clear_destination_cache"
]
