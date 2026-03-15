"""
Redis缓存管理器 - 生产环境推荐

支持:
- 多实例共享缓存
- 自动过期清理
- 数据持久化
- 丰富的数据结构
"""

import json
import hashlib
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)

# 全局Redis客户端实例
_redis_client = None


def get_redis_client():
    """获取Redis客户端（延迟初始化）"""
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    try:
        import redis
        import os

        # 从环境变量读取配置
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        redis_password = os.getenv("REDIS_PASSWORD", "")
        redis_db = int(os.getenv("REDIS_CACHE_DB", 1))  # 使用DB1，DB0给session

        # 创建连接池
        pool = redis.ConnectionPool(
            host=redis_host,
            port=redis_port,
            password=redis_password if redis_password else None,
            db=redis_db,
            decode_responses=True,  # 自动解码为字符串
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            max_connections=50
        )

        _redis_client = redis.Redis(connection_pool=pool)

        # 测试连接
        _redis_client.ping()

        logger.info(f"✅ Redis缓存已连接: {redis_host}:{redis_port}/DB{redis_db}")
        return _redis_client

    except ImportError:
        logger.warning("⚠️ redis模块未安装，使用内存缓存回退 (pip install redis)")
        return None
    except Exception as e:
        logger.warning(f"⚠️ Redis连接失败: {e}，使用内存缓存回退")
        return None


class RedisCacheManager:
    """Redis缓存管理器"""

    # TTL配置（秒）
    CACHE_TTL_CONFIG = {
        "weather_forecast": 1800,      # 30分钟
        "attraction_search": 3600,     # 1小时
        "restaurant_search": 3600,     # 1小时
        "route_planning": 7200,        # 2小时
        "destination_search": 86400,   # 24小时
        "image_search": 604800,        # 7天
        "llm_response": 3600,          # LLM响应 1小时
        "api_response": 1800,          # API响应 30分钟
    }

    def __init__(self):
        self.client = get_redis_client()
        self.use_redis = self.client is not None
        self._stats = {
            "hits": 0,
            "misses": 0,
            "total_requests": 0
        }

        if not self.use_redis:
            logger.info("使用内存缓存回退方案")
            self._memory_cache: Dict[str, tuple] = {}  # (value, expires_at)

    def _generate_cache_key(self, tool_name: str, params: Dict[str, Any]) -> str:
        """生成缓存键"""
        # 对参数进行排序后生成JSON，确保顺序不影响结果
        params_json = json.dumps(params, sort_keys=True, ensure_ascii=False)
        params_hash = hashlib.md5(params_json.encode('utf-8')).hexdigest()[:12]

        # 格式: tool_name:params_hash
        return f"cache:{tool_name}:{params_hash}"

    def _is_expired(self, expires_at: Optional[datetime]) -> bool:
        """检查是否过期"""
        if expires_at is None:
            return False
        return datetime.now() > expires_at

    def get_ttl_for_tool(self, tool_name: str) -> int:
        """获取工具对应的TTL"""
        return self.CACHE_TTL_CONFIG.get(tool_name, 3600)

    def get(self, tool_name: str, params: Dict[str, Any],
            ttl: Optional[int] = None) -> Optional[Any]:
        """
        获取缓存结果

        Args:
            tool_name: 工具名称
            params: 参数字典
            ttl: 过期时间（秒），None则使用工具默认TTL

        Returns:
            缓存结果，未命中返回None
        """
        self._stats["total_requests"] += 1
        cache_key = self._generate_cache_key(tool_name, params)

        try:
            if self.use_redis:
                # Redis模式
                value = self.client.get(cache_key)
                if value:
                    self._stats["hits"] += 1
                    return json.loads(value)
                else:
                    self._stats["misses"] += 1
                    return None
            else:
                # 内存缓存回退
                if cache_key in self._memory_cache:
                    value, expires_at = self._memory_cache[cache_key]

                    if not self._is_expired(expires_at):
                        self._stats["hits"] += 1
                        return value
                    else:
                        # 过期，删除
                        del self._memory_cache[cache_key]

                self._stats["misses"] += 1
                return None

        except Exception as e:
            logger.warning(f"缓存读取失败: {e}")
            self._stats["misses"] += 1
            return None

    def set(self, tool_name: str, params: Dict[str, Any],
            result: Any, ttl: Optional[int] = None) -> None:
        """
        设置缓存

        Args:
            tool_name: 工具名称
            params: 参数字典
            result: 要缓存的结果
            ttl: 过期时间（秒），None则使用工具默认TTL
        """
        cache_key = self._generate_cache_key(tool_name, params)

        # 确定TTL
        if ttl is None:
            ttl = self.get_ttl_for_tool(tool_name)

        try:
            if self.use_redis:
                # Redis模式 - 自动过期
                value_json = json.dumps(result, ensure_ascii=False)
                self.client.setex(cache_key, ttl, value_json)
            else:
                # 内存缓存回退
                expires_at = datetime.now() + timedelta(seconds=ttl)
                self._memory_cache[cache_key] = (result, expires_at)

                # 定期清理过期缓存（简单策略）
                if len(self._memory_cache) > 1000:
                    self._cleanup_expired()

        except Exception as e:
            logger.warning(f"缓存写入失败: {e}")

    def delete(self, tool_name: str, params: Dict[str, Any]) -> bool:
        """删除指定缓存"""
        cache_key = self._generate_cache_key(tool_name, params)

        try:
            if self.use_redis:
                return bool(self.client.delete(cache_key))
            else:
                if cache_key in self._memory_cache:
                    del self._memory_cache[cache_key]
                    return True
                return False
        except Exception as e:
            logger.warning(f"缓存删除失败: {e}")
            return False

    def clear(self, pattern: str = "") -> int:
        """
        清空缓存

        Args:
            pattern: 匹配模式，如 "weather:" 只清理天气相关缓存
                     空字符串则清空所有缓存

        Returns:
            清理的缓存数量
        """
        try:
            if self.use_redis:
                if pattern:
                    # 使用SCAN避免阻塞
                    keys = []
                    for key in self.client.scan_iter(match=f"cache:{pattern}*"):
                        keys.append(key)
                    if keys:
                        return self.client.delete(*keys)
                    return 0
                else:
                    # 清空所有cache:开头的键
                    keys = []
                    for key in self.client.scan_iter(match="cache:*"):
                        keys.append(key)
                    if keys:
                        return self.client.delete(*keys)
                    return 0
            else:
                if pattern:
                    keys_to_delete = [k for k in self._memory_cache.keys() if pattern in k]
                    for key in keys_to_delete:
                        del self._memory_cache[key]
                    return len(keys_to_delete)
                else:
                    count = len(self._memory_cache)
                    self._memory_cache.clear()
                    return count

        except Exception as e:
            logger.warning(f"缓存清理失败: {e}")
            return 0

    def _cleanup_expired(self):
        """清理过期的内存缓存"""
        now = datetime.now()
        expired_keys = [
            k for k, (_, expires_at) in self._memory_cache.items()
            if expires_at and now > expires_at
        ]
        for key in expired_keys:
            del self._memory_cache[key]

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        hit_rate = 0.0
        if self._stats["total_requests"] > 0:
            hit_rate = self._stats["hits"] / self._stats["total_requests"]

        cache_size = 0
        if self.use_redis:
            try:
                cache_size = len(list(self.client.scan_iter(match="cache:*")))
            except:
                pass
        else:
            cache_size = len(self._memory_cache)

        return {
            "cache_type": "redis" if self.use_redis else "memory",
            "total_requests": self._stats["total_requests"],
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "hit_rate": round(hit_rate, 3),
            "cache_size": cache_size,
            "default_ttl": self.CACHE_TTL_CONFIG
        }

    def get_all_keys(self, pattern: str = "cache:*") -> List[str]:
        """获取所有缓存键"""
        if self.use_redis:
            try:
                return list(self.client.scan_iter(match=pattern))
            except:
                return []
        else:
            return [k for k in self._memory_cache.keys() if pattern.replace("cache:", "") in k]


# 全局缓存管理器实例
_cache_manager: Optional[RedisCacheManager] = None


def get_cache_manager() -> RedisCacheManager:
    """获取缓存管理器（单例模式）"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = RedisCacheManager()
    return _cache_manager


def cached_tool_call(tool_name: str, ttl: Optional[int] = None):
    """
    缓存装饰器

    Usage:
        @cached_tool_call("attraction_search", ttl=3600)
        def search_attractions(destination: str, keywords: str):
            return api_results
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成参数字典
            params = {}
            if args:
                # 尝试从函数签名获取参数名
                import inspect
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                params = dict(bound_args.arguments)
            else:
                params = kwargs

            # 检查缓存
            cache_manager = get_cache_manager()
            cached_result = cache_manager.get(tool_name, params, ttl)
            if cached_result is not None:
                logger.debug(f"缓存命中: {tool_name}")
                return cached_result

            # 调用函数
            result = func(*args, **kwargs)

            # 保存到缓存
            if result is not None:
                cache_manager.set(tool_name, params, result, ttl)

            return result

        return wrapper
    return decorator


def get_ttl_for_tool(tool_name: str) -> int:
    """获取工具对应的TTL（便捷函数）"""
    return RedisCacheManager.CACHE_TTL_CONFIG.get(tool_name, 3600)


__all__ = [
    "RedisCacheManager",
    "get_cache_manager",
    "cached_tool_call",
    "get_ttl_for_tool",
    "get_redis_client",
]
