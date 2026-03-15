"""
智能体消息协议

定义智能体间通信的消息格式、类型和优先级。
"""

from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import json


class MessageType(str, Enum):
    """消息类型枚举"""

    # 请求类型
    REQUEST = "request"           # 请求消息
    QUERY = "query"               # 查询消息

    # 响应类型
    RESPONSE = "response"         # 响应消息
    ACKNOWLEDGE = "acknowledge"   # 确认消息

    # 通知类型
    NOTIFICATION = "notification" # 通知消息
    BROADCAST = "broadcast"       # 广播消息

    # 事件类型
    EVENT = "event"               # 事件消息
    STATUS_UPDATE = "status_update" # 状态更新

    # 控制类型
    CONTROL = "control"           # 控制消息
    COMMAND = "command"           # 命令消息

    # 错误类型
    ERROR = "error"               # 错误消息
    WARNING = "warning"           # 警告消息


class MessagePriority(str, Enum):
    """消息优先级枚举"""
    CRITICAL = "critical"  # 紧急消息，立即处理
    HIGH = "high"         # 高优先级，优先处理
    NORMAL = "normal"     # 普通优先级，按序处理
    LOW = "low"           # 低优先级，延后处理


@dataclass
class AgentMessage:
    """
    智能体消息类

    用于智能体之间的通信，包含发送者、接收者、消息类型、内容等信息。
    """

    # 基本属性
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.NOTIFICATION
    priority: MessagePriority = MessagePriority.NORMAL

    # 发送和接收信息
    sender: str = ""              # 发送者ID
    receiver: str = ""            # 接收者ID（空表示广播）
    reply_to: Optional[str] = None  # 回复消息ID

    # 消息内容
    content: Dict[str, Any] = field(default_factory=dict)
    data: Optional[Any] = None    # 附加数据（可以是任意类型）

    # 时间戳
    timestamp: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None  # 过期时间

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "type": self.type.value,
            "priority": self.priority.value,
            "sender": self.sender,
            "receiver": self.receiver,
            "reply_to": self.reply_to,
            "content": self.content,
            "data": str(self.data) if self.data else None,
            "timestamp": self.timestamp.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata,
            "headers": self.headers
        }

    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """从字典创建消息"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            type=MessageType(data.get("type", MessageType.NOTIFICATION)),
            priority=MessagePriority(data.get("priority", MessagePriority.NORMAL)),
            sender=data.get("sender", ""),
            receiver=data.get("receiver", ""),
            reply_to=data.get("reply_to"),
            content=data.get("content", {}),
            data=data.get("data"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.now(),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            metadata=data.get("metadata", {}),
            headers=data.get("headers", {})
        )

    def is_expired(self) -> bool:
        """检查消息是否已过期"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def is_broadcast(self) -> bool:
        """检查是否为广播消息"""
        return not self.receiver or self.receiver == "*"

    def respond(self, content: Dict[str, Any], **kwargs) -> "AgentMessage":
        """创建回复消息"""
        return create_response(
            original_message=self,
            content=content,
            **kwargs
        )


def create_message(
    sender: str,
    receiver: str,
    message_type: MessageType = MessageType.NOTIFICATION,
    content: Optional[Dict[str, Any]] = None,
    priority: MessagePriority = MessagePriority.NORMAL,
    **kwargs
) -> AgentMessage:
    """
    创建新消息

    Args:
        sender: 发送者ID
        receiver: 接收者ID
        message_type: 消息类型
        content: 消息内容
        priority: 消息优先级
        **kwargs: 其他属性

    Returns:
        AgentMessage对象
    """
    return AgentMessage(
        sender=sender,
        receiver=receiver,
        type=message_type,
        content=content or {},
        priority=priority,
        **kwargs
    )


def create_response(
    original_message: AgentMessage,
    content: Dict[str, Any],
    success: bool = True,
    **kwargs
) -> AgentMessage:
    """
    创建回复消息

    Args:
        original_message: 原始消息
        content: 回复内容
        success: 是否成功
        **kwargs: 其他属性

    Returns:
        AgentMessage对象
    """
    response = AgentMessage(
        sender=original_message.receiver,
        receiver=original_message.sender,
        type=MessageType.RESPONSE,
        content=content,
        reply_to=original_message.id,
        **kwargs
    )

    # 如果原消息有优先级，回复使用相同优先级
    if original_message.priority != MessagePriority.NORMAL:
        response.priority = original_message.priority

    return response


def create_error_response(
    original_message: AgentMessage,
    error_message: str,
    error_code: Optional[str] = None,
    **kwargs
) -> AgentMessage:
    """
    创建错误回复消息

    Args:
        original_message: 原始消息
        error_message: 错误信息
        error_code: 错误代码
        **kwargs: 其他属性

    Returns:
        AgentMessage对象
    """
    content = {
        "success": False,
        "error": error_message,
        "error_code": error_code
    }

    return AgentMessage(
        sender=original_message.receiver,
        receiver=original_message.sender,
        type=MessageType.ERROR,
        content=content,
        reply_to=original_message.id,
        priority=original_message.priority,
        **kwargs
    )


# 旅行系统专用消息类型
class TravelMessageType:
    """旅行系统消息类型常量"""

    # 目的地相关
    DESTINATION_MATCHED = "destination.matched"
    DESTINATION_RANKED = "destination.ranked"
    DESTINATION_SELECTED = "destination.selected"

    # 方案设计相关
    STYLE_PROPOSAL_CREATED = "proposal.style.created"
    STYLE_PROPOSAL_UPDATED = "proposal.style.updated"
    ALL_PROPOSALS_READY = "proposal.all_ready"

    # 行程规划相关
    ITINERARY_PLANNED = "itinerary.planned"
    ITINERARY_UPDATED = "itinerary.updated"

    # 攻略生成相关
    GUIDE_GENERATION_STARTED = "guide.generation.started"
    GUIDE_GENERATION_PROGRESS = "guide.generation.progress"
    GUIDE_GENERATION_COMPLETED = "guide.generation.completed"

    # 用户相关
    USER_REQUIREMENTS_ANALYZED = "user.requirements.analyzed"
    USER_PORTRAIT_CREATED = "user.portrait.created"

    # 系统相关
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_ERROR = "agent.error"


# 预定义的消息内容结构
class MessageContent:
    """消息内容构建器"""

    @staticmethod
    def destination_matched(
        destination: str,
        score: int,
        reason: str
    ) -> Dict[str, Any]:
        """目的地匹配消息内容"""
        return {
            "destination": destination,
            "match_score": score,
            "match_reason": reason,
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def proposal_created(
        style_name: str,
        style_type: str,
        days: int,
        highlights: List[str]
    ) -> Dict[str, Any]:
        """方案创建消息内容"""
        return {
            "style_name": style_name,
            "style_type": style_type,
            "days": days,
            "highlights": highlights,
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def progress_update(
        agent: str,
        progress: int,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """进度更新消息内容"""
        return {
            "agent": agent,
            "progress": progress,
            "status": status,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def error(
        agent: str,
        error_type: str,
        error_message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """错误消息内容"""
        return {
            "agent": agent,
            "error_type": error_type,
            "error_message": error_message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
