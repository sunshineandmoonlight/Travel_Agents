"""
热门目的地图片URL缓存服务

在内存/Redis中缓存热门城市的图片URL，避免频繁调用外部API
"""

import logging
import time
import asyncio
from typing import Dict, Optional
from datetime import datetime, timedelta
from threading import Lock

logger = logging.getLogger(__name__)


class DestinationImageCache:
    """目的地图片缓存服务"""

    def __init__(self):
        # 内存缓存：{city: {"url": str, "source": str, "updated_at": timestamp}}
        self._cache: Dict[str, Dict] = {}
        self._lock = Lock()
        self._cache_ttl = 86400  # 缓存有效期：24小时（秒）
        self._last_refresh = 0
        self._is_refreshing = False

        # 统计信息
        self._stats = {
            "hits": 0,           # 缓存命中次数
            "misses": 0,         # 缓存未命中次数
            "refreshes": 0,      # 刷新次数
            "errors": 0          # 错误次数
        }

    def get(self, city: str) -> Optional[Dict]:
        """
        从缓存获取城市图片URL

        Args:
            city: 城市名称

        Returns:
            {"url": str, "source": str, "updated_at": timestamp} 或 None
        """
        with self._lock:
            cached = self._cache.get(city)

            if cached:
                # 检查是否过期
                age = time.time() - cached["updated_at"]
                if age < self._cache_ttl:
                    self._stats["hits"] += 1
                    logger.debug(f"缓存命中: {city} (年龄: {age:.0f}秒)")
                    return cached.copy()
                else:
                    # 过期，删除
                    logger.info(f"缓存过期: {city} (年龄: {age:.0f}秒)")
                    del self._cache[city]

            self._stats["misses"] += 1
            return None

    def set(self, city: str, url: str, source: str = "unknown") -> None:
        """
        设置城市图片URL到缓存

        Args:
            city: 城市名称
            url: 图片URL
            source: 图片来源 (unsplash, pexels, placeholder)
        """
        with self._lock:
            self._cache[city] = {
                "url": url,
                "source": source,
                "updated_at": time.time()
            }
            logger.debug(f"缓存更新: {city} -> {source}")

    def delete(self, city: str) -> bool:
        """删除指定城市的缓存"""
        with self._lock:
            if city in self._cache:
                del self._cache[city]
                logger.info(f"缓存删除: {city}")
                return True
            return False

    def clear(self) -> int:
        """清空所有缓存"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"缓存已清空: {count}条")
            return count

    def get_all(self) -> Dict[str, Dict]:
        """获取所有缓存（只读）"""
        with self._lock:
            return {k: v.copy() for k, v in self._cache.items()}

    def size(self) -> int:
        """获取缓存大小"""
        return len(self._cache)

    def get_stats(self) -> Dict:
        """获取缓存统计信息"""
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0

            return {
                **self._stats,
                "size": len(self._cache),
                "hit_rate": f"{hit_rate:.1f}%",
                "ttl_hours": self._cache_ttl / 3600,
                "last_refresh": datetime.fromtimestamp(self._last_refresh).isoformat() if self._last_refresh else None,
                "next_refresh": datetime.fromtimestamp(self._last_refresh + self._cache_ttl).isoformat() if self._last_refresh else None
            }

    def needs_refresh(self) -> bool:
        """检查是否需要刷新缓存"""
        age = time.time() - self._last_refresh
        return age >= self._cache_ttl

    async def refresh_popular_destinations(
        self,
        cities: list,
        fetch_func: callable,
        force: bool = False
    ) -> Dict:
        """
        刷新热门城市缓存

        Args:
            cities: 城市列表
            fetch_func: 获取图片URL的函数，签名为 fetch_func(city) -> (url, source)
            force: 是否强制刷新（忽略TTL检查）

        Returns:
            {"success": int, "failed": int, "total": int}
        """
        if not force and not self.needs_refresh():
            logger.info("缓存未过期，跳过刷新")
            return {
                "success": 0,
                "failed": 0,
                "total": 0,
                "skipped": True
            }

        if self._is_refreshing:
            logger.warning("缓存刷新正在进行中，跳过")
            return {
                "success": 0,
                "failed": 0,
                "total": 0,
                "skipped": True,
                "reason": "already_refreshing"
            }

        self._is_refreshing = True
        self._stats["refreshes"] += 1

        logger.info(f"开始刷新热门城市缓存: {len(cities)}个城市")
        start_time = time.time()

        success = 0
        failed = 0
        errors = []

        for city in cities:
            try:
                # 调用获取函数
                url, source = await fetch_func(city)

                # 更新缓存
                self.set(city, url, source)
                success += 1

            except Exception as e:
                failed += 1
                self._stats["errors"] += 1
                error_msg = f"{city}: {str(e)}"
                errors.append(error_msg)
                logger.warning(f"刷新失败: {error_msg}")

        self._last_refresh = time.time()
        self._is_refreshing = False

        elapsed = time.time() - start_time

        logger.info(
            f"缓存刷新完成: 成功{success}, 失败{failed}, "
            f"耗时{elapsed:.1f}秒, 当前缓存{self.size()}条"
        )

        return {
            "success": success,
            "failed": failed,
            "total": len(cities),
            "elapsed": elapsed,
            "errors": errors[:10]  # 只返回前10个错误
        }


# 全局单例
_cache_instance: Optional[DestinationImageCache] = None
_cache_lock = Lock()


def get_destination_image_cache() -> DestinationImageCache:
    """获取缓存服务单例"""
    global _cache_instance

    if _cache_instance is None:
        with _cache_lock:
            if _cache_instance is None:
                _cache_instance = DestinationImageCache()
                logger.info("目的地图片缓存服务已初始化")

    return _cache_instance


async def initialize_popular_destinations_cache():
    """
    初始化热门目的地缓存

    在应用启动时调用，预加载热门城市图片URL到缓存
    """
    from tradingagents.config.popular_destinations import get_top_destinations
    from tradingagents.services.attraction_image_service import get_attraction_image

    cache = get_destination_image_cache()

    # 如果缓存已存在且未过期，跳过
    if not cache.needs_refresh() and cache.size() > 0:
        logger.info(f"缓存已存在: {cache.size()}条，跳过初始化")
        return

    # 定义异步获取函数
    async def fetch_image_url(city: str):
        # 在线程池中执行同步的API调用
        import asyncio
        loop = asyncio.get_event_loop()
        url = await loop.run_in_executor(
            None,
            lambda: get_attraction_image(city, city, 600, 400)
        )

        # 判断来源
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

        return url, source

    # 获取TOP 20城市
    cities = get_top_destinations(20)

    logger.info(f"开始初始化热门目的地缓存: {len(cities)}个城市")
    result = await cache.refresh_popular_destinations(cities, fetch_image_url, force=True)

    logger.info(
        f"热门目的地缓存初始化完成: "
        f"成功{result['success']}, 失败{result['failed']}, "
        f"耗时{result.get('elapsed', 0):.1f}秒"
    )

    return result


def schedule_cache_refresh():
    """
    安排定期刷新缓存

    应该在应用启动时调用，启动后台任务定期刷新
    """
    import threading

    def refresh_worker():
        cache = get_destination_image_cache()
        while True:
            try:
                # 检查是否需要刷新
                if cache.needs_refresh():
                    logger.info("定时任务：开始刷新缓存")

                    # 使用asyncio运行异步刷新
                    import asyncio
                    asyncio.run(initialize_popular_destinations_cache())

                # 每小时检查一次
                import time
                time.sleep(3600)

            except Exception as e:
                logger.error(f"定时刷新缓存失败: {e}")
                import time
                time.sleep(3600)

    # 启动后台线程
    thread = threading.Thread(
        target=refresh_worker,
        daemon=True,
        name="DestinationImageCacheRefresh"
    )
    thread.start()

    logger.info("缓存定期刷新任务已启动")
