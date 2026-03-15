"""
消息总线

提供智能体间点对点消息传递功能。
"""

from typing import Dict, Callable, Optional, List, Any
from collections import defaultdict, deque
from datetime import datetime
import asyncio
import logging

from .agent_protocol import AgentMessage, MessageType, MessagePriority
from .pubsub import PubSub, TravelTopics
from .service_registry import ServiceRegistry


logger = logging.getLogger('travel_agents.communication')


class MessageHandler:
    """消息处理器类"""

    def __init__(
        self,
        handler_func: Callable,
        message_types: Optional[List[MessageType]] = None,
        priority_filter: Optional[MessagePriority] = None
    ):
        self.handler_func = handler_func
        self.message_types = set(message_types or [])
        self.priority_filter = priority_filter

    def can_handle(self, message: AgentMessage) -> bool:
        """检查是否能处理该消息"""
        # 检查消息类型
        if self.message_types and message.type not in self.message_types:
            return False

        # 检查优先级
        if self.priority_filter and message.priority != self.priority_filter:
            return False

        return True


class MessageQueue:
    """优先级消息队列"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._queues = {
            MessagePriority.CRITICAL: deque(),
            MessagePriority.HIGH: deque(),
            MessagePriority.NORMAL: deque(),
            MessagePriority.LOW: deque()
        }

    def put(self, message: AgentMessage) -> bool:
        """放入消息"""
        if self.size() >= self.max_size:
            logger.warning(f"[MessageQueue] 队列已满，丢弃消息: {message.id}")
            return False

        self._queues[message.priority].append(message)
        return True

    def get(self) -> Optional[AgentMessage]:
        """获取消息（按优先级）"""
        for priority in [MessagePriority.CRITICAL, MessagePriority.HIGH, MessagePriority.NORMAL, MessagePriority.LOW]:
            if self._queues[priority]:
                return self._queues[priority].popleft()
        return None

    def size(self) -> int:
        """队列大小"""
        return sum(len(q) for q in self._queues.values())

    def clear(self):
        """清空队列"""
        for q in self._queues.values():
            q.clear()


class PendingRequest:
    """待处理请求类"""

    def __init__(
        self,
        request_message: AgentMessage,
        timeout: float = 30.0,
        callback: Optional[Callable] = None
    ):
        self.request_message = request_message
        self.timeout = timeout
        self.callback = callback
        self.created_at = datetime.now()
        self.future = asyncio.Future()

    def is_expired(self) -> bool:
        """检查是否已超时"""
        return (datetime.now() - self.created_at).total_seconds() > self.timeout

    def complete(self, response: AgentMessage):
        """完成请求"""
        if not self.future.done():
            self.future.set_result(response)
        if self.callback:
            self.callback(response)

    def fail(self, error: Exception):
        """请求失败"""
        if not self.future.done():
            self.future.set_exception(error)


class MessageBus:
    """
    消息总线

    提供智能体间点对点消息传递、请求-响应模式等功能。
    """

    def __init__(self, pubsub: Optional[PubSub] = None):
        # 接收者 -> 消息处理器列表
        self._handlers: Dict[str, List[MessageHandler]] = defaultdict(list)

        # 消息队列（接收者 -> 队列）
        self._queues: Dict[str, MessageQueue] = {}

        # 待处理请求（request_id -> PendingRequest）
        self._pending_requests: Dict[str, PendingRequest] = {}

        # PubSub引用（用于事件广播）
        self._pubsub = pubsub

        # 统计信息
        self._stats = {
            "sent": 0,
            "received": 0,
            "handled": 0,
            "errors": 0,
            "expired": 0
        }

        # 清理任务
        self._cleanup_task = None

    def register_handler(
        self,
        receiver_id: str,
        handler_func: Callable,
        message_types: Optional[List[MessageType]] = None
    ) -> Callable:
        """
        注册消息处理器

        Args:
            receiver_id: 接收者ID
            handler_func: 处理函数
            message_types: 可处理的消息类型列表

        Returns:
            取消注册函数
        """
        handler = MessageHandler(handler_func, message_types)
        self._handlers[receiver_id].append(handler)

        logger.debug(f"[MessageBus] 注册处理器: {receiver_id}")

        def unregister():
            self.unregister_handler(receiver_id, handler)

        return unregister

    def unregister_handler(self, receiver_id: str, handler: MessageHandler):
        """取消注册处理器"""
        if receiver_id in self._handlers and handler in self._handlers[receiver_id]:
            self._handlers[receiver_id].remove(handler)
            logger.debug(f"[MessageBus] 取消处理器: {receiver_id}")

    def unregister_all_handlers(self, receiver_id: str):
        """取消接收者的所有处理器"""
        if receiver_id in self._handlers:
            del self._handlers[receiver_id]
            logger.debug(f"[MessageBus] 取消所有处理器: {receiver_id}")

    def send(
        self,
        message: AgentMessage,
        block: bool = True
    ) -> bool:
        """
        发送消息

        Args:
            message: 消息对象
            block: 是否阻塞等待处理完成

        Returns:
            是否成功
        """
        # 检查消息是否已过期
        if message.is_expired():
            logger.warning(f"[MessageBus] 消息已过期: {message.id}")
            self._stats["expired"] += 1
            return False

        # 广播消息
        if message.is_broadcast():
            return self._broadcast(message, block)

        # 点对点消息
        return self._send_to_receiver(message, block)

    def _send_to_receiver(
        self,
        message: AgentMessage,
        block: bool = True
    ) -> bool:
        """发送消息到指定接收者"""
        receiver_id = message.receiver

        # 检查是否有处理器
        if receiver_id not in self._handlers or not self._handlers[receiver_id]:
            logger.warning(f"[MessageBus] 接收者无处理器: {receiver_id}")
            return False

        self._stats["sent"] += 1
        self._stats["received"] += 1

        # 查找能处理该消息的处理器
        handlers = self._handlers[receiver_id]
        matched_handlers = [h for h in handlers if h.can_handle(message)]

        if not matched_handlers:
            logger.warning(f"[MessageBus] 没有匹配的处理器: {message.type} -> {receiver_id}")
            return False

        # 调用处理器
        try:
            if block:
                for handler in matched_handlers:
                    handler.handler_func(message)
            else:
                for handler in matched_handlers:
                    asyncio.create_task(self._async_handle(handler.handler_func, message))

            self._stats["handled"] += 1
            logger.debug(f"[MessageBus] 消息已发送: {message.id} -> {receiver_id}")
            return True

        except Exception as e:
            logger.error(f"[MessageBus] 处理消息失败: {e}")
            self._stats["errors"] += 1
            return False

    def _broadcast(self, message: AgentMessage, block: bool = True) -> int:
        """广播消息到所有接收者"""
        count = 0
        for receiver_id in self._handlers:
            msg = AgentMessage(
                sender=message.sender,
                receiver=receiver_id,
                type=message.type,
                priority=message.priority,
                content=message.content,
                data=message.data,
                metadata=message.metadata
            )
            if self._send_to_receiver(msg, block):
                count += 1

        logger.info(f"[MessageBus] 广播消息: {message.id} -> {count}个接收者")
        return count

    async def send_async(self, message: AgentMessage) -> bool:
        """异步发送消息"""
        return self.send(message, block=False)

    async def request(
        self,
        message: AgentMessage,
        timeout: float = 30.0
    ) -> Optional[AgentMessage]:
        """
        发送请求并等待响应

        Args:
            message: 请求消息
            timeout: 超时时间（秒）

        Returns:
            响应消息（超时返回None）
        """
        # 记录待处理请求
        pending = PendingRequest(message, timeout)
        self._pending_requests[message.id] = pending

        # 发送请求
        success = self.send(message)

        if not success:
            self._pending_requests.pop(message.id, None)
            return None

        # 等待响应
        try:
            response = await asyncio.wait_for(pending.future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            logger.warning(f"[MessageBus] 请求超时: {message.id}")
            self._pending_requests.pop(message.id, None)
            return None

    def respond(self, response: AgentMessage) -> bool:
        """
        发送响应消息

        Args:
            response: 响应消息

        Returns:
            是否成功
        """
        # 查找对应的请求
        request_id = response.reply_to
        if not request_id:
            logger.warning("[MessageBus] 响应消息缺少reply_to")
            return False

        pending = self._pending_requests.get(request_id)
        if not pending:
            logger.warning(f"[MessageBus] 未找到待处理请求: {request_id}")
            return False

        # 完成请求
        pending.complete(response)
        self._pending_requests.pop(request_id, None)

        # 发送响应
        return self.send(response)

    async def _async_handle(self, handler: Callable, message: AgentMessage):
        """异步处理消息"""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(message)
            else:
                handler(message)
        except Exception as e:
            logger.error(f"[MessageBus] 异步处理失败: {e}")

    def publish_event(self, topic: str, message: AgentMessage) -> int:
        """
        发布事件到PubSub

        Args:
            topic: 主题名称
            message: 消息对象

        Returns:
            接收数量
        """
        if self._pubsub:
            return self._pubsub.publish(topic, message)
        return 0

    def subscribe_event(
        self,
        topic: str,
        callback: Callable,
        subscriber_id: str
    ) -> str:
        """
        订阅事件

        Args:
            topic: 主题名称
            callback: 回调函数
            subscriber_id: 订阅者ID

        Returns:
            订阅ID
        """
        if self._pubsub:
            return self._pubsub.subscribe(topic, callback, subscriber_id)
        return ""

    def start_cleanup_task(self):
        """启动清理任务"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def _cleanup_loop(self):
        """清理循环"""
        while True:
            try:
                await asyncio.sleep(10)  # 每10秒清理一次
                self._cleanup_expired_requests()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[MessageBus] 清理任务错误: {e}")

    def _cleanup_expired_requests(self):
        """清理过期请求"""
        expired = [
            req_id for req_id, pending in self._pending_requests.items()
            if pending.is_expired()
        ]

        for req_id in expired:
            pending = self._pending_requests.pop(req_id)
            pending.fail(TimeoutError(f"请求超时: {req_id}"))
            self._stats["expired"] += 1

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self._stats,
            "handlers": sum(len(hs) for hs in self._handlers.values()),
            "pending_requests": len(self._pending_requests),
            "queues": len(self._queues)
        }


# 全局MessageBus实例
_message_bus_instance: Optional[MessageBus] = None


def get_message_bus() -> MessageBus:
    """获取全局MessageBus实例"""
    global _message_bus_instance
    if _message_bus_instance is None:
        from .pubsub import get_pubsub
        _message_bus_instance = MessageBus(pubsub=get_pubsub())
    return _message_bus_instance
