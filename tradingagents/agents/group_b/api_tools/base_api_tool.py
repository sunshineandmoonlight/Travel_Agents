"""
API工具基类

定义所有API工具的通用接口和功能
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import hashlib
import json

logger = logging.getLogger('travel_agents')


class BaseAPITool(ABC):
    """API工具基类

    提供统一的接口和缓存机制，子类实现具体的API调用
    """

    def __init__(self, api_key: str = None, cache_ttl: int = 3600):
        """
        初始化API工具

        Args:
            api_key: API密钥
            cache_ttl: 缓存有效期（秒），默认1小时
        """
        self.api_key = api_key
        self.cache_ttl = cache_ttl
        self._cache = {}  # 缓存存储: {key: (data, expires_at)}

    @abstractmethod
    async def search_attractions(
        self,
        destination: str,
        keywords: str,
        days: int,
        style: str
    ) -> List[Dict[str, Any]]:
        """
        搜索景点

        Args:
            destination: 目的地名称
            keywords: 搜索关键词
            days: 旅行天数
            style: 旅行风格 (immersive/exploration/relaxation/hidden_gem)

        Returns:
            景点列表，每个景点包含name, address, coordinates等字段
        """
        pass

    @abstractmethod
    async def get_attraction_details(self, attraction_id: str) -> Dict[str, Any]:
        """
        获取景点详情

        Args:
            attraction_id: 景点ID

        Returns:
            景点详细信息
        """
        pass

    def _get_cache_key(self, method: str, **kwargs) -> str:
        """
        生成缓存键

        Args:
            method: 方法名
            **kwargs: 参数

        Returns:
            缓存键字符串
        """
        # 对参数进行排序，确保相同参数生成相同的key
        params_str = json.dumps(kwargs, sort_keys=True)
        key_str = f"{method}:{params_str}"
        return hashlib.md5(key_str.encode()).hexdigest()

    async def _cached_call(self, key: str, func):
        """
        带缓存的异步调用

        Args:
            key: 缓存键
            func: 异步函数

        Returns:
            函数结果（来自缓存或实际调用）
        """
        now = datetime.now()

        # 检查缓存
        if key in self._cache:
            data, expires_at = self._cache[key]
            if now < expires_at:
                logger.info(f"[缓存命中] {key[:16]}...")
                return data
            else:
                # 缓存已过期，删除
                del self._cache[key]
                logger.info(f"[缓存过期] {key[:16]}...")

        # 调用函数获取数据
        result = await func()

        # 存入缓存
        expires_at = now + timedelta(seconds=self.cache_ttl)
        self._cache[key] = (result, expires_at)
        logger.info(f"[缓存存储] {key[:16]}..., 过期时间: {expires_at.strftime('%H:%M:%S')}")

        return result

    def _is_available(self) -> bool:
        """检查API是否可用"""
        return self.api_key is not None and self.api_key != ""

    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        logger.info("[缓存] 已清空所有缓存")

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        now = datetime.now()
        valid_count = sum(1 for _, expires_at in self._cache.values() if now < expires_at)
        expired_count = len(self._cache) - valid_count

        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_count,
            "expired_entries": expired_count,
            "cache_ttl": self.cache_ttl
        }


class APIToolException(Exception):
    """API工具异常基类"""
    pass


class APIKeyMissingException(APIToolException):
    """API密钥缺失异常"""
    pass


class APICallException(APIToolException):
    """API调用异常"""
    pass
