"""
发布订阅系统 (PubSub)

提供基于主题的消息发布和订阅功能，支持异步事件通知。
"""

from typing import Dict, List, Callable, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
import re
from collections import defaultdict

from .agent_protocol import AgentMessage, MessageType


logger = logging.getLogger('travel_agents.communication')


@dataclass
class Topic:
    """主题类"""

    name: str                          # 主题名称，支持通配符
    description: str = ""              # 主题描述
    created_at: datetime = field(default_factory=datetime.now)

    def matches(self, pattern: str) -> bool:
        """检查主题是否匹配模式（支持通配符）"""
        # 简单的通配符匹配
        regex_pattern = pattern.replace("*", ".*").replace("?", ".")
        return bool(re.match(f"^{regex_pattern}$", self.name))

    def __str__(self) -> str:
        return self.name


@dataclass
class Subscription:
    """订阅信息类"""

    id: str                            # 订阅ID
    subscriber_id: str                 # 订阅者ID
    topic: str                         # 订阅的主题
    callback: Callable                 # 回调函数
    filter_func: Optional[Callable] = None  # 消息过滤器
    created_at: datetime = field(default_factory=datetime.now)
    active: bool = True                # 是否激活


class PubSub:
    """
    发布订阅系统

    支持主题订阅、消息发布、通配符订阅等功能。
    """

    def __init__(self):
        # 主题 -> 订阅列表
        self._subscriptions: Dict[str, List[Subscription]] = defaultdict(list)

        # 订阅者 -> 订阅列表
        self._subscriber_subscriptions: Dict[str, Set[str]] = defaultdict(set)

        # 消息队列（用于持久化，暂未实现）
        self._message_queue: List[Any] = []

        # 统计信息
        self._stats = {
            "published": 0,
            "delivered": 0,
            "errors": 0
        }

    def subscribe(
        self,
        topic: str,
        callback: Callable,
        subscriber_id: str,
        filter_func: Optional[Callable] = None
    ) -> str:
        """
        订阅主题

        Args:
            topic: 主题名称（支持通配符）
            callback: 消息回调函数
            subscriber_id: 订阅者ID
            filter_func: 消息过滤器（返回False则不处理消息）

        Returns:
            订阅ID
        """
        import uuid
        subscription_id = f"sub_{subscriber_id}_{uuid.uuid4().hex[:8]}"

        subscription = Subscription(
            id=subscription_id,
            subscriber_id=subscriber_id,
            topic=topic,
            callback=callback,
            filter_func=filter_func
        )

        self._subscriptions[topic].append(subscription)
        self._subscriber_subscriptions[subscriber_id].add(subscription_id)

        logger.info(f"[PubSub] {subscriber_id} 订阅主题: {topic}")
        return subscription_id

    def unsubscribe(self, subscription_id: str, subscriber_id: str) -> bool:
        """
        取消订阅

        Args:
            subscription_id: 订阅ID
            subscriber_id: 订阅者ID

        Returns:
            是否成功
        """
        # 查找并删除订阅
        for topic, subscriptions in self._subscriptions.items():
            for i, sub in enumerate(subscriptions):
                if sub.id == subscription_id and sub.subscriber_id == subscriber_id:
                    sub.active = False
                    subscriptions.pop(i)
                    self._subscriber_subscriptions[subscriber_id].discard(subscription_id)
                    logger.info(f"[PubSub] {subscriber_id} 取消订阅: {topic}")
                    return True

        return False

    def unsubscribe_all(self, subscriber_id: str) -> int:
        """
        取消订阅者的所有订阅

        Args:
            subscriber_id: 订阅者ID

        Returns:
            取消的订阅数量
        """
        count = 0
        subscription_ids = self._subscriber_subscriptions.get(subscriber_id, set()).copy()

        for sub_id in subscription_ids:
            if self.unsubscribe(sub_id, subscriber_id):
                count += 1

        return count

    def publish(
        self,
        topic: str,
        message: AgentMessage,
        block: bool = True
    ) -> int:
        """
        发布消息到主题

        Args:
            topic: 主题名称
            message: 消息对象
            block: 是否阻塞等待消息处理完成

        Returns:
            接收到消息的订阅者数量
        """
        self._stats["published"] += 1

        # 查找匹配的订阅
        matched_subscriptions = self._find_matching_subscriptions(topic)

        if not matched_subscriptions:
            logger.debug(f"[PubSub] 主题 {topic} 没有订阅者")
            return 0

        logger.info(f"[PubSub] 发布消息到 {topic}: {len(matched_subscriptions)} 个订阅者")

        # 传递消息给订阅者
        delivered_count = 0

        for subscription in matched_subscriptions:
            if not subscription.active:
                continue

            # 应用过滤器
            if subscription.filter_func and not subscription.filter_func(message):
                continue

            try:
                if block:
                    # 同步调用
                    subscription.callback(message)
                else:
                    # 异步调用
                    asyncio.create_task(self._async_callback(subscription.callback, message))

                delivered_count += 1
                self._stats["delivered"] += 1

            except Exception as e:
                logger.error(f"[PubSub] 消息传递失败: {e}")
                self._stats["errors"] += 1

        return delivered_count

    async def publish_async(
        self,
        topic: str,
        message: AgentMessage
    ) -> int:
        """
        异步发布消息

        Args:
            topic: 主题名称
            message: 消息对象

        Returns:
            接收到消息的订阅者数量
        """
        return self.publish(topic, message, block=False)

    def _find_matching_subscriptions(self, topic: str) -> List[Subscription]:
        """查找匹配主题的所有订阅"""
        matched = []

        for sub_topic, subscriptions in self._subscriptions.items():
            # 检查订阅主题是否匹配
            topic_obj = Topic(name=sub_topic)
            if topic_obj.matches(topic):
                matched.extend(subscriptions)

        return matched

    async def _async_callback(self, callback: Callable, message: AgentMessage):
        """异步执行回调"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(message)
            else:
                callback(message)
        except Exception as e:
            logger.error(f"[PubSub] 异步回调失败: {e}")

    def get_topics(self) -> List[str]:
        """获取所有活跃的主题"""
        return list(self._subscriptions.keys())

    def get_subscribers(self, topic: Optional[str] = None) -> List[str]:
        """
        获取订阅者列表

        Args:
            topic: 主题名称（None表示获取所有订阅者）

        Returns:
            订阅者ID列表
        """
        if topic:
            subscriptions = self._subscriptions.get(topic, [])
            return [sub.subscriber_id for sub in subscriptions if sub.active]
        else:
            return list(self._subscriber_subscriptions.keys())

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self._stats,
            "topics": len(self._subscriptions),
            "subscriptions": sum(len(subs) for subs in self._subscriptions.values()),
            "subscribers": len(self._subscriber_subscriptions)
        }


# 全局PubSub实例
_pubsub_instance: Optional[PubSub] = None


def get_pubsub() -> PubSub:
    """获取全局PubSub实例"""
    global _pubsub_instance
    if _pubsub_instance is None:
        _pubsub_instance = PubSub()
    return _pubsub_instance


# 旅行系统主题常量
class TravelTopics:
    """旅行系统主题常量"""

    # 通用主题
    ALL = "*"                          # 所有消息
    AGENT_ALL = "agent.*"              # 所有智能体消息

    # Group A 主题
    GROUP_A_ALL = "group_a.*"          # Group A所有消息
    USER_REQUIREMENTS = "group_a.user.requirements"
    DESTINATION_MATCH = "group_a.destination.match"
    DESTINATION_RANK = "group_a.destination.rank"

    # Group B 主题
    GROUP_B_ALL = "group_b.*"          # Group B所有消息
    STYLE_PROPOSAL = "group_b.proposal.*"
    PROPOSAL_CREATED = "group_b.proposal.created"
    PROPOSAL_UPDATED = "group_b.proposal.updated"

    # Group C 主题
    GROUP_C_ALL = "group_c.*"          # Group C所有消息
    ITINERARY_PLAN = "group_c.itinerary.*"
    GUIDE_GENERATE = "group_c.guide.*"

    # 事件主题
    EVENTS = "events.*"                # 所有事件
    AGENT_STARTED = "events.agent.started"
    AGENT_COMPLETED = "events.agent.completed"
    AGENT_ERROR = "events.agent.error"
    PROGRESS_UPDATE = "events.progress"

    # 控制主题
    CONTROL = "control.*"              # 所有控制消息
    CONTROL_START = "control.start"
    CONTROL_STOP = "control.stop"
    CONTROL_PAUSE = "control.pause"
    CONTROL_RESUME = "control.resume"
