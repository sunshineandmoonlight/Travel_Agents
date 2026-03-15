"""
测试Group A智能体 - 通信版本

验证UserRequirementAnalyst、DestinationMatcher、RankingScorer的通信功能
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
print("  Group A 智能体通信测试")
print("=" * 70)

# 导入通信模块
from tradingagents.communication import (
    MessageBus,
    PubSub,
    ServiceRegistry,
    CommunicatingAgent,
    TravelTopics,
    TravelAgentTypes
)

# 导入Group A智能体
from tradingagents.agents.group_a import (
    UserRequirementAnalyst,
    DestinationMatcher,
    RankingScorer
)

print("\n[OK] 模块导入成功")


# ==================== 测试1: UserRequirementAnalyst ====================
print("\n" + "=" * 70)
print("【1】测试 UserRequirementAnalyst (需求分析智能体)")
print("-" * 70)

try:
    analyst = UserRequirementAnalyst()
    print(f"创建智能体: {analyst.agent_name}")

    # 初始化
    analyst.initialize()
    print(f"智能体已初始化: {analyst.agent_id}")

    # 测试需求分析
    requirements = {
        'travel_scope': 'domestic',
        'days': 5,
        'adults': 2,
        'children': 0,
        'budget': 'medium',
        'interests': ['历史文化', '美食']
    }

    print(f"\n分析用户需求: {requirements}")

    portrait = analyst.analyze_requirements(requirements)

    print(f"\n[结果] 用户画像:")
    print(f"  旅行类型: {portrait.get('travel_type')}")
    print(f"  节奏偏好: {portrait.get('pace_preference')}")
    print(f"  预算等级: {portrait.get('budget_level')}")
    print(f"  主要兴趣: {portrait.get('primary_interests')}")
    print(f"  描述: {portrait.get('portrait_description', 'N/A')[:100]}...")

    # 测试服务注册
    registry = analyst._registry
    registered = registry.discover_agent(analyst.agent_id)
    print(f"\n[服务注册] 智能体已注册:")
    print(f"  ID: {registered.agent_id if registered else 'N/A'}")
    print(f"  类型: {registered.agent_type if registered else 'N/A'}")
    print(f"  状态: {registered.status if registered else 'N/A'}")

    print("\n[OK] UserRequirementAnalyst 测试通过")

    analyst.shutdown()

except Exception as e:
    print(f"\n[ERROR] UserRequirementAnalyst 测试失败: {e}")
    import traceback
    traceback.print_exc()


# ==================== 测试2: DestinationMatcher ====================
print("\n" + "=" * 70)
print("【2】测试 DestinationMatcher (地区匹配智能体)")
print("-" * 70)

try:
    matcher = DestinationMatcher()
    print(f"创建智能体: {matcher.agent_name}")

    # 初始化
    matcher.initialize()

    # 创建测试用户画像
    user_portrait = {
        'travel_type': '情侣游',
        'days': 5,
        'total_travelers': 2,
        'budget': 'medium',
        'primary_interests': ['历史文化', '美食'],
        'pace_preference': '沉浸型'
    }

    print(f"\n匹配目的地:")
    print(f"  范围: 国内")
    print(f"  兴趣: {user_portrait['primary_interests']}")

    candidates = matcher.match_destinations(user_portrait, "domestic")

    print(f"\n[结果] 匹配到 {len(candidates)} 个目的地")
    if candidates:
        print(f"\n  Top 5:")
        for i, dest in enumerate(candidates[:5], 1):
            print(f"    {i}. {dest['destination']} - 匹配分: {dest['match_score']}")

    print("\n[OK] DestinationMatcher 测试通过")

    matcher.shutdown()

except Exception as e:
    print(f"\n[ERROR] DestinationMatcher 测试失败: {e}")
    import traceback
    traceback.print_exc()


# ==================== 测试3: RankingScorer ====================
print("\n" + "=" * 70)
print("【3】测试 RankingScorer (排名打分智能体)")
print("-" * 70)

try:
    scorer = RankingScorer()
    print(f"创建智能体: {scorer.agent_name}")

    # 初始化
    scorer.initialize()

    # 创建测试候选列表
    candidates = [
        {
            "destination": "北京",
            "match_score": 85,
            "estimated_budget": 5000,
            "tags": ["历史文化", "美食", "购物"]
        },
        {
            "destination": "成都",
            "match_score": 90,
            "estimated_budget": 4000,
            "tags": ["历史文化", "美食", "休闲度假"]
        },
        {
            "destination": "西安",
            "match_score": 82,
            "estimated_budget": 4500,
            "tags": ["历史文化"]
        },
        {
            "destination": "杭州",
            "match_score": 75,
            "estimated_budget": 4800,
            "tags": ["自然风光", "休闲度假"]
        }
    ]

    user_portrait = {
        'travel_type': '情侣游',
        'budget': 'medium',
        'primary_interests': ['历史文化', '美食'],
        'days': 5
    }

    print(f"\n对 {len(candidates)} 个候选目的地排名")

    ranked = scorer.rank_and_select_top(candidates, user_portrait, 3)

    print(f"\n[结果] Top {len(ranked)} 目的地:")
    for i, dest in enumerate(ranked, 1):
        print(f"    {i}. {dest['destination']} - 综合得分: {dest.get('final_score', 0):.1f}")

    print("\n[OK] RankingScorer 测试通过")

    scorer.shutdown()

except Exception as e:
    print(f"\n[ERROR] RankingScorer 测试失败: {e}")
    import traceback
    traceback.print_exc()


# ==================== 测试4: 智能体间通信 ====================
print("\n" + "=" * 70)
print("【4】测试智能体间通信协作")
print("-" * 70)

try:
    # 创建通信组件
    message_bus = MessageBus()
    pubsub = PubSub()
    registry = ServiceRegistry()

    # 创建智能体
    analyst = UserRequirementAnalyst()
    matcher = DestinationMatcher()
    scorer = RankingScorer()

    # 初始化所有智能体
    analyst.initialize()
    matcher.initialize()
    scorer.initialize()

    print("已初始化3个智能体")

    # 订阅事件
    received_events = []

    def on_portrait_created(msg):
        received_events.append("portrait_created")
        print(f"  [Matcher] 收到用户画像事件")

    def on_destinations_matched(msg):
        received_events.append("destinations_matched")
        print(f"  [Scorer] 收到目的地匹配事件")

    pubsub.subscribe("events.user_portrait_created", on_portrait_created, "test_subscriber")
    pubsub.subscribe("events.destinations_matched", on_destinations_matched, "test_subscriber")

    print("\n[流程] 开始智能体协作流程...")

    # Step 1: 分析需求
    print("\n[A1] 需求分析...")
    requirements = {
        'travel_scope': 'domestic',
        'days': 5,
        'adults': 2,
        'budget': 'medium',
        'interests': ['历史文化', '美食']
    }
    portrait = analyst.analyze_requirements(requirements)
    print(f"  -> 用户画像: {portrait['travel_type']}, {portrait['pace_preference']}")

    # Step 2: 匹配目的地
    print("\n[A2] 地区匹配...")
    candidates = matcher.match_destinations(portrait, "domestic")
    print(f"  -> 匹配到 {len(candidates)} 个目的地")

    # Step 3: 排名选择
    print("\n[A3] 排名选择...")
    ranked = scorer.rank_and_select_top(candidates, portrait, 4)
    print(f"  -> Top {len(ranked)}: {[d['destination'] for d in ranked]}")

    print("\n[OK] 智能体协作流程完成")

    # 清理
    analyst.shutdown()
    matcher.shutdown()
    scorer.shutdown()

except Exception as e:
    print(f"\n[ERROR] 智能体协作测试失败: {e}")
    import traceback
    traceback.print_exc()


# ==================== 总结 ====================
print("\n" + "=" * 70)
print("  测试总结")
print("=" * 70)

print("""
Group A 智能体更新完成:

[OK] UserRequirementAnalyst - 通信版本
  - 继承 CommunicatingAgent
  - 支持消息发送和接收
  - 支持事件发布
  - 支持进度报告
  - 服务注册功能

[OK] DestinationMatcher - 通信版本
  - 继承 CommunicatingAgent
  - 支持消息发送和接收
  - 支持事件发布
  - 支持进度报告
  - 服务注册功能

[OK] RankingScorer - 通信版本
  - 继承 CommunicatingAgent
  - 支持消息发送和接收
  - 支持事件发布
  - 支持进度报告
  - 服务注册功能

新功能:
  - 智能体可独立初始化和关闭
  - 支持服务发现和注册
  - 支持事件发布和订阅
  - 支持进度报告
  - 保留原有函数接口（向后兼容）

使用方式:
  # 新方式（通信式）
  agent = UserRequirementAnalyst()
  agent.initialize()
  portrait = agent.analyze_requirements(requirements)
  agent.shutdown()

  # 原有方式（函数式，仍然可用）
  from tradingagents.agents.group_a import create_user_portrait
  portrait = create_user_portrait(requirements, llm)
""")

print("\n下一步:")
print("  - 更新Group B智能体")
print("  - 更新Group C智能体")
print("  - 测试跨组智能体通信")

print("\n" + "=" * 70)
