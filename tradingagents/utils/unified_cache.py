"""
统一缓存抽象层

自动选择 Redis 或 内存缓存，实现以下特性：
- 生产环境优先使用Redis
- Redis不可用时自动降级到内存缓存
- 统一的API接口
- 无缝切换，无需修改业务代码
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# 尝试导入Redis缓存，失败则使用内存缓存
try:
    from .redis_cache import RedisCacheManager as CacheManager
    logger.info("使用 Redis 缓存管理器")
except ImportError:
    from .tool_cache import ToolCacheManager as CacheManager
    logger.info("Redis不可用，使用内存缓存管理器")


class UnifiedCacheManager(CacheManager):
    """
    统一缓存管理器

    继承自RedisCacheManager或ToolCacheManager，提供统一接口
    自动根据环境选择最佳缓存方案
    """

    def __init__(self):
        super().__init__()
        self.cache_type = "redis" if hasattr(super(), 'use_redis') and super().use_redis else "memory"
        logger.info(f"缓存类型: {self.cache_type}")


# 全局实例
_unified_cache_manager: Optional[UnifiedCacheManager] = None


def get_unified_cache_manager() -> UnifiedCacheManager:
    """获取统一缓存管理器"""
    global _unified_cache_manager
    if _unified_cache_manager is None:
        _unified_cache_manager = UnifiedCacheManager()
    return _unified_cache_manager


# 导出便捷函数
def get_cache(tool_name: str, params: Dict[str, Any], ttl: Optional[int] = None):
    """获取缓存"""
    return get_unified_cache_manager().get(tool_name, params, ttl)


def set_cache(tool_name: str, params: Dict[str, Any], result: Any, ttl: Optional[int] = None):
    """设置缓存"""
    return get_unified_cache_manager().set(tool_name, params, result, ttl)


def clear_cache(pattern: str = "") -> int:
    """清空缓存"""
    return get_unified_cache_manager().clear(pattern)


def get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计"""
    return get_unified_cache_manager().get_stats()


__all__ = [
    "UnifiedCacheManager",
    "get_unified_cache_manager",
    "get_cache",
    "set_cache",
    "clear_cache",
    "get_cache_stats",
]
