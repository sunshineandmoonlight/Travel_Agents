"""
多智能体通信系统

提供智能体之间的消息传递、事件发布订阅、服务发现等功能。

模块结构:
- message_bus: 消息总线，用于智能体间异步通信
- pubsub: 发布订阅系统，用于主题式事件通知
- service_registry: 服务注册中心，用于智能体发现
- agent_protocol: 消息协议和类型定义
- agent_base: 可通信智能体基类
"""

from .message_bus import MessageBus, get_message_bus
from .pubsub import PubSub, Topic, Subscription, TravelTopics, get_pubsub
from .service_registry import (
    ServiceRegistry,
    AgentInfo,
    ServiceInfo,
    get_service_registry,
    TravelAgentTypes,
    TravelCapabilities,
    TravelServices
)
from .agent_protocol import (
    AgentMessage,
    MessageType,
    MessagePriority,
    create_message,
    create_response,
    TravelMessageType,
    MessageContent,
    create_error_response
)
from .agent_base import CommunicatingAgent

__all__ = [
    # Message Bus
    "MessageBus",
    "get_message_bus",

    # PubSub
    "PubSub",
    "Topic",
    "Message",
    "Subscription",
    "TravelTopics",
    "get_pubsub",

    # Service Registry
    "ServiceRegistry",
    "AgentInfo",
    "ServiceInfo",
    "get_service_registry",
    "TravelAgentTypes",
    "TravelCapabilities",
    "TravelServices",

    # Agent Protocol
    "AgentMessage",
    "MessageType",
    "MessagePriority",
    "create_message",
    "create_response",
    "TravelMessageType",
    "MessageContent",
    "create_error_response",

    # Agent Base
    "CommunicatingAgent",
]
