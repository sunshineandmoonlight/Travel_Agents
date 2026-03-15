"""
降级管理API

提供降级系统监控、管理和配置的API端点。
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging

from app.core.fallback_manager import get_fallback_manager
from app.core.fallback_config import get_strategy, get_all_strategies

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/fallback", tags=["Fallback"])


# ============================================================
# 请求/响应模型
# ============================================================

class ProviderToggleRequest(BaseModel):
    """提供商启用/禁用请求"""
    provider_name: str
    enabled: bool


class CircuitBreakerResetRequest(BaseModel):
    """熔断器重置请求"""
    provider_name: str


# ============================================================
# API端点
# ============================================================

@router.get("/status")
async def get_fallback_status():
    """
    获取降级系统状态

    Returns:
        降级系统整体状态，包括所有策略和提供商状态
    """
    try:
        manager = get_fallback_manager()
        return manager.get_status()
    except Exception as e:
        logger.error(f"获取降级状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies")
async def list_strategies():
    """
    列出所有降级策略

    Returns:
        所有功能的降级策略配置
    """
    try:
        strategies = get_all_strategies()

        result = []
        for name, strategy in strategies.items():
            providers = []
            for provider in strategy.providers:
                providers.append({
                    "name": provider.name,
                    "priority": provider.priority,
                    "enabled": provider.enabled,
                    "status": provider.status.value,
                    "max_retries": provider.max_retries,
                    "circuit_breaker_threshold": provider.circuit_breaker_threshold,
                    "retry_delay": provider.retry_delay,
                })

            result.append({
                "feature_name": name,
                "description": strategy.description,
                "providers": providers,
                "total_calls": strategy.total_calls,
                "successful_calls": strategy.successful_calls,
                "failed_calls": strategy.failed_calls,
                "success_rate": strategy.get_success_rate(),
                "current_provider": strategy.providers[strategy.current_provider_index].name if strategy.providers else None,
            })

        return {
            "status": "ok",
            "strategies": result,
            "total": len(result)
        }

    except Exception as e:
        logger.error(f"获取策略列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies/{feature_name}")
async def get_strategy_detail(feature_name: str):
    """
    获取特定功能的降级策略详情

    Args:
        feature_name: 功能名称

    Returns:
        策略详情
    """
    try:
        strategy = get_strategy(feature_name)
        if not strategy:
            raise HTTPException(status_code=404, detail=f"未找到功能: {feature_name}")

        providers = []
        for provider in strategy.providers:
            providers.append({
                "name": provider.name,
                "priority": provider.priority,
                "enabled": provider.enabled,
                "status": provider.status.value,
                "check_endpoint": provider.check_endpoint,
                "max_retries": provider.max_retries,
                "retry_delay": provider.retry_delay,
                "retry_backoff": provider.retry_backoff,
                "circuit_breaker_threshold": provider.circuit_breaker_threshold,
                "circuit_breaker_timeout": provider.circuit_breaker_timeout,
            })

        return {
            "status": "ok",
            "feature_name": feature_name,
            "description": strategy.description,
            "providers": providers,
            "statistics": {
                "total_calls": strategy.total_calls,
                "successful_calls": strategy.successful_calls,
                "failed_calls": strategy.failed_calls,
                "success_rate": strategy.get_success_rate(),
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取策略详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/strategies/{feature_name}/providers/{provider_name}/toggle")
async def toggle_provider(feature_name: str, provider_name: str, request: ProviderToggleRequest):
    """
    启用或禁用提供商

    Args:
        feature_name: 功能名称
        provider_name: 提供商名称
        request: 启用/禁用请求

    Returns:
        操作结果
    """
    try:
        manager = get_fallback_manager()

        if request.enabled:
            success = manager.enable_provider(feature_name, provider_name)
        else:
            success = manager.disable_provider(feature_name, provider_name)

        if success:
            return {
                "status": "ok",
                "message": f"已{'启用' if request.enabled else '禁用'} {provider_name}",
                "feature_name": feature_name,
                "provider_name": provider_name,
                "enabled": request.enabled
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"未找到 {feature_name} 的 {provider_name} 提供商"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换提供商状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/strategies/{feature_name}/providers/{provider_name}/reset-circuit")
async def reset_circuit_breaker(feature_name: str, provider_name: str):
    """
    重置熔断器

    Args:
        feature_name: 功能名称
        provider_name: 提供商名称

    Returns:
        操作结果
    """
    try:
        manager = get_fallback_manager()
        success = manager.reset_circuit_breaker(feature_name, provider_name)

        if success:
            return {
                "status": "ok",
                "message": f"已重置 {feature_name}/{provider_name} 的熔断器",
                "feature_name": feature_name,
                "provider_name": provider_name
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"未找到 {feature_name} 的 {provider_name} 熔断器"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重置熔断器失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def check_health():
    """
    检查降级系统健康状态

    Returns:
        各功能的健康状态
    """
    try:
        manager = get_fallback_manager()
        status = manager.get_status()

        # 计算健康指标
        healthy_strategies = 0
        degraded_strategies = 0
        total_providers = 0
        healthy_providers = 0

        for strategy in status.get("strategies", []):
            total_providers += len(strategy.get("providers", []))
            healthy_providers += sum(
                1 for p in strategy.get("providers", [])
                if p.get("status") == "healthy"
            )

            if strategy.get("success_rate", 1.0) >= 0.8:
                healthy_strategies += 1
            elif strategy.get("success_rate", 1.0) >= 0.5:
                degraded_strategies += 1

        overall_health = "healthy"
        if degraded_strategies > len(status.get("strategies", [])) / 2:
            overall_health = "degraded"
        if healthy_providers < total_providers / 2:
            overall_health = "unhealthy"

        return {
            "status": "ok",
            "health": overall_health,
            "summary": {
                "total_strategies": len(status.get("strategies", [])),
                "healthy_strategies": healthy_strategies,
                "degraded_strategies": degraded_strategies,
                "total_providers": total_providers,
                "healthy_providers": healthy_providers,
                "provider_health_rate": healthy_providers / total_providers if total_providers > 0 else 0,
            },
            "details": status
        }

    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ["router"]
