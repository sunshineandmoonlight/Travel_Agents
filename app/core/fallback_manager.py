"""
智能降级管理器

实现熔断器模式、自动重试、降级策略管理等功能。
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
from functools import wraps
import httpx

from .fallback_config import (
    FallbackStrategy,
    FallbackProvider,
    ProviderStatus,
    get_strategy,
    get_all_strategies,
    FALLBACK_STRATEGIES,
)

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """熔断器"""

    def __init__(self, provider: FallbackProvider):
        self.provider = provider
        self.failure_count = 0
        self.last_failure_time = None
        self.is_open = False

    def record_success(self):
        """记录成功"""
        self.failure_count = 0
        self.is_open = False
        self.last_failure_time = None
        logger.debug(f"[熔断器] {self.provider.name} 成功，熔断器关闭")

    def record_failure(self):
        """记录失败"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.provider.circuit_breaker_threshold:
            self.is_open = True
            logger.warning(
                f"[熔断器] {self.provider.name} 达到失败阈值 "
                f"({self.failure_count}/{self.provider.circuit_breaker_threshold})，熔断器打开"
            )

    def can_attempt(self) -> bool:
        """检查是否可以尝试请求"""
        if not self.is_open:
            return True

        # 检查是否超过恢复时间
        if self.last_failure_time:
            elapsed = (datetime.now() - self.last_failure_time).total_seconds()
            if elapsed >= self.provider.circuit_breaker_timeout:
                # 半开状态，允许一次尝试
                logger.info(f"[熔断器] {self.provider.name} 熔断器进入半开状态")
                self.is_open = False
                self.failure_count = 0
                return True

        logger.debug(f"[熔断器] {self.provider.name} 熔断器打开，拒绝请求")
        return False


class RetryManager:
    """重试管理器"""

    @staticmethod
    async def execute_with_retry(
        func: Callable,
        provider: FallbackProvider,
        *args,
        **kwargs
    ) -> Any:
        """
        执行带重试的函数

        Args:
            func: 要执行的异步函数
            provider: 提供商配置
            *args, **kwargs: 函数参数

        Returns:
            函数执行结果

        Raises:
            Exception: 所有重试都失败后抛出最后的异常
        """
        last_exception = None
        delay = provider.retry_delay

        for attempt in range(provider.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(
                    f"[重试] {provider.name} 第{attempt + 1}次尝试失败: {str(e)}"
                )

                # 最后一次尝试不再延迟
                if attempt < provider.max_retries - 1:
                    await asyncio.sleep(delay)
                    delay *= provider.retry_backoff

        logger.error(f"[重试] {provider.name} 所有重试均失败")
        raise last_exception


class SmartFallbackManager:
    """智能降级管理器"""

    def __init__(self):
        self.strategies: Dict[str, FallbackStrategy] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._initialize_strategies()

    def _initialize_strategies(self):
        """初始化降级策略"""
        self.strategies = FALLBACK_STRATEGIES.copy()

        # 为每个提供商创建熔断器
        for strategy_name, strategy in self.strategies.items():
            for provider in strategy.providers:
                key = f"{strategy_name}_{provider.name}"
                self.circuit_breakers[key] = CircuitBreaker(provider)

        logger.info(f"[降级管理器] 初始化了 {len(self.strategies)} 个降级策略")

    def get_strategy(self, feature_name: str) -> Optional[FallbackStrategy]:
        """获取功能的降级策略"""
        return self.strategies.get(feature_name)

    async def execute_with_fallback(
        self,
        feature_name: str,
        func_map: Dict[str, Callable],
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行带降级的API调用

        Args:
            feature_name: 功能名称（如 weather_forecast）
            func_map: 提供商名称到执行函数的映射
            *args, **kwargs: 函数参数

        Returns:
            {
                "success": bool,
                "provider": str,
                "data": Any,
                "fallback_used": bool,
                "retry_count": int,
                "execution_time": float
            }
        """
        start_time = time.time()
        strategy = self.get_strategy(feature_name)

        if not strategy:
            logger.warning(f"[降级管理器] 未找到 {feature_name} 的降级策略，使用默认执行")
            # 没有策略，直接执行
            if func_map:
                func = next(iter(func_map.values()))
                try:
                    result = await func(*args, **kwargs)
                    return {"success": True, "data": result, "provider": "default"}
                except Exception as e:
                    return {"success": False, "error": str(e)}

        strategy.total_calls += 1

        # 按优先级尝试每个提供商
        for i, provider in enumerate(strategy.providers):
            if not provider.enabled:
                logger.debug(f"[降级管理器] {provider.name} 已禁用，跳过")
                continue

            provider_key = f"{feature_name}_{provider.name}"
            circuit_breaker = self.circuit_breakers.get(provider_key)

            # 检查熔断器
            if circuit_breaker and not circuit_breaker.can_attempt():
                logger.warning(
                    f"[降级管理器] {provider.name} 熔断器打开，跳过"
                )
                continue

            # 检查是否有对应的执行函数
            if provider.name not in func_map:
                logger.debug(
                    f"[降级管理器] {provider.name} 没有对应的执行函数，跳过"
                )
                continue

            # 执行API调用
            try:
                logger.info(f"[降级管理器] 尝试使用 {provider.name} (优先级 {provider.priority})")

                # 使用重试机制执行
                result = await RetryManager.execute_with_retry(
                    func_map[provider.name],
                    provider,
                    *args,
                    **kwargs
                )

                # 成功
                execution_time = time.time() - start_time
                strategy.successful_calls += 1
                strategy.last_call_status = f"{provider.name}_success"
                strategy.current_provider_index = i

                # 更新提供商状态
                provider.status = ProviderStatus.HEALTHY
                provider.success_count += 1
                provider.failure_count = 0

                # 记录熔断器成功
                if circuit_breaker:
                    circuit_breaker.record_success()

                logger.info(
                    f"[降级管理器] {provider.name} 执行成功 "
                    f"(耗时{execution_time:.2f}秒)"
                )

                return {
                    "success": True,
                    "provider": provider.name,
                    "data": result,
                    "fallback_used": i > 0,
                    "execution_time": execution_time,
                    "retry_count": 0
                }

            except Exception as e:
                logger.warning(
                    f"[降级管理器] {provider.name} 执行失败: {str(e)}"
                )

                # 更新提供商状态
                provider.status = ProviderStatus.DOWN
                provider.failure_count += 1
                provider.success_count = 0

                # 记录熔断器失败
                if circuit_breaker:
                    circuit_breaker.record_failure()

                # 继续尝试下一个提供商
                continue

        # 所有提供商都失败
        execution_time = time.time() - start_time
        strategy.failed_calls += 1
        strategy.last_call_status = "all_failed"

        logger.error(
            f"[降级管理器] {feature_name} 所有提供商均失败，"
            f"尝试了 {len(strategy.providers)} 个提供商"
        )

        return {
            "success": False,
            "provider": None,
            "error": "All providers failed",
            "fallback_used": True,
            "execution_time": execution_time,
            "available_providers": [p.name for p in strategy.providers]
        }

    def get_status(self) -> Dict[str, Any]:
        """获取降级系统状态"""
        strategies_status = []

        for name, strategy in self.strategies.items():
            providers_status = []
            for provider in strategy.providers:
                circuit_breaker = self.circuit_breakers.get(f"{name}_{provider.name}")

                providers_status.append({
                    "name": provider.name,
                    "priority": provider.priority,
                    "enabled": provider.enabled,
                    "status": provider.status.value,
                    "failure_count": provider.failure_count,
                    "success_count": provider.success_count,
                    "is_circuit_open": circuit_breaker.is_open if circuit_breaker else False,
                    "check_endpoint": provider.check_endpoint
                })

            strategies_status.append({
                "feature_name": name,
                "description": strategy.description,
                "total_calls": strategy.total_calls,
                "successful_calls": strategy.successful_calls,
                "failed_calls": strategy.failed_calls,
                "success_rate": strategy.get_success_rate(),
                "current_provider": strategy.providers[strategy.current_provider_index].name if strategy.providers else None,
                "last_call_status": strategy.last_call_status,
                "providers": providers_status
            })

        return {
            "status": "ok",
            "strategies": strategies_status,
            "total_strategies": len(self.strategies)
        }

    def enable_provider(self, feature_name: str, provider_name: str):
        """启用提供商"""
        strategy = self.get_strategy(feature_name)
        if strategy:
            for provider in strategy.providers:
                if provider.name == provider_name:
                    provider.enabled = True
                    logger.info(f"[降级管理器] 启用 {feature_name} 的 {provider_name}")
                    return True
        return False

    def disable_provider(self, feature_name: str, provider_name: str):
        """禁用提供商"""
        strategy = self.get_strategy(feature_name)
        if strategy:
            for provider in strategy.providers:
                if provider.name == provider_name:
                    provider.enabled = False
                    logger.info(f"[降级管理器] 禁用 {feature_name} 的 {provider_name}")
                    return True
        return False

    def reset_circuit_breaker(self, feature_name: str, provider_name: str):
        """重置熔断器"""
        key = f"{feature_name}_{provider_name}"
        if key in self.circuit_breakers:
            circuit_breaker = self.circuit_breakers[key]
            circuit_breaker.is_open = False
            circuit_breaker.failure_count = 0
            logger.info(f"[降级管理器] 重置 {feature_name}/{provider_name} 的熔断器")
            return True
        return False


# 全局降级管理器实例
_fallback_manager: Optional[SmartFallbackManager] = None


def get_fallback_manager() -> SmartFallbackManager:
    """获取全局降级管理器"""
    global _fallback_manager
    if _fallback_manager is None:
        _fallback_manager = SmartFallbackManager()
    return _fallback_manager


def reset_fallback_manager():
    """重置全局降级管理器"""
    global _fallback_manager
    _fallback_manager = None
    logger.info("[降级管理器] 重置全局降级管理器")


__all__ = [
    "SmartFallbackManager",
    "CircuitBreaker",
    "RetryManager",
    "get_fallback_manager",
    "reset_fallback_manager",
]
