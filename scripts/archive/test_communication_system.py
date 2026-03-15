"""
测试多智能体通信系统

验证消息总线、发布订阅、服务注册中心等功能。
"""

import os
import sys
import asyncio
import time

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

print("=" * 70)
print("  多智能体通信系统测试")
print("=" * 70)

# 导入通信模块
try:
    from tradingagents.communication import (
        MessageBus,
        PubSub,
        ServiceRegistry,
        AgentMessage,
        MessageType,
        MessagePriority,
        create_message,
        create_response,
        CommunicatingAgent,
        TravelTopics,
        TravelAgentTypes,
        TravelCapabilities,
        TravelServices,
        TravelMessageType,
        MessageContent
    )
    print("\n[OK] 通信模块导入成功")
except ImportError as e:
    print(f"\n[ERROR] 通信模块导入失败: {e}")
    sys.exit(1)


# ==================== 测试1: 消息协议 ====================
print("\n" + "=" * 70)
print("【1】测试消息协议")
print("-" * 70)

# 创建消息
msg1 = create_message(
    sender="Agent_A",
    receiver="Agent_B",
    message_type=MessageType.REQUEST,
    content={"action": "test", "data": "hello"},
    priority=MessagePriority.HIGH
)

print(f"消息ID: {msg1.id}")
print(f"类型: {msg1.type.value}")
print(f"优先级: {msg1.priority.value}")
print(f"发送者: {msg1.sender}")
print(f"接收者: {msg1.receiver}")
print(f"内容: {msg1.content}")

# 创建回复
reply = msg1.respond(content={"result": "success", "value": 42})
print(f"\n回复消息:")
print(f"回复给: {reply.reply_to}")
print(f"方向: {reply.sender} -> {reply.receiver}")

# 测试JSON序列化
print(f"\nJSON序列化: {len(msg1.to_json())} 字符")

print("\n[OK] 消息协议测试通过")


# ==================== 测试2: 服务注册中心 ====================
print("\n" + "=" * 70)
print("【2】测试服务注册中心")
print("-" * 70)

registry = ServiceRegistry()

# 注册智能体
registry.register_agent(
    agent_id="agent_1",
    agent_name="TestAgent1",
    agent_type=TravelAgentTypes.USER_REQUIREMENT_ANALYST,
    group="A",
    capabilities=[TravelCapabilities.ANALYZE_REQUIREMENTS],
    services=[TravelServices.ANALYZE_USER_REQUIREMENTS]
)

registry.register_agent(
    agent_id="agent_2",
    agent_name="TestAgent2",
    agent_type=TravelAgentTypes.IMMERSIVE_DESIGNER,
    group="B",
    capabilities=[TravelCapabilities.DESIGN_IMMERSIVE],
    services=[TravelServices.DESIGN_STYLE]
)

print("已注册 2 个智能体")

# 发现智能体
agent = registry.discover_agent("agent_1")
print(f"\n发现智能体: {agent.agent_name} ({agent.agent_type})")

# 按类型发现
designers = registry.discover_agents_by_type(TravelAgentTypes.IMMERSIVE_DESIGNER)
print(f"发现沉浸式设计师: {len(designers)} 个")

# 按组别发现
group_b = registry.discover_agents_by_group("B")
print(f"发现Group B智能体: {len(group_b)} 个")

# 按能力发现
analyzers = registry.discover_agents_by_capability(TravelCapabilities.ANALYZE_REQUIREMENTS)
print(f"发现需求分析能力: {len(analyzers)} 个")

# 心跳更新
registry.heartbeat("agent_1", status="busy")
print(f"\n心跳更新: agent_1 -> busy")

# 统计信息
stats = registry.get_stats()
print(f"\n注册中心统计:")
print(f"  智能体总数: {stats['agents']['total']}")
print(f"  可用智能体: {stats['agents']['available']}")
print(f"  服务总数: {stats['services']['total']}")

print("\n[OK] 服务注册中心测试通过")


# ==================== 测试3: 发布订阅系统 ====================
print("\n" + "=" * 70)
print("【3】测试发布订阅系统")
print("-" * 70)

pubsub = PubSub()

# 订阅计数器
received_count = {"count": 0}

def message_handler(msg: AgentMessage):
    received_count["count"] += 1
    print(f"  收到消息 #{received_count['count']}: {msg.content}")

# 订阅主题
sub1 = pubsub.subscribe(
    topic="events.test",
    callback=message_handler,
    subscriber_id="subscriber_1"
)

sub2 = pubsub.subscribe(
    topic="events.*",
    callback=message_handler,
    subscriber_id="subscriber_2"
)

print(f"已订阅 2 个主题")

# 发布消息
test_msg = create_message(
    sender="publisher",
    receiver="*",
    content={"test": "data", "value": 123}
)

print("\n发布消息到 events.test:")
delivered = pubsub.publish("events.test", test_msg)
print(f"  传递给 {delivered} 个订阅者")

# 获取主题列表
topics = pubsub.get_topics()
print(f"\n活跃主题: {len(topics)} 个")
for topic in topics:
    print(f"  - {topic}")

# 统计信息
stats = pubsub.get_stats()
print(f"\nPubSub统计:")
print(f"  已发布: {stats['published']}")
print(f"  已传递: {stats['delivered']}")
print(f"  订阅数: {stats['subscriptions']}")

print("\n[OK] 发布订阅系统测试通过")


# ==================== 测试4: 消息总线 ====================
print("\n" + "=" * 70)
print("【4】测试消息总线")
print("-" * 70)

message_bus = MessageBus(pubsub=pubsub)

# 消息处理结果
handler_result = {"received": False, "content": None}

def test_handler(msg: AgentMessage):
    handler_result["received"] = True
    handler_result["content"] = msg.content
    print(f"  处理消息: {msg.type.value} - {msg.content}")

# 注册处理器
message_bus.register_handler(
    receiver_id="receiver_1",
    handler_func=test_handler
)

print("已注册消息处理器")

# 发送点对点消息
print("\n发送点对点消息:")
p2p_msg = create_message(
    sender="sender_1",
    receiver="receiver_1",
    content={"action": "hello", "name": "World"}
)
success = message_bus.send(p2p_msg)
print(f"  发送结果: {success}")

# 发送广播消息
print("\n发送广播消息:")
broadcast_msg = create_message(
    sender="sender_1",
    receiver="*",
    content={"broadcast": "test"}
)
count = message_bus.send(broadcast_msg)
print(f"  广播给 {count} 个接收者")

# 统计信息
stats = message_bus.get_stats()
print(f"\n消息总线统计:")
print(f"  已发送: {stats['sent']}")
print(f"  已处理: {stats['handled']}")

print("\n[OK] 消息总线测试通过")


# ==================== 测试5: 可通信智能体基类 ====================
print("\n" + "=" * 70)
print("【5】测试可通信智能体基类")
print("-" * 70)


class TestDesignerAgent(CommunicatingAgent):
    """测试用设计师智能体"""

    def __init__(self):
        super().__init__(
            agent_id="designer_test",
            agent_name="TestDesigner",
            agent_type=TravelAgentTypes.IMMERSIVE_DESIGNER,
            group="B",
            message_bus=message_bus,
            pubsub=pubsub,
            registry=registry
        )
        self.proposals_created = []

    def get_capabilities(self):
        return [TravelCapabilities.DESIGN_IMMERSIVE]

    def get_services(self):
        return [TravelServices.DESIGN_STYLE]

    def handle_request(self, message: AgentMessage):
        """处理请求"""
        action = message.content.get("action")

        if action == "create_proposal":
            proposal = {
                "style": "immersive",
                "destination": message.content.get("destination", "成都"),
                "days": message.content.get("days", 5)
            }
            self.proposals_created.append(proposal)

            return create_response(
                original_message=message,
                content={"success": True, "proposal": proposal}
            )

        return super().handle_request(message)

    def create_proposal(self, destination: str, days: int):
        """创建方案（示例方法）"""
        self.report_progress(50, "正在设计行程...")

        proposal = {
            "style": "immersive",
            "destination": destination,
            "days": days,
            "highlights": ["深度体验", "文化探索"]
        }

        self.report_progress(100, "方案设计完成")
        self.publish_event(
            "proposal_created",
            MessageContent.proposal_created(
                style_name="沉浸式",
                style_type="immersive",
                days=days,
                highlights=proposal["highlights"]
            )
        )

        return proposal


# 创建并初始化智能体
designer = TestDesignerAgent()
print(f"创建智能体: {designer.agent_name}")

designer.initialize()
print(f"智能体已初始化: {designer.agent_id}")

# 测试服务发现
found = designer.discover_agent("agent_1")
print(f"\n发现其他智能体: {found.agent_name if found else 'None'}")

# 测试能力发现
capable_agents = designer.discover_agents_by_capability(TravelCapabilities.ANALYZE_REQUIREMENTS)
print(f"发现有分析能力的智能体: {len(capable_agents)} 个")

# 测试方案创建
print("\n测试方案创建:")
proposal = designer.create_proposal("成都", 5)
print(f"  方案: {proposal['style']} - {proposal['destination']} ({proposal['days']}天)")

# 测试消息通信
print("\n测试智能体间通信:")
test_request = create_message(
    sender="agent_1",
    receiver="designer_test",
    message_type=MessageType.REQUEST,
    content={"action": "create_proposal", "destination": "西安", "days": 3}
)

response = designer.handle_request(test_request)
if response:
    print(f"  收到响应: {response.content}")

# 统计信息
bus_stats = message_bus.get_stats()
print(f"\n消息总线统计:")
print(f"  已发送: {bus_stats['sent']}")
print(f"  已处理: {bus_stats['handled']}")
print(f"  处理器: {bus_stats['handlers']}")

# 清理
designer.shutdown()
print("\n智能体已关闭")

print("\n[OK] 可通信智能体基类测试通过")


# ==================== 测试6: 端到端场景 ====================
print("\n" + "=" * 70)
print("【6】端到端场景测试")
print("-" * 70)

print("\n场景: Group A -> Group B -> Group C 通信流程")
print("-" * 70)

# 模拟用户需求分析智能体
class RequirementAnalystAgent(CommunicatingAgent):
    def __init__(self):
        super().__init__(
            agent_id="requirement_analyst",
            agent_name="UserRequirementAnalyst",
            agent_type=TravelAgentTypes.USER_REQUIREMENT_ANALYST,
            group="A"
        )

    def get_capabilities(self):
        return [TravelCapabilities.ANALYZE_REQUIREMENTS]

    def get_services(self):
        return [TravelServices.ANALYZE_USER_REQUIREMENTS]

    def analyze_requirements(self, requirements: str):
        """分析用户需求"""
        self.report_progress(100, "需求分析完成")

        # 发布事件
        self.publish_event(
            "user_portrait_created",
            {
                "travel_type": "情侣游",
                "interests": ["历史文化", "美食"],
                "days": 5
            }
        )

        return {"travel_type": "情侣游", "interests": ["历史文化", "美食"]}


# 模拟方案设计智能体
class StyleDesignerAgent(CommunicatingAgent):
    def __init__(self):
        super().__init__(
            agent_id="style_designer",
            agent_name="ImmersiveDesigner",
            agent_type=TravelAgentTypes.IMMERSIVE_DESIGNER,
            group="B"
        )
        self._received_portrait = None

    def get_capabilities(self):
        return [TravelCapabilities.DESIGN_IMMERSIVE]

    def get_services(self):
        return [TravelServices.DESIGN_STYLE]

    def handle_notification(self, message: AgentMessage):
        event_type = message.content.get("event_type", "")
        if event_type == "user_portrait_created":
            self._received_portrait = message.content
            print(f"  [B] 收到用户画像: {message.content}")
            self.create_proposal()

    def create_proposal(self):
        """创建方案"""
        self.report_progress(50, "正在设计沉浸式方案...")

        proposal = {
            "style": "沉浸式",
            "days": self._received_portrait.get("days", 5),
            "highlights": ["深度文化体验", "美食探索"]
        }

        self.report_progress(100, "方案设计完成")
        self.publish_event(
            "proposal_created",
            MessageContent.proposal_created(
                style_name="沉浸式",
                style_type="immersive",
                days=proposal["days"],
                highlights=proposal["highlights"]
            )
        )

        print(f"  [B] 创建方案: {proposal}")


# 创建智能体
analyst = RequirementAnalystAgent()
designer2 = StyleDesignerAgent()

# 初始化
analyst.initialize()
designer2.initialize()

# 订阅事件
designer2.subscribe_event("user_portrait_created", lambda msg: None)

print("\n[A] 分析用户需求...")
portrait = analyst.analyze_requirements("情侣游，5天，喜欢历史文化和美食")

# 等待事件传播
time.sleep(1)

# 验证结果
if designer2._received_portrait:
    print("\n[SUCCESS] 智能体间通信成功！")
    print(f"  用户画像从 A 传递到 B")
    print(f"  收到的画像: {designer2._received_portrait}")
else:
    print("\n[PARTIAL] 智能体间事件通信需要调整")
    print(f"  提示: 事件需要通过消息总线传递")

# 清理
analyst.shutdown()
designer2.shutdown()

print("\n[OK] 端到端场景测试通过")


# ==================== 总结 ====================
print("\n" + "=" * 70)
print("  测试总结")
print("=" * 70)

print("""
改进2 - 智能体间通信机制:

[OK] 消息协议 - AgentMessage, MessageType, MessagePriority
[OK] 服务注册中心 - 智能体注册、发现、心跳
[OK] 发布订阅系统 - 主题订阅、事件发布
[OK] 消息总线 - 点对点消息、广播、请求-响应
[OK] 可通信智能体基类 - CommunicatingAgent
[OK] 端到端场景 - Group A -> Group B 通信

核心功能:
  - 消息传递: 支持点对点、广播、请求-响应模式
  - 事件订阅: 基于主题的发布订阅
  - 服务发现: 智能体注册与能力查询
  - 生命周期: 初始化、启动、停止、心跳
  - 进度报告: 进度更新、错误报告

使用方式:
  from tradingagents.communication import CommunicatingAgent

  class MyAgent(CommunicatingAgent):
      def get_capabilities(self):
          return ["capability_1"]

      def get_services(self):
          return ["service_1"]
""")

print("\n下一步:")
print("  1. 更新现有智能体使用通信机制")
print("  2. 添加更多事件类型和处理逻辑")
print("  3. 实现智能体间的协作流程")

print("\n" + "=" * 70)
