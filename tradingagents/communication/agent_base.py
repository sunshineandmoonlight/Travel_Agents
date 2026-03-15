"""
智能体基类

提供集成通信系统的智能体基类。
"""

from typing import Optional, Dict, Any, List, Callable
from abc import ABC, abstractmethod
import logging

from .message_bus import MessageBus, get_message_bus
from .pubsub import PubSub, get_pubsub, TravelTopics
from .service_registry import (
    ServiceRegistry,
    get_service_registry,
    AgentInfo,
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
    MessageContent
)


logger = logging.getLogger('travel_agents.communication')


class CommunicatingAgent(ABC):
    """
    可通信智能体基类

    提供消息发送、事件订阅、服务注册等通信功能。
    """

    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        agent_type: str,
        group: str,
        message_bus: Optional[MessageBus] = None,
        pubsub: Optional[PubSub] = None,
        registry: Optional[ServiceRegistry] = None
    ):
        # 基本属性
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.group = group

        # 通信组件
        self._message_bus = message_bus or get_message_bus()
        self._pubsub = pubsub or get_pubsub()
        self._registry = registry or get_service_registry()

        # 订阅ID列表
        self._subscription_ids: List[str] = []

        # 状态
        self._status = "idle"
        self._initialized = False

        # 注册取消处理器的回调
        self._unregister_handlers: List[Callable] = []

    def initialize(self) -> bool:
        """
        初始化智能体

        子类可以重写此方法进行自定义初始化。

        Returns:
            是否成功
        """
        if self._initialized:
            return True

        try:
            # 注册到服务注册中心
            self._register_to_registry()

            # 注册消息处理器
            self._register_message_handlers()

            # 订阅事件
            self._subscribe_to_events()

            self._initialized = True
            logger.info(f"[{self.agent_name}] 初始化完成: {self.agent_id}")
            return True

        except Exception as e:
            logger.error(f"[{self.agent_name}] 初始化失败: {e}")
            return False

    def shutdown(self):
        """关闭智能体"""
        # 取消消息处理器
        for unregister in self._unregister_handlers:
            unregister()

        # 取消事件订阅
        for sub_id in self._subscription_ids:
            self._pubsub.unsubscribe(sub_id, self.agent_id)

        # 注销服务
        self._registry.unregister_agent(self.agent_id)

        self._initialized = False
        logger.info(f"[{self.agent_name}] 关闭完成")

    def _register_to_registry(self):
        """注册到服务注册中心"""
        capabilities = self.get_capabilities()
        services = self.get_services()

        self._registry.register_agent(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            agent_type=self.agent_type,
            group=self.group,
            capabilities=capabilities,
            services=services
        )

        # 注册提供的服务
        for service_name in services:
            self._registry.register_service(
                agent_id=self.agent_id,
                service_name=service_name,
                service_type=f"{self.group}.{service_name}"
            )

    def _register_message_handlers(self):
        """注册消息处理器"""
        unregister = self._message_bus.register_handler(
            receiver_id=self.agent_id,
            handler_func=self._handle_message,
            message_types=None  # 处理所有类型
        )
        self._unregister_handlers.append(unregister)

    def _subscribe_to_events(self):
        """订阅事件（子类可重写）"""
        # 默认订阅智能体错误事件
        sub_id = self._pubsub.subscribe(
            topic=TravelTopics.AGENT_ERROR,
            callback=self._on_agent_error,
            subscriber_id=self.agent_id
        )
        self._subscription_ids.append(sub_id)

    def _handle_message(self, message: AgentMessage):
        """
        处理接收到的消息

        Args:
            message: 消息对象
        """
        logger.info(f"[{self.agent_name}] 收到消息: {message.type} from {message.sender}")

        # 更新心跳和状态
        self._update_heartbeat("busy")

        try:
            # 根据消息类型分发
            if message.type == MessageType.REQUEST:
                response = self.handle_request(message)
                if response:
                    self._message_bus.respond(response)
            elif message.type == MessageType.RESPONSE:
                self.handle_response(message)
            elif message.type == MessageType.NOTIFICATION:
                self.handle_notification(message)
            elif message.type == MessageType.EVENT:
                self.handle_event(message)
            elif message.type == MessageType.CONTROL:
                self.handle_control(message)
            else:
                logger.warning(f"[{self.agent_name}] 未知消息类型: {message.type}")

        except Exception as e:
            logger.error(f"[{self.agent_name}] 处理消息失败: {e}")
        finally:
            self._update_heartbeat("idle")

    # 消息处理方法（子类可重写）
    def handle_request(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        处理请求消息

        Args:
            message: 请求消息

        Returns:
            响应消息
        """
        return create_response(
            original_message=message,
            content={"success": True, "message": "请求已处理"}
        )

    def handle_response(self, message: AgentMessage):
        """
        处理响应消息

        Args:
            message: 响应消息
        """
        logger.debug(f"[{self.agent_name}] 收到响应: {message.reply_to}")

    def handle_notification(self, message: AgentMessage):
        """
        处理通知消息

        Args:
            message: 通知消息
        """
        logger.debug(f"[{self.agent_name}] 收到通知: {message.content}")

    def handle_event(self, message: AgentMessage):
        """
        处理事件消息

        Args:
            message: 事件消息
        """
        logger.debug(f"[{self.agent_name}] 收到事件: {message.content}")

    def handle_control(self, message: AgentMessage):
        """
        处理控制消息

        Args:
            message: 控制消息
        """
        control_type = message.content.get("type")
        if control_type == "start":
            self.start()
        elif control_type == "stop":
            self.stop()
        elif control_type == "pause":
            self.pause()
        elif control_type == "resume":
            self.resume()

    def _on_agent_error(self, message: AgentMessage):
        """处理其他智能体错误事件"""
        error_content = message.content
        logger.warning(
            f"[{self.agent_name}] 智能体错误: "
            f"{error_content.get('agent')} - {error_content.get('error_message')}"
        )

    # 发送消息方法
    def send_message(
        self,
        receiver: str,
        content: Dict[str, Any],
        message_type: MessageType = MessageType.NOTIFICATION,
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> bool:
        """
        发送消息给其他智能体

        Args:
            receiver: 接收者ID
            content: 消息内容
            message_type: 消息类型
            priority: 消息优先级

        Returns:
            是否成功
        """
        message = create_message(
            sender=self.agent_id,
            receiver=receiver,
            message_type=message_type,
            content=content,
            priority=priority
        )

        return self._message_bus.send(message)

    def broadcast_message(
        self,
        content: Dict[str, Any],
        message_type: MessageType = MessageType.BROADCAST,
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> int:
        """
        广播消息给所有智能体

        Args:
            content: 消息内容
            message_type: 消息类型
            priority: 消息优先级

        Returns:
            接收者数量
        """
        message = create_message(
            sender=self.agent_id,
            receiver="*",
            message_type=message_type,
            content=content,
            priority=priority
        )

        return self._message_bus.send(message)

    def publish_event(
        self,
        event_type: str,
        content: Dict[str, Any],
        broadcast: bool = True
    ) -> int:
        """
        发布事件

        Args:
            event_type: 事件类型
            content: 事件内容
            broadcast: 是否广播到所有智能体

        Returns:
            接收者数量
        """
        full_content = {
            "event_type": event_type,
            **content
        }

        # 通过PubSub发布事件（用于订阅者）
        message = create_message(
            sender=self.agent_id,
            receiver="*",
            message_type=MessageType.EVENT,
            content=full_content
        )

        topic = f"events.{event_type}"
        pubsub_count = self._message_bus.publish_event(topic, message)

        # 如果需要广播，也通过MessageBus发送
        if broadcast:
            broadcast_count = self._message_bus.send(message)
            return max(pubsub_count, broadcast_count)

        return pubsub_count

    def subscribe_event(
        self,
        event_type: str,
        callback: Callable
    ) -> str:
        """
        订阅事件

        Args:
            event_type: 事件类型
            callback: 回调函数

        Returns:
            订阅ID
        """
        topic = f"events.{event_type}"
        sub_id = self._pubsub.subscribe(
            topic=topic,
            callback=lambda msg: callback(msg),
            subscriber_id=self.agent_id
        )
        self._subscription_ids.append(sub_id)
        return sub_id

    async def request(
        self,
        receiver: str,
        content: Dict[str, Any],
        timeout: float = 30.0
    ) -> Optional[AgentMessage]:
        """
        发送请求并等待响应

        Args:
            receiver: 接收者ID
            content: 请求内容
            timeout: 超时时间

        Returns:
            响应消息
        """
        message = create_message(
            sender=self.agent_id,
            receiver=receiver,
            message_type=MessageType.REQUEST,
            content=content
        )

        return await self._message_bus.request(message, timeout=timeout)

    # 服务发现方法
    def discover_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """发现智能体"""
        return self._registry.discover_agent(agent_id)

    def discover_agents_by_type(self, agent_type: str) -> List[AgentInfo]:
        """按类型发现智能体"""
        return self._registry.discover_agents_by_type(agent_type)

    def discover_agents_by_capability(self, capability: str) -> List[AgentInfo]:
        """按能力发现智能体"""
        return self._registry.discover_agents_by_capability(capability)

    def discover_service(self, service_name: str) -> List[Any]:
        """发现服务"""
        return self._registry.discover_service(service_name)

    # 生命周期方法
    def start(self):
        """启动智能体"""
        self._status = "idle"
        self._update_heartbeat("idle")
        self.publish_event("agent_started", {"agent": self.agent_id})
        logger.info(f"[{self.agent_name}] 启动")

    def stop(self):
        """停止智能体"""
        self._status = "offline"
        self.publish_event("agent_completed", {"agent": self.agent_id})
        logger.info(f"[{self.agent_name}] 停止")

    def pause(self):
        """暂停智能体"""
        self._status = "paused"
        logger.info(f"[{self.agent_name}] 暂停")

    def resume(self):
        """恢复智能体"""
        self._status = "idle"
        logger.info(f"[{self.agent_name}] 恢复")

    def _update_heartbeat(self, status: Optional[str] = None):
        """更新心跳"""
        if status:
            self._status = status
        self._registry.heartbeat(self.agent_id, self._status)

    # 抽象方法（子类必须实现）
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """获取智能体能力列表"""
        pass

    @abstractmethod
    def get_services(self) -> List[str]:
        """获取智能体提供的服务列表"""
        pass

    # 进度报告方法
    def report_progress(
        self,
        progress: int,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        报告进度

        Args:
            progress: 进度百分比 (0-100)
            status: 状态描述
            details: 详细信息
        """
        self.publish_event(
            "progress_update",
            MessageContent.progress_update(
                agent=self.agent_id,
                progress=progress,
                status=status,
                details=details
            )
        )

    def report_error(
        self,
        error_type: str,
        error_message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        报告错误

        Args:
            error_type: 错误类型
            error_message: 错误信息
            details: 详细信息
        """
        self.publish_event(
            "agent_error",
            MessageContent.error(
                agent=self.agent_id,
                error_type=error_type,
                error_message=error_message,
                details=details
            )
        )
