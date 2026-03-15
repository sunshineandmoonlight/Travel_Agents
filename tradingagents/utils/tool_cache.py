"""
工具调用缓存管理器

为智能体工具调用提供缓存机制，避免重复API调用，节省费用和时间。
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from functools import wraps

logger = logging.getLogger('travel_agents')


class ToolCacheManager:
    """
    工具调用缓存管理器

    功能：
    1. 缓存工具调用结果
    2. 支持 TTL（过期时间）
    3. 支持缓存统计
    4. 支持手动清理
    """

    def __init__(self, default_ttl: int = 3600):
        """
        初始化缓存管理器

        Args:
            default_ttl: 默认缓存有效期（秒），默认1小时
        """
        self._cache: Dict[str, tuple] = {}  # {key: (result, expires_at, metadata)}
        self.default_ttl = default_ttl
        self._stats = {
            "hits": 0,          # 缓存命中次数
            "misses": 0,        # 缓存未命中次数
            "total_requests": 0 # 总请求次数
        }

    def _generate_cache_key(self, tool_name: str, params: Dict[str, Any]) -> str:
        """
        生成缓存键

        Args:
            tool_name: 工具名称
            params: 调用参数

        Returns:
            缓存键（MD5哈希）
        """
        # 对参数进行排序，确保相同参数生成相同的key
        params_str = json.dumps(params, sort_keys=True)
        key_str = f"{tool_name}:{params_str}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(
        self,
        tool_name: str,
        params: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> Optional[Any]:
        """
        获取缓存结果

        Args:
            tool_name: 工具名称
            params: 调用参数
            ttl: 可选的缓存有效期检查

        Returns:
            缓存的结果，如果不存在或已过期则返回 None
        """
        self._stats["total_requests"] += 1

        cache_key = self._generate_cache_key(tool_name, params)

        if cache_key not in self._cache:
            self._stats["misses"] += 1
            logger.debug(f"[缓存未命中] {tool_name} | key: {cache_key[:16]}...")
            return None

        result, expires_at, metadata = self._cache[cache_key]

        # 检查是否过期
        now = datetime.now()
        if ttl:
            # 使用指定的TTL检查
            expiry_time = metadata["cached_at"] + timedelta(seconds=ttl)
            if now > expiry_time:
                self._remove(cache_key)
                self._stats["misses"] += 1
                logger.debug(f"[缓存过期] {tool_name} | key: {cache_key[:16]}...")
                return None

        if now > expires_at:
            self._remove(cache_key)
            self._stats["misses"] += 1
            logger.debug(f"[缓存过期] {tool_name} | key: {cache_key[:16]}...")
            return None

        # 缓存命中
        self._stats["hits"] += 1
        logger.info(f"[缓存命中] {tool_name} | key: {cache_key[:16]}... | 年龄: {(now - metadata['cached_at']).seconds}s")
        return result

    def set(
        self,
        tool_name: str,
        params: Dict[str, Any],
        result: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        设置缓存结果

        Args:
            tool_name: 工具名称
            params: 调用参数
            result: 要缓存的结果
            ttl: 缓存有效期（秒），默认使用 default_ttl
        """
        cache_key = self._generate_cache_key(tool_name, params)

        # 使用指定的TTL或默认TTL
        ttl = ttl if ttl is not None else self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)

        # 存储结果和元数据
        metadata = {
            "tool_name": tool_name,
            "cached_at": datetime.now(),
            "params": params
        }

        self._cache[cache_key] = (result, expires_at, metadata)

        logger.info(f"[缓存存储] {tool_name} | key: {cache_key[:16]}... | TTL: {ttl}s")

    def _remove(self, cache_key: str) -> None:
        """移除缓存条目"""
        if cache_key in self._cache:
            del self._cache[cache_key]

    def clear(self, pattern: Optional[str] = None) -> int:
        """
        清空缓存

        Args:
            pattern: 可选的工具名模式，如果指定则只清理匹配工具的缓存

        Returns:
            清理的缓存条目数
        """
        if pattern:
            # 清理特定工具的缓存
            keys_to_remove = []
            for key, (_, _, metadata) in self._cache.items():
                if metadata["tool_name"] == pattern:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self._cache[key]

            count = len(keys_to_remove)
            logger.info(f"[缓存清理] 清理 {pattern} 的 {count} 条缓存")
            return count
        else:
            # 清理所有缓存
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"[缓存清理] 清理所有 {count} 条缓存")
            return count

    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            统计信息字典
        """
        total = self._stats["total_requests"]
        hits = self._stats["hits"]
        misses = self._stats["misses"]

        hit_rate = (hits / total * 100) if total > 0 else 0

        return {
            "total_requests": total,
            "hits": hits,
            "misses": misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "cache_size": len(self._cache),
            "default_ttl": self.default_ttl
        }

    def preload_cache(self, cache_data: Dict[str, Dict]) -> None:
        """
        预加载缓存数据

        Args:
            cache_data: {tool_name: {params: result, ttl: ...}}
        """
        count = 0
        for tool_name, items in cache_data.items():
            for params, result_with_ttl in items.items():
                if isinstance(result_with_ttl, dict):
                    result = result_with_ttl.get("result")
                    ttl = result_with_ttl.get("ttl", self.default_ttl)
                else:
                    result = result_with_ttl
                    ttl = self.default_ttl

                self.set(tool_name, params, result, ttl)
                count += 1

        logger.info(f"[缓存预加载] 加载了 {count} 条缓存数据")


# ============================================================
# 全局缓存管理器实例
# ============================================================

# 全局单例
_global_cache_manager: Optional[ToolCacheManager] = None


def get_cache_manager() -> ToolCacheManager:
    """获取全局缓存管理器实例"""
    global _global_cache_manager
    if _global_cache_manager is None:
        _global_cache_manager = ToolCacheManager()
        logger.info("[缓存管理器] 创建全局缓存管理器")
    return _global_cache_manager


def reset_cache_manager() -> None:
    """重置全局缓存管理器"""
    global _global_cache_manager
    _global_cache_manager = None
    logger.info("[缓存管理器] 重置全局缓存管理器")


# ============================================================
# 装饰器：自动缓存工具调用结果
# ============================================================

def cached_tool_call(tool_name: Optional[str] = None, ttl: Optional[int] = None):
    """
    工具调用缓存装饰器

    使用方式：
    @cached_tool_call("weather_forecast", ttl=1800)
    def get_weather(city: str, days: int):
        ...

    Args:
        tool_name: 工具名称，如果为None则使用函数名
        ttl: 缓存有效期（秒）
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取缓存管理器
            cache_manager = get_cache_manager()

            # 确定工具名称
            name = tool_name or func.__name__

            # 构建参数字典（用于生成缓存键）
            # 假设第一个参数后的关键字参数作为缓存键
            params = kwargs if kwargs else {}

            # 尝试从缓存获取
            cached_result = cache_manager.get(name, params, ttl)
            if cached_result is not None:
                return cached_result

            # 缓存未命中，调用实际函数
            result = func(*args, **kwargs)

            # 存入缓存
            if result is not None:
                cache_manager.set(name, params, result, ttl)

            return result

        return wrapper
    return decorator


# ============================================================
# 常用工具的缓存配置
# ============================================================

# 不同工具的推荐TTL
CACHE_TTL_CONFIG = {
    "weather_forecast": 1800,     # 天气：30分钟
    "attraction_search": 3600,     # 景点搜索：1小时
    "restaurant_search": 3600,     # 餐厅搜索：1小时
    "route_planning": 7200,        # 路径规划：2小时
    "destination_search": 86400,   # 目的地搜索：24小时
    "image_search": 604800,        # 图片搜索：7天
}


def get_ttl_for_tool(tool_name: str) -> int:
    """获取工具推荐的TTL"""
    return CACHE_TTL_CONFIG.get(tool_name, 3600)


__all__ = [
    "ToolCacheManager",
    "get_cache_manager",
    "reset_cache_manager",
    "cached_tool_call",
    "get_ttl_for_tool",
    "CACHE_TTL_CONFIG",
]
