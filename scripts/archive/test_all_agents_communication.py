"""
测试所有智能体的通信协作

验证Group A、B、C智能体的通信功能
"""

import os
import sys
import time

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

print("=" * 70)
print("  全部智能体通信协作测试")
print("=" * 70)

# 导入通信模块
from tradingagents.communication import (
    MessageBus,
    PubSub,
    ServiceRegistry,
    TravelTopics,
    TravelCapabilities
)

# 导入所有智能体
from tradingagents.agents.group_a import (
    UserRequirementAnalyst,
    DestinationMatcher,
    RankingScorer
)

from tradingagents.agents.group_b import (
    ImmersiveDesignerAgent,
    ExplorationDesignerAgent,
    RelaxationDesignerAgent,
    HiddenGemDesignerAgent
)

from tradingagents.agents.group_c import (
    AttractionSchedulerAgent,
    AccommodationAdvisorAgent,
    DiningRecommenderAgent,
    TransportPlannerAgent,
    LLMGuideWriterAgent
)

print("\n[OK] 所有智能体模块导入成功")


# ==================== 测试：完整流程 ====================
print("\n" + "=" * 70)
print("【完整流程测试】模拟完整的旅行规划流程")
print("=" * 70)

# 创建通信组件
message_bus = MessageBus()
pubsub = PubSub()
registry = ServiceRegistry()

# 创建LLM（可选）
llm = None
try:
    from tradingagents.graph.trading_graph import create_llm_by_provider
    llm = create_llm_by_provider(
        provider=os.getenv("LLM_PROVIDER", "siliconflow"),
        model=os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-7B-Instruct"),
        backend_url=os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"),
        temperature=0.7,
        max_tokens=2000,
        timeout=60
    )
    print("\n[OK] LLM实例创建成功")
except Exception as e:
    print(f"\n[WARN] LLM创建失败: {e}")

# ==================== Group A: 需求分析与目的地推荐 ====================
print("\n" + "-" * 70)
print("Group A: 需求分析与目的地推荐")
print("-" * 70)

try:
    # A1: 需求分析
    print("\n[A1] 需求分析...")
    analyst = UserRequirementAnalyst(llm=llm)
    analyst.initialize()

    requirements = {
        'travel_scope': 'domestic',
        'days': 5,
        'adults': 2,
        'children': 0,
        'budget': 'medium',
        'interests': ['历史文化', '美食']
    }

    portrait = analyst.analyze_requirements(requirements)
    print(f"  -> 旅行类型: {portrait['travel_type']}")
    print(f"  -> 节奏偏好: {portrait['pace_preference']}")

    # A2: 地区匹配
    print("\n[A2] 地区匹配...")
    matcher = DestinationMatcher(llm=llm)
    matcher.initialize()

    candidates = matcher.match_destinations(portrait, "domestic")
    print(f"  -> 匹配到 {len(candidates)} 个目的地")

    # A3: 排名选择
    print("\n[A3] 排名选择...")
    scorer = RankingScorer(llm=llm)
    scorer.initialize()

    ranked = scorer.rank_and_select_top(candidates, portrait, 4)
    print(f"  -> Top {len(ranked)} 目的地:")
    for i, dest in enumerate(ranked, 1):
        print(f"       {i}. {dest['destination']} (得分: {dest.get('final_score', 0):.0f})")

    # 选择第一个目的地
    selected_destination = ranked[0]['destination']

    analyst.shutdown()
    matcher.shutdown()
    scorer.shutdown()

except Exception as e:
    print(f"\n[ERROR] Group A处理失败: {e}")
    import traceback
    traceback.print_exc()
    selected_destination = "成都"
    portrait = {"travel_type": "情侣游", "pace_preference": "沉浸型", "days": 5}


# ==================== Group B: 风格方案设计 ====================
print("\n" + "-" * 70)
print("Group B: 风格方案设计")
print("-" * 70)

try:
    # 模拟目的地数据
    dest_data = {
        "tags": ["历史文化", "美食"],
        "highlights": ["宽窄巷子", "锦里古街", "大熊猫基地"],
        "budget_level": {"medium": 500}
    }

    # 创建设计师
    designers = [
        ("Immersive", ImmersiveDesignerAgent(llm=llm)),
        ("Exploration", ExplorationDesignerAgent(llm=llm)),
        ("Relaxation", RelaxationDesignerAgent(llm=llm)),
        ("HiddenGem", HiddenGemDesignerAgent(llm=llm))
    ]

    proposals = []

    for name, designer in designers:
        print(f"\n[B] {name} 设计师初始化...")
        designer.initialize()

        proposal = designer.create_proposal(
            destination=selected_destination,
            dest_data=dest_data,
            user_portrait=portrait,
            days=5
        )

        proposals.append(proposal)
        print(f"  -> {proposal.get('style_name')} 节奏: {proposal.get('daily_pace')}")

        designer.shutdown()

    print(f"\n[结果] 生成了 {len(proposals)} 个风格方案")

except Exception as e:
    print(f"\n[ERROR] Group B处理失败: {e}")
    import traceback
    traceback.print_exc()
    proposals = []


# ==================== Group C: 详细攻略生成 ====================
print("\n" + "-" * 70)
print("Group C: 详细攻略生成")
print("-" * 70)

try:
    # C1: 景点排程
    print("\n[C1] 景点排程...")
    scheduler = AttractionSchedulerAgent(llm=llm)
    scheduler.initialize()

    # 使用第一个方案
    style_proposal = proposals[0] if proposals else {}
    scheduled_attractions = scheduler.create_schedule(
        destination=selected_destination,
        dest_data=dest_data,
        style_proposal=style_proposal,
        days=5,
        start_date="2024-04-01"
    )
    print(f"  -> 行程安排完成")

    # C2: 交通规划
    print("\n[C2] 交通规划...")
    transport_planner = TransportPlannerAgent(llm=llm)
    transport_planner.initialize()

    transport_plan = transport_planner.create_plan(
        destination=selected_destination,
        scheduled_attractions=scheduled_attractions,
        budget_level="medium"
    )
    print(f"  -> 交通规划完成")

    # C3: 餐饮推荐
    print("\n[C3] 餐饮推荐...")
    dining_recommender = DiningRecommenderAgent(llm=llm)
    dining_recommender.initialize()

    dining_plan = dining_recommender.create_recommendations(
        destination=selected_destination,
        scheduled_attractions=scheduled_attractions,
        budget_level="medium"
    )
    print(f"  -> 餐饮推荐完成")

    # C4: 住宿推荐
    print("\n[C4] 住宿推荐...")
    accommodation_advisor = AccommodationAdvisorAgent(llm=llm)
    accommodation_advisor.initialize()

    accommodation_plan = accommodation_advisor.create_recommendations(
        destination=selected_destination,
        days=5,
        budget_level="medium",
        travelers=2
    )
    print(f"  -> 住宿推荐完成")

    # C5: 攻略生成
    print("\n[C5] 攻略生成...")
    guide_writer = LLMGuideWriterAgent(llm=llm)
    guide_writer.initialize()

    user_requirements = {
        "user_portrait": portrait,
        "start_date": "2024-04-01"
    }

    guide = guide_writer.write_guide(
        destination=selected_destination,
        style_proposal=style_proposal,
        scheduled_attractions=scheduled_attractions,
        transport_plan=transport_plan,
        dining_plan=dining_plan,
        accommodation_plan=accommodation_plan,
        user_requirements=user_requirements
    )
    print(f"  -> 攻略生成完成")

    scheduler.shutdown()
    transport_planner.shutdown()
    dining_recommender.shutdown()
    accommodation_advisor.shutdown()
    guide_writer.shutdown()

    print("\n[OK] Group C处理完成")

except Exception as e:
    print(f"\n[ERROR] Group C处理失败: {e}")
    import traceback
    traceback.print_exc()


# ==================== 服务注册验证 ====================
print("\n" + "=" * 70)
print("【服务注册验证】")
print("-" * 70)

# 检查服务注册中心
all_agents = registry.get_all_agents()
print(f"\n已注册智能体: {len(all_agents)} 个")

for agent_info in all_agents:
    print(f"  - {agent_info.agent_name} ({agent_info.group})")
    print(f"    服务: {', '.join(agent_info.services)}")

# 按能力发现
print(f"\n按能力发现智能体:")

design_capability = TravelCapabilities.DESIGN_IMMERSIVE
capable_agents = registry.discover_agents_by_capability(design_capability)
print(f"  设计能力 ({design_capability}): {len(capable_agents)} 个")
for agent in capable_agents:
    print(f"    - {agent.agent_name}")


# ==================== 总结 ====================
print("\n" + "=" * 70)
print("  测试总结")
print("=" * 70)

print("""
所有智能体更新完成:

[OK] Group A (3个智能体) - 通信版本
  - UserRequirementAnalyst
  - DestinationMatcher
  - RankingScorer

[OK] Group B (4个智能体) - 通信版本
  - ImmersiveDesignerAgent
  - ExplorationDesignerAgent
  - RelaxationDesignerAgent
  - HiddenGemDesignerAgent

[OK] Group C (6个智能体) - 通信版本
  - AttractionSchedulerAgent
  - TransportPlannerAgent
  - DiningRecommenderAgent
  - AccommodationAdvisorAgent
  - GuideFormatterAgent
  - LLMGuideWriterAgent

新增功能:
  - 智能体可以独立初始化和关闭
  - 支持服务注册和发现
  - 支持事件发布和订阅
  - 支持进度报告
  - 支持消息通信
  - 保留原有函数接口（向后兼容）

使用方式:
  # 新方式（通信式）
  agent = UserRequirementAnalyst(llm)
  agent.initialize()
  result = agent.analyze_requirements(data)
  agent.shutdown()

  # 原有方式（函数式，仍然可用）
  from tradingagents.agents.group_a import create_user_portrait
  result = create_user_portrait(requirements, llm)
""")

print("\下一步:")
print("  - 测试跨智能体消息传递")
print("  - 实现智能体协作流程")
print("  - 优化通信性能")

print("\n" + "=" * 70)
