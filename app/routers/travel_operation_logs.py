"""
旅行操作日志 API路由

记录用户在旅行规划系统中的所有操作：
- 规划创建
- 攻略保存/修改
- 收藏/点赞
- 导出操作
等
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/travel/logs", tags=["旅行操作日志"])


# ============================================================
# 数据模型
# ============================================================

class TravelOperationLog(BaseModel):
    """旅行操作日志"""
    id: str
    user_id: int
    username: str
    action_type: str  # plan_created/guide_saved/guide_deleted/favorited/liked/exported/searched
    action_description: str
    resource_type: Optional[str]  # plan/guide/destination
    resource_id: Optional[str]
    resource_name: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_data: Optional[Dict[str, Any]]
    response_data: Optional[Dict[str, Any]]
    success: bool
    error_message: Optional[str]
    duration_ms: Optional[int]
    created_at: str


class OperationLogQuery(BaseModel):
    """操作日志查询"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    action_type: Optional[str] = None
    resource_type: Optional[str] = None
    success: Optional[bool] = None
    keyword: Optional[str] = None
    page: int = 1
    page_size: int = 20


class OperationLogListResponse(BaseModel):
    """操作日志列表响应"""
    logs: List[TravelOperationLog]
    total: int
    page: int
    page_size: int
    total_pages: int


class OperationLogStats(BaseModel):
    """操作日志统计"""
    total_operations: int
    operations_by_type: Dict[str, int]
    operations_by_date: Dict[str, int]
    success_rate: float
    avg_duration_ms: float
    most_active_users: List[Dict[str, Any]]
    most_used_resources: List[Dict[str, Any]]


# ============================================================
# 内存存储 (生产环境应使用数据库)
# ============================================================

_logs_store = []
_log_counter = 0


def add_log(log_data: dict) -> dict:
    """添加操作日志"""
    global _log_counter, _logs_store
    _log_counter += 1

    log = {
        "id": f"log_{_log_counter}_{datetime.utcnow().timestamp()}",
        "created_at": datetime.utcnow().isoformat(),
        **log_data
    }

    _logs_store.insert(0, log)  # 新日志在前

    # 限制存储数量
    if len(_logs_store) > 10000:
        _logs_store = _logs_store[:10000]

    return log


def query_logs(query: OperationLogQuery) -> tuple[list, int]:
    """查询操作日志"""
    logs = _logs_store.copy()

    # 日期筛选
    if query.start_date:
        try:
            start_dt = datetime.fromisoformat(query.start_date)
            logs = [log for log in logs if datetime.fromisoformat(log["created_at"]) >= start_dt]
        except:
            pass

    if query.end_date:
        try:
            end_dt = datetime.fromisoformat(query.end_date)
            logs = [log for log in logs if datetime.fromisoformat(log["created_at"]) <= end_dt]
        except:
            pass

    # 类型筛选
    if query.action_type:
        logs = [log for log in logs if log.get("action_type") == query.action_type]

    if query.resource_type:
        logs = [log for log in logs if log.get("resource_type") == query.resource_type]

    # 成功筛选
    if query.success is not None:
        logs = [log for log in logs if log.get("success") == query.success]

    # 关键词搜索
    if query.keyword:
        keyword_lower = query.keyword.lower()
        logs = [
            log for log in logs
            if keyword_lower in log.get("action_description", "").lower() or
               keyword_lower in log.get("resource_name", "").lower() or
               keyword_lower in log.get("username", "").lower()
        ]

    total = len(logs)

    # 分页
    start = (query.page - 1) * query.page_size
    end = start + query.page_size
    paginated_logs = logs[start:end]

    return paginated_logs, total


def get_stats(days: int = 30) -> dict:
    """获取统计信息"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    recent_logs = [
        log for log in _logs_store
        if datetime.fromisoformat(log["created_at"]) >= cutoff_date
    ]

    # 按类型统计
    operations_by_type = {}
    for log in recent_logs:
        action_type = log.get("action_type", "unknown")
        operations_by_type[action_type] = operations_by_type.get(action_type, 0) + 1

    # 按日期统计
    operations_by_date = {}
    for log in recent_logs:
        date = log["created_at"][:10]
        operations_by_date[date] = operations_by_date.get(date, 0) + 1

    # 成功率
    success_count = sum(1 for log in recent_logs if log.get("success", True))
    success_rate = success_count / len(recent_logs) if recent_logs else 1.0

    # 平均耗时
    durations = [log.get("duration_ms", 0) for log in recent_logs if log.get("duration_ms")]
    avg_duration = sum(durations) / len(durations) if durations else 0

    # 最活跃用户
    user_activity = {}
    for log in recent_logs:
        user_id = log.get("user_id", 0)
        user_activity[user_id] = user_activity.get(user_id, 0) + 1

    most_active_users = [
        {"user_id": uid, "username": next((log["username"] for log in _logs_store if log.get("user_id") == uid), "unknown"), "count": count}
        for uid, count in sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10]
    ]

    # 最常用资源
    resource_usage = {}
    for log in recent_logs:
        resource = log.get("resource_name", "unknown")
        if resource:
            resource_usage[resource] = resource_usage.get(resource, 0) + 1

    most_used_resources = [
        {"resource": resource, "count": count}
        for resource, count in sorted(resource_usage.items(), key=lambda x: x[1], reverse=True)[:10]
    ]

    return {
        "total_operations": len(recent_logs),
        "operations_by_type": operations_by_type,
        "operations_by_date": operations_by_date,
        "success_rate": success_rate,
        "avg_duration_ms": avg_duration,
        "most_active_users": most_active_users,
        "most_used_resources": most_used_resources
    }


# ============================================================
# API端点
# ============================================================

@router.get("/list", response_model=OperationLogListResponse)
async def get_operation_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    action_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    success: Optional[bool] = None,
    keyword: Optional[str] = None
):
    """获取操作日志列表"""
    query = OperationLogQuery(
        start_date=start_date,
        end_date=end_date,
        action_type=action_type,
        resource_type=resource_type,
        success=success,
        keyword=keyword,
        page=page,
        page_size=page_size
    )

    logs, total = query_logs(query)

    return OperationLogListResponse(
        logs=[TravelOperationLog(**log) for log in logs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/stats", response_model=OperationLogStats)
async def get_operation_log_stats(
    days: int = Query(30, ge=1, le=365)
):
    """获取操作日志统计"""
    stats_data = get_stats(days)
    return OperationLogStats(**stats_data)


@router.get("/action-types")
async def get_action_types():
    """获取所有操作类型"""
    return {
        "action_types": [
            {"value": "plan_created", "label": "创建规划", "category": "planning"},
            {"value": "plan_completed", "label": "规划完成", "category": "planning"},
            {"value": "guide_created", "label": "创建攻略", "category": "guide"},
            {"value": "guide_updated", "label": "更新攻略", "category": "guide"},
            {"value": "guide_deleted", "label": "删除攻略", "category": "guide"},
            {"value": "guide_copied", "label": "复制攻略", "category": "guide"},
            {"value": "guide_exported", "label": "导出攻略", "category": "guide"},
            {"value": "favorited", "label": "收藏", "category": "interaction"},
            {"value": "unfavorited", "label": "取消收藏", "category": "interaction"},
            {"value": "liked", "label": "点赞", "category": "interaction"},
            {"value": "unliked", "label": "取消点赞", "category": "interaction"},
            {"value": "searched", "label": "搜索", "category": "search"},
            {"value": "reviewed", "label": "评论", "category": "interaction"},
            {"value": "shared", "label": "分享", "category": "interaction"},
        ]
    }


@router.delete("/cleanup")
async def cleanup_old_logs(
    days: int = Query(90, ge=30, le=365, description="清理多少天前的日志")
):
    """清理旧日志"""
    global _logs_store

    cutoff_date = datetime.utcnow() - timedelta(days=days)
    original_count = len(_logs_store)

    _logs_store = [
        log for log in _logs_store
        if datetime.fromisoformat(log["created_at"]) >= cutoff_date
    ]

    deleted_count = original_count - len(_logs_store)

    return {
        "success": True,
        "message": f"已清理 {deleted_count} 条旧日志",
        "deleted_count": deleted_count,
        "remaining_count": len(_logs_store)
    }


# ============================================================
# 便捷函数：记录各类操作
# ============================================================

def log_plan_created(
    user_id: int,
    username: str,
    destination: str,
    days: int,
    plan_id: str,
    duration_ms: int = 0
):
    """记录规划创建"""
    global _logs_store
    return add_log({
        "user_id": user_id,
        "username": username,
        "action_type": "plan_created",
        "action_description": f"创建 {destination} {days}天旅行规划",
        "resource_type": "plan",
        "resource_id": plan_id,
        "resource_name": f"{destination} {days}天游",
        "success": True,
        "duration_ms": duration_ms
    })


def log_plan_completed(
    user_id: int,
    username: str,
    destination: str,
    days: int,
    plan_id: str,
    duration_ms: int
):
    """记录规划完成"""
    return add_log({
        "user_id": user_id,
        "username": username,
        "action_type": "plan_completed",
        "action_description": f"完成 {destination} {days}天旅行规划",
        "resource_type": "plan",
        "resource_id": plan_id,
        "resource_name": f"{destination} {days}天游",
        "success": True,
        "duration_ms": duration_ms
    })


def log_guide_saved(
    user_id: int,
    username: str,
    guide_title: str,
    guide_id: int
):
    """记录攻略保存"""
    return add_log({
        "user_id": user_id,
        "username": username,
        "action_type": "guide_created",
        "action_description": f"保存攻略: {guide_title}",
        "resource_type": "guide",
        "resource_id": str(guide_id),
        "resource_name": guide_title,
        "success": True
    })


def log_guide_exported(
    user_id: int,
    username: str,
    guide_title: str,
    guide_id: int,
    format_type: str = "pdf"
):
    """记录攻略导出"""
    return add_log({
        "user_id": user_id,
        "username": username,
        "action_type": "guide_exported",
        "action_description": f"导出攻略: {guide_title} ({format_type.upper()})",
        "resource_type": "guide",
        "resource_id": str(guide_id),
        "resource_name": guide_title,
        "success": True
    })


def log_favorited(
    user_id: int,
    username: str,
    resource_type: str,
    resource_id: str,
    resource_name: str
):
    """记录收藏操作"""
    return add_log({
        "user_id": user_id,
        "username": username,
        "action_type": "favorited",
        "action_description": f"收藏{resource_type}: {resource_name}",
        "resource_type": resource_type,
        "resource_id": resource_id,
        "resource_name": resource_name,
        "success": True
    })


def log_searched(
    user_id: int,
    username: str,
    keyword: str,
    result_count: int
):
    """记录搜索操作"""
    return add_log({
        "user_id": user_id,
        "username": username,
        "action_type": "searched",
        "action_description": f"搜索: {keyword}",
        "resource_type": "search",
        "resource_name": keyword,
        "success": True,
        "response_data": {"result_count": result_count}
    })


# 导出便捷函数
__all__ = [
    "log_plan_created",
    "log_plan_completed",
    "log_guide_saved",
    "log_guide_exported",
    "log_favorited",
    "log_searched"
]
