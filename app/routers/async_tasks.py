"""
异步任务API路由

提供异步任务相关的API端点：
- 提交异步任务
- 查询任务状态
- 获取任务结果
- 取消任务
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging

from app.celery_app import celery_app, get_celery_status
from app.tasks.travel_tasks import (
    generate_destinations_task,
    generate_styles_task,
    generate_full_guide_task
)
from app.tasks.guide_tasks import generate_complete_guide_task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/travel/async", tags=["Async-Tasks"])


# ============================================================
# 请求模型
# ============================================================

class TravelRequirement(BaseModel):
    """旅行需求模型"""
    destination_type: str = "domestic"  # domestic/international
    days: int = 3
    budget: str = "medium"
    travelers: int = 2
    travel_type: str = "leisure"
    primary_interests: list = []
    departure_city: str = ""

    class Config:
        extra = "allow"


class GenerateGuideRequest(TravelRequirement):
    """生成攻略请求"""
    destination: Optional[str] = None
    style_type: Optional[str] = None


# ============================================================
# API端点
# ============================================================

@router.get("/status")
async def get_async_status():
    """
    获取异步任务系统状态

    Returns:
        Celery连接状态和配置信息
    """
    status = get_celery_status()

    return {
        "status": "ok",
        "async_system": status,
        "endpoints": {
            "submit_guide": "POST /api/travel/async/generate-guide",
            "check_status": "GET /api/travel/async/tasks/{task_id}",
            "cancel_task": "DELETE /api/travel/async/tasks/{task_id}"
        }
    }


@router.post("/generate-guide")
async def submit_generate_guide(request: GenerateGuideRequest):
    """
    异步生成完整旅行攻略

    Args:
        request: 旅行需求

    Returns:
        任务ID和状态查询URL
    """
    try:
        # 提交异步任务
        task = generate_complete_guide_task.delay(request.dict())

        logger.info(f"✅ 异步任务已提交: {task.id}")

        return {
            "status": "submitted",
            "task_id": task.id,
            "message": "攻略生成任务已提交，请使用task_id查询进度",
            "check_url": f"/api/travel/async/tasks/{task.id}",
            "estimated_time": "30-60秒"
        }

    except Exception as e:
        logger.error(f"提交任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"任务提交失败: {str(e)}")


@router.post("/destinations")
async def submit_destinations(request: TravelRequirement):
    """
    异步生成目的地推荐

    Returns:
        任务ID和状态查询URL
    """
    try:
        task = generate_destinations_task.delay(request.dict())

        return {
            "status": "submitted",
            "task_id": task.id,
            "check_url": f"/api/travel/async/tasks/{task.id}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"任务提交失败: {str(e)}")


@router.post("/styles")
async def submit_styles(destination: str, destination_data: Dict,
                       user_portrait: Dict, days: int):
    """
    异步生成风格方案

    Returns:
        任务ID和状态查询URL
    """
    try:
        task = generate_styles_task.delay(destination, destination_data, user_portrait, days)

        return {
            "status": "submitted",
            "task_id": task.id,
            "check_url": f"/api/travel/async/tasks/{task.id}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"任务提交失败: {str(e)}")


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    查询任务状态

    Args:
        task_id: 任务ID

    Returns:
        任务状态、进度和结果（如果完成）
    """
    try:
        result = celery_app.AsyncResult(task_id)

        response = {
            "task_id": task_id,
            "state": result.state,
        }

        # 处理不同状态
        if result.state == 'PENDING':
            response['message'] = "任务等待中..."
        elif result.state == 'PROGRESS':
            response.update(result.info or {})
            response['message'] = result.info.get('message', '处理中...')
        elif result.state == 'SUCCESS':
            response['result'] = result.result
            response['message'] = "任务完成"
        elif result.state == 'FAILURE':
            response['error'] = str(result.info)
            response['message'] = "任务失败"

        return response

    except Exception as e:
        logger.error(f"查询任务状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.delete("/tasks/{task_id}")
async def cancel_task(task_id: str):
    """
    取消任务

    Args:
        task_id: 任务ID

    Returns:
        取消结果
    """
    try:
        # 撤销任务
        celery_app.control.revoke(task_id, terminate=True)

        return {
            "status": "cancelled",
            "task_id": task_id,
            "message": "任务已取消"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消失败: {str(e)}")


@router.get("/tasks/active")
async def get_active_tasks():
    """
    获取活动任务列表

    Returns:
        当前活动中的任务
    """
    try:
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()

        return {
            "status": "ok",
            "active_tasks": active_tasks or {}
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/workers")
async def get_workers_status():
    """
    获取Worker状态

    Returns:
        Worker列表和状态
    """
    try:
        inspect = celery_app.control.inspect()

        stats = inspect.stats()
        registered = inspect.registered()

        return {
            "status": "ok",
            "workers": {
                "stats": stats or {},
                "registered_tasks": registered or {}
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


__all__ = ["router"]
