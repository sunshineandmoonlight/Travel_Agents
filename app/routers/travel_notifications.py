"""
旅行通知系统 API路由

提供旅行规划相关的通知功能：
- 规划完成通知
- 攻略更新提醒
- 价格提醒
- 系统消息
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/travel/notifications", tags=["旅行通知"])


# ============================================================
# 数据模型
# ============================================================

class NotificationCreate(BaseModel):
    """创建通知请求"""
    title: str = Field(..., max_length=200)
    content: str = Field(..., max_length=2000)
    notification_type: str = Field(..., description="通知类型: plan_completed/guide_updated/price_alert/weather_alert/system")
    priority: str = Field(default="normal", description="优先级: low/normal/high/urgent")
    link: Optional[str] = Field(None, description="相关链接")
    data: Optional[dict] = Field(None, description="附加数据")


class NotificationResponse(BaseModel):
    """通知响应"""
    id: str
    title: str
    content: str
    notification_type: str
    priority: str
    is_read: bool
    link: Optional[str]
    data: Optional[dict]
    created_at: str
    read_at: Optional[str]


class NotificationListResponse(BaseModel):
    """通知列表响应"""
    notifications: List[NotificationResponse]
    total: int
    unread_count: int


# ============================================================
# 内存存储 (生产环境应使用Redis)
# ============================================================

_notifications_store = {}  # {user_id: [notifications]}
_counter = 0


def get_next_id():
    """生成下一个通知ID"""
    global _counter
    _counter += 1
    return f"notif_{_counter}_{datetime.utcnow().timestamp()}"


def get_user_notifications(user_id: int, unread_only: bool = False, limit: int = 50):
    """获取用户通知"""
    user_notifs = _notifications_store.get(user_id, [])
    if unread_only:
        user_notifs = [n for n in user_notifs if not n.get("is_read", False)]
    return user_notifs[:limit]


def mark_notification_read(user_id: int, notif_id: str) -> bool:
    """标记通知为已读"""
    user_notifs = _notifications_store.get(user_id, [])
    for notif in user_notifs:
        if notif["id"] == notif_id:
            notif["is_read"] = True
            notif["read_at"] = datetime.utcnow().isoformat()
            return True
    return False


def get_unread_count(user_id: int) -> int:
    """获取未读数量"""
    user_notifs = _notifications_store.get(user_id, [])
    return sum(1 for n in user_notifs if not n.get("is_read", False))


def create_notification(user_id: int, notif_data: dict) -> dict:
    """创建通知"""
    notif = {
        "id": get_next_id(),
        "user_id": user_id,
        "title": notif_data.get("title"),
        "content": notif_data.get("content"),
        "notification_type": notif_data.get("notification_type", "system"),
        "priority": notif_data.get("priority", "normal"),
        "is_read": False,
        "link": notif_data.get("link"),
        "data": notif_data.get("data"),
        "created_at": datetime.utcnow().isoformat(),
        "read_at": None
    }

    if user_id not in _notifications_store:
        _notifications_store[user_id] = []
    _notifications_store[user_id].insert(0, notif)  # 新通知在前

    return notif


# ============================================================
# API端点
# ============================================================

@router.get("/", response_model=NotificationListResponse)
async def list_notifications(
    status: Optional[str] = Query(None, description="状态: unread/read/all"),
    notification_type: Optional[str] = Query(None, description="通知类型"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: int = 1  # TODO: 从JWT获取
):
    """
    获取通知列表

    参数：
    - status: 筛选状态 (unread/read/all)
    - notification_type: 通知类型筛选
    - page: 页码
    - page_size: 每页数量
    """
    all_notifications = get_user_notifications(user_id)

    # 状态筛选
    if status == "unread":
        notifications = [n for n in all_notifications if not n.get("is_read", False)]
    elif status == "read":
        notifications = [n for n in all_notifications if n.get("is_read", False)]
    else:
        notifications = all_notifications

    # 类型筛选
    if notification_type:
        notifications = [n for n in notifications if n.get("notification_type") == notification_type]

    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    paginated = notifications[start:end]

    return NotificationListResponse(
        notifications=[
            NotificationResponse(**notif) for notif in paginated
        ],
        total=len(notifications),
        unread_count=get_unread_count(user_id)
    )


@router.get("/unread-count")
async def get_unread_count_endpoint(
    user_id: int = 1  # TODO: 从JWT获取
):
    """获取未读通知数量"""
    count = get_unread_count(user_id)
    return {"count": count}


@router.post("/{notif_id}/read")
async def mark_read(
    notif_id: str,
    user_id: int = 1  # TODO: 从JWT获取
):
    """标记通知为已读"""
    success = mark_notification_read(user_id, notif_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"通知不存在: {notif_id}"
        )
    return {"success": True, "message": "已标记为已读"}


@router.post("/read-all")
async def mark_all_read(
    user_id: int = 1  # TODO: 从JWT获取
):
    """标记所有通知为已读"""
    user_notifs = _notifications_store.get(user_id, [])
    count = 0
    for notif in user_notifs:
        if not notif.get("is_read", False):
            notif["is_read"] = True
            notif["read_at"] = datetime.utcnow().isoformat()
            count += 1

    return {"success": True, "updated": count}


@router.delete("/{notif_id}")
async def delete_notification(
    notif_id: str,
    user_id: int = 1  # TODO: 从JWT获取
):
    """删除通知"""
    user_notifs = _notifications_store.get(user_id, [])
    original_length = len(user_notifs)
    _notifications_store[user_id] = [n for n in user_notifs if n["id"] != notif_id]

    if len(_notifications_store[user_id]) == original_length:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"通知不存在: {notif_id}"
        )

    return {"success": True, "message": "通知已删除"}


# ============================================================
# 便捷函数：创建各类通知
# ============================================================

def notify_plan_completed(user_id: int, destination: str, days: int, plan_id: str):
    """规划完成通知"""
    return create_notification(user_id, {
        "title": "✅ 旅行规划已完成",
        "content": f"您的 {destination} {days}天旅行规划已生成，快来查看吧！",
        "notification_type": "plan_completed",
        "priority": "high",
        "link": f"/travel/plan/{plan_id}",
        "data": {"destination": destination, "days": days, "plan_id": plan_id}
    })


def notify_guide_updated(user_id: int, guide_title: str, guide_id: int):
    """攻略更新通知"""
    return create_notification(user_id, {
        "title": "📝 攻略有更新",
        "content": f"您收藏的攻略《{guide_title}》有新的更新",
        "notification_type": "guide_updated",
        "priority": "normal",
        "link": f"/travel/guides/{guide_id}",
        "data": {"guide_title": guide_title, "guide_id": guide_id}
    })


def notify_price_alert(user_id: int, destination: str, original_price: float, current_price: float):
    """价格提醒"""
    discount = ((original_price - current_price) / original_price) * 100
    return create_notification(user_id, {
        "title": "💰 价格下降提醒",
        "content": f"{destination}旅行价格下降 {discount:.1f}%！原价 ¥{original_price}，现价 ¥{current_price}",
        "notification_type": "price_alert",
        "priority": "high",
        "data": {"destination": destination, "original_price": original_price, "current_price": current_price}
    })


def notify_weather_alert(user_id: int, destination: str, weather_condition: str, travel_date: str):
    """天气预警"""
    return create_notification(user_id, {
        "title": "⚠️ 天气预警",
        "content": f"{travel_date} {destination}可能有{weather_condition}，请注意调整行程",
        "notification_type": "weather_alert",
        "priority": "urgent",
        "data": {"destination": destination, "weather": weather_condition, "date": travel_date}
    })


def notify_system_message(user_id: int, title: str, content: str, priority: str = "normal"):
    """系统消息"""
    return create_notification(user_id, {
        "title": title,
        "content": content,
        "notification_type": "system",
        "priority": priority
    })


# 导出便捷函数
__all__ = [
    "notify_plan_completed",
    "notify_guide_updated",
    "notify_price_alert",
    "notify_weather_alert",
    "notify_system_message"
]
