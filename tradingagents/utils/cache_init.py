"""
缓存系统初始化模块

在应用启动时自动检测Redis可用性，选择最佳缓存方案。
支持:
- Redis缓存（生产环境推荐）
- 内存缓存（开发环境/Redis不可用时的回退方案）
"""

import logging
import os
from typing import Optional

logger = logging.getLogger("travel_agents.cache")

# 全局缓存类型标志
_cache_type: Optional[str] = None
_redis_available: bool = False


def init_cache_system() -> dict:
    """
    初始化缓存系统

    在应用启动时调用，自动检测Redis并选择缓存方案

    Returns:
        缓存系统状态信息
    """
    global _cache_type, _redis_available

    status = {
        "cache_type": "memory",
        "redis_available": False,
        "redis_configured": False,
        "message": ""
    }

    # 🔥 检查是否强制使用内存缓存
    cache_type = os.getenv("CACHE_TYPE", "").lower()
    if cache_type == "memory":
        _cache_type = "memory"
        _redis_available = False
        status["message"] = "强制使用内存缓存 (CACHE_TYPE=memory)"
        logger.info("✅ 缓存系统初始化成功: 内存模式 (环境变量配置)")
        return status

    # 检查Redis配置
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = os.getenv("REDIS_PORT", "6379")
    redis_password = os.getenv("REDIS_PASSWORD", "")

    status["redis_configured"] = bool(
        os.getenv("REDIS_HOST") or
        os.getenv("REDIS_PORT") or
        os.getenv("REDIS_PASSWORD")
    )

    # 尝试连接Redis
    try:
        import redis

        # 测试连接
        client = redis.Redis(
            host=redis_host,
            port=int(redis_port),
            password=redis_password if redis_password else None,
            db=int(os.getenv("REDIS_CACHE_DB", 1)),
            socket_connect_timeout=2,
            decode_responses=True
        )

        client.ping()
        _redis_available = True
        _cache_type = "redis"

        status["cache_type"] = "redis"
        status["redis_available"] = True
        status["message"] = f"Redis缓存已启用: {redis_host}:{redis_port}"

        logger.info(f"✅ 缓存系统初始化成功: Redis模式 ({redis_host}:{redis_port})")

    except ImportError:
        _cache_type = "memory"
        _redis_available = False
        status["message"] = "redis模块未安装，使用内存缓存"
        logger.warning("⚠️ 缓存系统初始化: 内存模式 (redis未安装)")

    except Exception as e:
        _cache_type = "memory"
        _redis_available = False
        status["message"] = f"Redis连接失败: {e}，使用内存缓存"
        logger.warning(f"⚠️ 缓存系统初始化: 内存模式 (Redis不可用: {e})")

    return status


def get_cache_type() -> str:
    """获取当前缓存类型"""
    return _cache_type or "memory"


def is_redis_available() -> bool:
    """检查Redis是否可用"""
    return _redis_available


def get_cache_manager():
    """
    获取缓存管理器（统一入口）

    根据初始化结果自动返回Redis或内存缓存管理器

    Returns:
        RedisCacheManager 或 ToolCacheManager 实例
    """
    if _redis_available:
        from .redis_cache import RedisCacheManager
        logger.debug("使用 Redis 缓存管理器")
        return RedisCacheManager()
    else:
        from .tool_cache import ToolCacheManager
        logger.debug("使用内存缓存管理器")
        return ToolCacheManager()


# 便捷函数（兼容现有代码）
def get_cache_stats() -> dict:
    """获取缓存统计"""
    manager = get_cache_manager()
    stats = manager.get_stats()
    stats["cache_backend"] = get_cache_type()
    return stats


def clear_cache(pattern: str = "") -> int:
    """清空缓存"""
    manager = get_cache_manager()
    return manager.clear(pattern)


__all__ = [
    "init_cache_system",
    "get_cache_type",
    "is_redis_available",
    "get_cache_manager",
    "get_cache_stats",
    "clear_cache",
]
