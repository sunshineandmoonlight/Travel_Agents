"""
智能降级策略配置

定义API降级的优先级和策略，当主API失败时自动切换到备用方案。
"""

from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    """API提供商状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


@dataclass
class FallbackProvider:
    """降级提供商配置"""
    name: str
    priority: int  # 优先级，1最高
    enabled: bool = True
    check_endpoint: Optional[str] = None
    check_interval: int = 60  # 健康检查间隔（秒）
    failure_count: int = 0
    success_count: int = 0
    last_check: Optional[str] = None
    status: ProviderStatus = ProviderStatus.UNKNOWN

    # 重试配置
    max_retries: int = 3
    retry_delay: int = 5  # 秒
    retry_backoff: float = 2.0  # 指数退避因子

    # 熔断器配置
    circuit_breaker_threshold: int = 5  # 连续失败多少次触发熔断
    circuit_breaker_timeout: int = 60  # 熔断恢复时间（秒）
    is_circuit_open: bool = False
    circuit_opened_at: Optional[float] = None


@dataclass
class FallbackStrategy:
    """降级策略"""
    feature_name: str  # 功能名称（如 weather_forecast）
    description: str  # 描述
    providers: List[FallbackProvider] = field(default_factory=list)
    current_provider_index: int = 0
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    last_call_status: Optional[str] = None

    def get_success_rate(self) -> float:
        """获取成功率"""
        if self.total_calls == 0:
            return 1.0
        return self.successful_calls / self.total_calls


# ============================================================
# 预定义降级策略
# ============================================================

FALLBACK_STRATEGIES: Dict[str, FallbackStrategy] = {
    "weather_forecast": FallbackStrategy(
        feature_name="weather_forecast",
        description="天气预报",
        providers=[
            FallbackProvider(
                name="amap",
                priority=1,
                check_endpoint="https://restapi.amap.com/v3/weather/weatherInfo",
                max_retries=3,
                circuit_breaker_threshold=5
            ),
            FallbackProvider(
                name="openmeteo",
                priority=2,
                check_endpoint="https://api.open-meteo.com/v1/forecast",
                max_retries=2,
                circuit_breaker_threshold=3
            ),
            FallbackProvider(
                name="mock",
                priority=3,
                max_retries=1,
                circuit_breaker_threshold=10
            ),
        ]
    ),

    "attraction_search": FallbackStrategy(
        feature_name="attraction_search",
        description="景点搜索",
        providers=[
            FallbackProvider(
                name="serpapi",
                priority=1,
                check_endpoint="https://serpapi.com/search",
                max_retries=3,
                circuit_breaker_threshold=5
            ),
            FallbackProvider(
                name="opentripmap",
                priority=2,
                check_endpoint="https://api.opentripmap.com/0.1/en/places/geonames",
                max_retries=2,
                circuit_breaker_threshold=3
            ),
            FallbackProvider(
                name="amap",
                priority=3,
                check_endpoint="https://restapi.amap.com/v3/place/text",
                max_retries=2,
                circuit_breaker_threshold=5
            ),
            FallbackProvider(
                name="database",
                priority=4,
                max_retries=1,
                circuit_breaker_threshold=10
            ),
        ]
    ),

    "restaurant_search": FallbackStrategy(
        feature_name="restaurant_search",
        description="餐厅搜索",
        providers=[
            FallbackProvider(
                name="amap",
                priority=1,
                check_endpoint="https://restapi.amap.com/v3/place/text",
                max_retries=3,
                circuit_breaker_threshold=5
            ),
            FallbackProvider(
                name="database",
                priority=2,
                max_retries=1,
                circuit_breaker_threshold=10
            ),
        ]
    ),

    "image_search": FallbackStrategy(
        feature_name="image_search",
        description="图片搜索",
        providers=[
            FallbackProvider(
                name="unsplash",
                priority=1,
                check_endpoint="https://api.unsplash.com/photos",
                max_retries=3,
                circuit_breaker_threshold=5
            ),
            FallbackProvider(
                name="pexels",
                priority=2,
                check_endpoint="https://api.pexels.com/v1/curated",
                max_retries=2,
                circuit_breaker_threshold=3
            ),
            FallbackProvider(
                name="loremflickr",
                priority=3,
                check_endpoint="https://loremflickr.com/g/320/240",
                max_retries=2,
                circuit_breaker_threshold=10
            ),
            FallbackProvider(
                name="placeholder",
                priority=4,
                max_retries=1
            ),
        ]
    ),

    "llm_generation": FallbackStrategy(
        feature_name="llm_generation",
        description="LLM内容生成",
        providers=[
            FallbackProvider(
                name="siliconflow",
                priority=1,
                check_endpoint="https://api.siliconflow.cn/v1/models",
                max_retries=2,
                circuit_breaker_threshold=3
            ),
            FallbackProvider(
                name="deepseek",
                priority=2,
                check_endpoint="https://api.deepseek.com/v1/models",
                max_retries=2,
                circuit_breaker_threshold=3
            ),
            FallbackProvider(
                name="dashscope",
                priority=3,
                check_endpoint="https://dashscope.aliyuncs.com/api/v1/services",
                max_retries=2,
                circuit_breaker_threshold=3
            ),
            FallbackProvider(
                name="template",
                priority=4,
                max_retries=1
            ),
        ]
    ),
}


def get_strategy(feature_name: str) -> Optional[FallbackStrategy]:
    """获取功能的降级策略"""
    return FALLBACK_STRATEGIES.get(feature_name)


def get_all_strategies() -> Dict[str, FallbackStrategy]:
    """获取所有降级策略"""
    return FALLBACK_STRATEGIES.copy()


__all__ = [
    "FallbackProvider",
    "FallbackStrategy",
    "ProviderStatus",
    "get_strategy",
    "get_all_strategies",
    "FALLBACK_STRATEGIES",
]
