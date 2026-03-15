"""
旅行消息中心 API路由

提供旅行相关的内部消息推送：
- 旅行小贴士
- 目的地预警
- 活动推荐
- 节日提醒
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/travel/messages", tags=["旅行消息中心"])


# ============================================================
# 数据模型
# ============================================================

class TravelMessage(BaseModel):
    """旅行消息"""
    id: str
    message_type: str  # tip/alert/promotion/holiday/system
    title: str
    content: str
    summary: Optional[str] = ""
    category: str
    subcategory: Optional[str] = ""
    tags: List[str] = []
    priority: str = "normal"  # low/normal/high/urgent
    importance: str = "medium"
    target_type: str = "all"  # all/user/destination
    target_id: Optional[str] = None
    link: Optional[str] = None
    image_url: Optional[str] = None
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    created_at: str
    is_read: bool = False


class MessageListResponse(BaseModel):
    """消息列表响应"""
    messages: List[TravelMessage]
    total: int
    unread_count: int


class MessageStatsResponse(BaseModel):
    """消息统计响应"""
    total_messages: int
    unread_count: int
    by_type: Dict[str, int]
    by_priority: Dict[str, int]
    recent_messages: List[Dict[str, Any]]


# ============================================================
# 内存存储
# ============================================================

_messages_store = []
_message_counter = 0


def get_next_message_id():
    """生成下一个消息ID"""
    global _message_counter
    _message_counter += 1
    return f"msg_{_message_counter}_{datetime.utcnow().timestamp()}"


def create_message(message_data: dict) -> dict:
    """创建消息"""
    message = {
        "id": get_next_message_id(),
        "created_at": datetime.utcnow().isoformat(),
        "is_read": False,
        **message_data
    }

    _messages_store.insert(0, message)
    return message


def get_user_messages(
    user_id: int,
    message_type: Optional[str] = None,
    unread_only: bool = False,
    limit: int = 50
) -> list:
    """获取用户消息"""
    messages = _messages_store.copy()

    # 筛选有效消息
    now = datetime.utcnow()
    messages = [
        m for m in messages
        if m.get("target_type") == "all" or m.get("target_id") == str(user_id)
    ]

    # 时间有效性筛选
    messages = [
        m for m in messages
        if not m.get("valid_until") or datetime.fromisoformat(m["valid_until"]) >= now
    ]

    # 类型筛选
    if message_type:
        messages = [m for m in messages if m.get("message_type") == message_type]

    # 已读筛选
    if unread_only:
        messages = [m for m in messages if not m.get("is_read", False)]

    return messages[:limit]


def mark_message_read(message_id: str) -> bool:
    """标记消息为已读"""
    for message in _messages_store:
        if message["id"] == message_id:
            message["is_read"] = True
            return True
    return False


def get_message_stats() -> dict:
    """获取消息统计"""
    total = len(_messages_store)
    unread = len([m for m in _messages_store if not m.get("is_read", False)])

    # 按类型统计
    by_type = {}
    for m in _messages_store:
        msg_type = m.get("message_type", "unknown")
        by_type[msg_type] = by_type.get(msg_type, 0) + 1

    # 按优先级统计
    by_priority = {}
    for m in _messages_store:
        priority = m.get("priority", "normal")
        by_priority[priority] = by_priority.get(priority, 0) + 1

    # 最近消息
    recent = [
        {
            "id": m["id"],
            "title": m["title"],
            "message_type": m["message_type"],
            "priority": m["priority"],
            "created_at": m["created_at"]
        }
        for m in _messages_store[:10]
    ]

    return {
        "total_messages": total,
        "unread_count": unread,
        "by_type": by_type,
        "by_priority": by_priority,
        "recent_messages": recent
    }


# ============================================================
# API端点
# ============================================================

@router.get("/", response_model=MessageListResponse)
async def get_messages(
    message_type: Optional[str] = None,
    unread_only: bool = False,
    user_id: int = 1,
    limit: int = Query(50, ge=1, le=100)
):
    """获取消息列表"""
    messages = get_user_messages(user_id, message_type, unread_only, limit)
    unread_count = len([m for m in get_user_messages(user_id) if not m.get("is_read", False)])

    return MessageListResponse(
        messages=[TravelMessage(**m) for m in messages],
        total=len(messages),
        unread_count=unread_count
    )


@router.get("/stats", response_model=MessageStatsResponse)
async def get_stats():
    """获取消息统计"""
    stats = get_message_stats()
    return MessageStatsResponse(**stats)


@router.post("/{message_id}/read")
async def mark_read(message_id: str):
    """标记消息为已读"""
    success = mark_message_read(message_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"消息不存在: {message_id}"
        )

    return {"success": True, "message": "已标记为已读"}


@router.post("/read-all")
async def mark_all_read():
    """标记所有消息为已读"""
    count = 0
    for message in _messages_store:
        if not message.get("is_read", False):
            message["is_read"] = True
            count += 1

    return {"success": True, "updated": count}


@router.delete("/{message_id}")
async def delete_message(message_id: str):
    """删除消息"""
    global _messages_store
    original_count = len(_messages_store)
    _messages_store = [m for m in _messages_store if m["id"] != message_id]

    if len(_messages_store) == original_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"消息不存在: {message_id}"
        )

    return {"success": True, "message": "消息已删除"}


# ============================================================
# 便捷函数：创建各类消息
# ============================================================

def send_travel_tip(
    title: str,
    content: str,
    category: str = "general",
    destination: Optional[str] = None
):
    """发送旅行小贴士"""
    return create_message({
        "message_type": "tip",
        "title": f"💡 {title}",
        "content": content,
        "summary": content[:100] + "..." if len(content) > 100 else content,
        "category": category,
        "priority": "normal",
        "importance": "low",
        "target_type": "all",
        "tags": ["旅行贴士", category]
    })


def send_destination_alert(
    destination: str,
    alert_type: str,  # weather/traffic/event
    title: str,
    content: str,
    valid_until: Optional[str] = None
):
    """发送目的地预警"""
    return create_message({
        "message_type": "alert",
        "title": f"⚠️ {destination} - {title}",
        "content": content,
        "summary": f"{destination}最新消息",
        "category": "alert",
        "subcategory": alert_type,
        "priority": "high",
        "importance": "high",
        "target_type": "destination",
        "target_id": destination,
        "tags": ["预警", destination],
        "valid_until": valid_until
    })


def send_promotion(
    title: str,
    content: str,
    link: Optional[str] = None,
    image_url: Optional[str] = None,
    valid_until: Optional[str] = None
):
    """发送推广消息"""
    return create_message({
        "message_type": "promotion",
        "title": f"🎉 {title}",
        "content": content,
        "summary": "限时优惠",
        "category": "promotion",
        "priority": "normal",
        "importance": "low",
        "target_type": "all",
        "link": link,
        "image_url": image_url,
        "tags": ["优惠", "推荐"],
        "valid_until": valid_until
    })


def send_holiday_reminder(
    holiday_name: str,
    date: str,
    content: str,
    destinations: Optional[List[str]] = None
):
    """发送节日提醒"""
    return create_message({
        "message_type": "holiday",
        "title": f"🎊 {holiday_name}旅行提醒",
        "content": content,
        "summary": f"{holiday_name}就要到了",
        "category": "holiday",
        "priority": "normal",
        "importance": "medium",
        "target_type": "all",
        "tags": ["节日", holiday_name] + (destinations or []),
        "valid_until": date
    })


def send_system_message(
    title: str,
    content: str,
    priority: str = "normal"
):
    """发送系统消息"""
    return create_message({
        "message_type": "system",
        "title": f"📢 {title}",
        "content": content,
        "summary": "系统通知",
        "category": "system",
        "priority": priority,
        "importance": "high" if priority == "urgent" else "medium",
        "target_type": "all",
        "tags": ["系统"]
    })


# 初始化默认消息
def init_default_messages():
    """初始化默认消息"""
    default_messages = [
        send_travel_tip(
            "旅行打包技巧",
            "学会打包是旅行的重要技能。将重物放在底部，常用物品放在顶部，记得准备雨具和常用药品。",
            category="packing"
        ),
        send_travel_tip(
            "安全旅行建议",
            "保管好贵重物品，提前了解目的地安全情况，购买旅行保险，保持与家人的联系。",
            category="safety"
        ),
        send_travel_tip(
            "摄影技巧分享",
            "黄金时段（日出后和日落前1小时）光线最佳。记得携带备用电池和存储卡。",
            category="photography"
        ),
        send_holiday_reminder(
            "五一劳动节",
            "2026-05-01",
            "五一假期即将到来，提前规划你的假期旅行，享受美好时光！",
            destinations=["三亚", "厦门", "桂林"]
        ),
        send_holiday_reminder(
            "端午节",
            "2026-06-03",
            "端午节吃粽子、赛龙舟，体验传统文化的好时机。",
            destinations=["杭州", "苏州", "南京"]
        ),
        send_promotion(
            "春季特惠",
            "精选目的地春季旅游套餐限时优惠，最高立减1000元！",
            link="/promotions/spring",
            valid_until="2026-04-30"
        ),
        send_system_message(
            "欢迎使用旅行规划系统",
            "本系统利用AI技术为您智能规划旅行，如有问题请查看帮助中心或联系客服。",
            priority="normal"
        )
    ]

    logger.info(f"初始化默认消息: {len(default_messages)}条")


# 导出函数
__all__ = [
    "send_travel_tip",
    "send_destination_alert",
    "send_promotion",
    "send_holiday_reminder",
    "send_system_message",
    "init_default_messages"
]
