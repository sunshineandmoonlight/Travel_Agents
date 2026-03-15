"""
旅行任务队列 API路由

管理后台任务：
- 旅行规划任务
- 攻略生成任务
- 数据同步任务
- 报告生成任务
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/travel/queue", tags=["旅行任务队列"])


# ============================================================
# 数据模型
# ============================================================

class TaskStatus(BaseModel):
    """任务状态"""
    id: str
    task_type: str  # plan_generation/guide_generation/data_sync/report_export
    task_name: str
    description: str
    status: str  # pending/running/completed/failed/cancelled
    progress: float  # 0-100
    current_step: str
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    user_id: int
    metadata: Optional[Dict[str, Any]]


class TaskListResponse(BaseModel):
    """任务列表响应"""
    tasks: List[TaskStatus]
    total: int
    running: int
    pending: int
    completed: int
    failed: int


class TaskStatsResponse(BaseModel):
    """任务统计响应"""
    total_tasks: int
    status_distribution: Dict[str, int]
    type_distribution: Dict[str, int]
    avg_completion_time: float
    success_rate: float
    recent_tasks: List[Dict[str, Any]]


# ============================================================
# 内存存储 (生产环境应使用Redis/Celery)
# ============================================================

_tasks_store = {}  # {task_id: task}
_task_counter = 0


def get_next_task_id():
    """生成下一个任务ID"""
    global _task_counter
    _task_counter += 1
    return f"task_{_task_counter}_{datetime.utcnow().timestamp()}"


def create_task(
    task_type: str,
    task_name: str,
    description: str,
    user_id: int,
    metadata: Optional[Dict[str, Any]] = None
) -> dict:
    """创建新任务"""
    task_id = get_next_task_id()

    task = {
        "id": task_id,
        "task_type": task_type,
        "task_name": task_name,
        "description": description,
        "status": "pending",
        "progress": 0.0,
        "current_step": "等待开始",
        "result": None,
        "error": None,
        "created_at": datetime.utcnow().isoformat(),
        "started_at": None,
        "completed_at": None,
        "user_id": user_id,
        "metadata": metadata or {}
    }

    _tasks_store[task_id] = task
    logger.info(f"创建任务: {task_id} - {task_name}")

    return task


def update_task(task_id: str, **updates):
    """更新任务状态"""
    if task_id not in _tasks_store:
        return False

    task = _tasks_store[task_id]

    for key, value in updates.items():
        task[key] = value

    return True


def get_user_tasks(user_id: int, status_filter: Optional[str] = None) -> list:
    """获取用户任务列表"""
    tasks = list(_tasks_store.values())
    tasks = [t for t in tasks if t.get("user_id") == user_id]

    if status_filter:
        tasks = [t for t in tasks if t.get("status") == status_filter]

    tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return tasks


def get_task_stats() -> dict:
    """获取任务统计"""
    tasks = list(_tasks_store.values())

    # 状态分布
    status_distribution = {}
    for task in tasks:
        status = task.get("status", "unknown")
        status_distribution[status] = status_distribution.get(status, 0) + 1

    # 类型分布
    type_distribution = {}
    for task in tasks:
        task_type = task.get("task_type", "unknown")
        type_distribution[task_type] = type_distribution.get(task_type, 0) + 1

    # 平均完成时间
    completed_tasks = [t for t in tasks if t.get("status") == "completed" and t.get("started_at") and t.get("completed_at")]
    completion_times = []
    for task in completed_tasks:
        try:
            started = datetime.fromisoformat(task["started_at"])
            completed = datetime.fromisoformat(task["completed_at"])
            completion_times.append((completed - started).total_seconds())
        except:
            pass

    avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0

    # 成功率
    success_count = len([t for t in tasks if t.get("status") == "completed"])
    total_finished = len([t for t in tasks if t.get("status") in ["completed", "failed"]])
    success_rate = success_count / total_finished if total_finished > 0 else 1.0

    # 最近任务
    recent_tasks = sorted(tasks, key=lambda x: x.get("created_at", ""), reverse=True)[:10]
    recent_tasks = [
        {
            "id": t["id"],
            "task_name": t["task_name"],
            "status": t["status"],
            "progress": t["progress"],
            "created_at": t["created_at"]
        }
        for t in recent_tasks
    ]

    return {
        "total_tasks": len(tasks),
        "status_distribution": status_distribution,
        "type_distribution": type_distribution,
        "avg_completion_time": avg_completion_time,
        "success_rate": success_rate,
        "recent_tasks": recent_tasks
    }


# ============================================================
# API端点
# ============================================================

@router.get("/stats", response_model=TaskStatsResponse)
async def get_queue_stats():
    """获取队列统计信息"""
    stats = get_task_stats()
    return TaskStatsResponse(**stats)


@router.get("/tasks", response_model=TaskListResponse)
async def get_tasks(
    user_id: int = Query(1, description="用户ID"),
    status: Optional[str] = Query(None, description="状态筛选"),
    task_type: Optional[str] = Query(None, description="类型筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """获取任务列表"""
    tasks = list(_tasks_store.values())

    # 用户筛选
    tasks = [t for t in tasks if t.get("user_id") == user_id]

    # 状态筛选
    if status:
        tasks = [t for t in tasks if t.get("status") == status]

    # 类型筛选
    if task_type:
        tasks = [t for t in tasks if t.get("task_type") == task_type]

    # 排序
    tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    total = len(tasks)

    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    paginated_tasks = tasks[start:end]

    # 统计
    all_user_tasks = [t for t in _tasks_store.values() if t.get("user_id") == user_id]

    return TaskListResponse(
        tasks=[TaskStatus(**t) for t in paginated_tasks],
        total=total,
        running=len([t for t in all_user_tasks if t.get("status") == "running"]),
        pending=len([t for t in all_user_tasks if t.get("status") == "pending"]),
        completed=len([t for t in all_user_tasks if t.get("status") == "completed"]),
        failed=len([t for t in all_user_tasks if t.get("status") == "failed"])
    )


@router.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task_detail(task_id: str):
    """获取任务详情"""
    if task_id not in _tasks_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务不存在: {task_id}"
        )

    return TaskStatus(**_tasks_store[task_id])


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str, user_id: int = 1):
    """取消任务"""
    if task_id not in _tasks_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务不存在: {task_id}"
        )

    task = _tasks_store[task_id]

    if task.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限取消此任务"
        )

    if task.get("status") in ["completed", "failed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"任务已{task.get('status')}，无法取消"
        )

    task["status"] = "cancelled"
    task["completed_at"] = datetime.utcnow().isoformat()

    logger.info(f"取消任务: {task_id}")

    return {"success": True, "message": "任务已取消"}


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, user_id: int = 1):
    """删除任务记录"""
    if task_id not in _tasks_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务不存在: {task_id}"
        )

    task = _tasks_store[task_id]

    if task.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除此任务"
        )

    del _tasks_store[task_id]

    return {"success": True, "message": "任务已删除"}


@router.post("/cleanup")
async def cleanup_old_tasks(
    days: int = Query(7, ge=1, le=30, description="清理多少天前的已完成任务")
):
    """清理旧任务"""
    from datetime import timedelta

    cutoff_date = datetime.utcnow() - timedelta(days=days)
    original_count = len(_tasks_store)

    to_delete = []
    for task_id, task in _tasks_store.items():
        if task.get("status") in ["completed", "failed", "cancelled"]:
            try:
                created_at = datetime.fromisoformat(task["created_at"])
                if created_at < cutoff_date:
                    to_delete.append(task_id)
            except:
                pass

    for task_id in to_delete:
        del _tasks_store[task_id]

    return {
        "success": True,
        "message": f"已清理 {len(to_delete)} 个旧任务",
        "deleted_count": len(to_delete),
        "remaining_count": len(_tasks_store)
    }


# ============================================================
# 便捷函数：创建各类任务
# ============================================================

def create_plan_generation_task(
    user_id: int,
    destination: str,
    days: int,
    budget: str,
    travelers: int
) -> str:
    """创建规划生成任务"""
    task = create_task(
        task_type="plan_generation",
        task_name=f"生成 {destination} {days}天旅行规划",
        description=f"为 {travelers} 人规划 {destination} {days}天行程，预算{budget}",
        user_id=user_id,
        metadata={
            "destination": destination,
            "days": days,
            "budget": budget,
            "travelers": travelers
        }
    )
    return task["id"]


def create_guide_export_task(
    user_id: int,
    guide_id: int,
    guide_title: str,
    export_format: str = "pdf"
) -> str:
    """创建攻略导出任务"""
    task = create_task(
        task_type="guide_export",
        task_name=f"导出攻略: {guide_title}",
        description=f"将攻略《{guide_title}》导出为 {export_format.upper()} 格式",
        user_id=user_id,
        metadata={
            "guide_id": guide_id,
            "guide_title": guide_title,
            "export_format": export_format
        }
    )
    return task["id"]


def create_data_sync_task(
    user_id: int,
    sync_type: str,  # attractions/weather/transportation
    destination: Optional[str] = None
) -> str:
    """创建数据同步任务"""
    if destination:
        task_name = f"同步 {destination} 数据"
        description = f"更新 {destination} 的{sync_type}数据"
    else:
        task_name = f"同步 {sync_type} 数据"
        description = f"更新所有{sync_type}数据"

    task = create_task(
        task_type="data_sync",
        task_name=task_name,
        description=description,
        user_id=user_id,
        metadata={
            "sync_type": sync_type,
            "destination": destination
        }
    )
    return task["id"]


def update_task_progress(task_id: str, progress: float, current_step: str):
    """更新任务进度"""
    return update_task(
        task_id,
        progress=progress,
        current_step=current_step
    )


def complete_task(task_id: str, result: Optional[Dict[str, Any]] = None):
    """完成任务"""
    return update_task(
        task_id,
        status="completed",
        progress=100.0,
        current_step="已完成",
        result=result,
        completed_at=datetime.utcnow().isoformat()
    )


def fail_task(task_id: str, error: str):
    """标记任务失败"""
    return update_task(
        task_id,
        status="failed",
        current_step="失败",
        error=error,
        completed_at=datetime.utcnow().isoformat()
    )


# 模拟任务执行
async def simulate_task_execution(task_id: str):
    """模拟任务执行（用于演示）"""
    task = _tasks_store.get(task_id)
    if not task:
        return

    # 开始执行
    update_task(
        task_id,
        status="running",
        started_at=datetime.utcnow().isoformat()
    )

    # 模拟进度
    steps = [
        (20, "初始化"),
        (40, "收集数据"),
        (60, "分析处理"),
        (80, "生成结果"),
        (100, "完成")
    ]

    for progress, step in steps:
        await asyncio.sleep(1)
        update_task_progress(task_id, progress, step)

    # 完成
    complete_task(task_id, {"message": "任务执行成功"})


# 导出函数
__all__ = [
    "create_plan_generation_task",
    "create_guide_export_task",
    "create_data_sync_task",
    "update_task_progress",
    "complete_task",
    "fail_task",
    "simulate_task_execution"
]
