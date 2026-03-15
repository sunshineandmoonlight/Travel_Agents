"""
后端整体流程测试 - 展示各智能体生成结果

完整运行旅行规划流程，展示每个智能体的详细输出
"""

import os
import sys
import json
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

print("=" * 80)
print("  旅行规划智能体整体流程测试")
print("  展示各智能体生成结果")
print("=" * 80)

# 创建LLM
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
    print(f"\n[WARN] LLM创建失败: {e}，将使用无LLM模式")

# 导入智能体
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
    TransportPlannerAgent,
    DiningRecommenderAgent,
    AccommodationAdvisorAgent,
    LLMGuideWriterAgent
)

print("[OK] 所有智能体模块导入成功\n")

# 测试数据
requirements = {
    'travel_scope': 'domestic',
    'days': 5,
    'adults': 2,
    'children': 0,
    'budget': 'medium',
    'interests': ['历史文化', '美食'],
    'start_date': '2024-04-15'
}

print("=" * 80)
print("  用户需求输入")
print("=" * 80)
print(json.dumps(requirements, ensure_ascii=False, indent=2))
print()

results = {}  # 存储所有结果

# ==================== 组A: 需求分析与目的地推荐 ====================
print("\n" + "=" * 80)
print("  【组A】需求分析与目的地推荐")
print("=" * 80)

# A1: 需求分析
print("\n┌─ A1: UserRequirementAnalyst (需求分析智能体)")
print("│")
print("│ 输入: 用户需求表单")
print("│")

try:
    analyst = UserRequirementAnalyst(llm=llm)
    analyst.initialize()

    portrait = analyst.analyze_requirements(requirements)
    results['user_portrait'] = portrait

    print("│ 输出: 用户画像")
    print("│ " + "─" * 70)
    for key, value in portrait.items():
        if key == 'portrait_description':
            print(f"│ {key}: {value[:100]}...")
        else:
            print(f"│ {key}: {value}")
    print("│ " + "─" * 70)

    analyst.shutdown()
    print("│")
    print("└─ [OK] A1 完成\n")

except Exception as e:
    print(f"│ [ERROR] A1 失败: {e}\n│")
    print("└─\n")

# A2: 地区匹配
print("┌─ A2: DestinationMatcher (地区匹配智能体)")
print("│")
print("│ 输入: 用户画像 + 旅行范围")
print("│")

try:
    matcher = DestinationMatcher(llm=llm)
    matcher.initialize()

    candidates = matcher.match_destinations(portrait, "domestic")
    results['matched_destinations'] = candidates

    print(f"│ 输出: 匹配到 {len(candidates)} 个目的地")
    print("│ " + "─" * 70)
    for i, dest in enumerate(candidates[:5], 1):
        print(f"│   {i}. {dest['destination']} - 匹配分: {dest['match_score']}")
        print(f"│      标签: {', '.join(dest['tags'][:3])}")
        print(f"│      亮点: {', '.join(dest['highlights'][:2])}")
    if len(candidates) > 5:
        print(f"│   ... 还有 {len(candidates) - 5} 个目的地")
    print("│ " + "─" * 70)

    matcher.shutdown()
    print("│")
    print("└─ [OK] A2 完成\n")

except Exception as e:
    print(f"│ [ERROR] A2 失败: {e}\n│")
    print("└─\n")

# A3: 排名打分
print("┌─ A3: RankingScorer (排名打分智能体)")
print("│")
print("│ 输入: 候选目的地列表")
print("│")

try:
    scorer = RankingScorer(llm=llm)
    scorer.initialize()

    ranked = scorer.rank_and_select_top(candidates, portrait, 4)
    results['ranked_destinations'] = ranked

    print(f"│ 输出: Top {len(ranked)} 目的地")
    print("│ " + "─" * 70)
    for i, dest in enumerate(ranked, 1):
        print(f"│   [{i}] {dest['destination']}")
        print(f"│       综合得分: {dest.get('final_score', 0):.1f}")
        print(f"│       匹配分: {dest['match_score']}")
        print(f"│       预算: {dest['estimated_budget']} 元")
        print(f"│       标签: {', '.join(dest.get('tags', []))}")
    print("│ " + "─" * 70)

    scorer.shutdown()
    print("│")
    print("└─ [OK] A3 完成\n")

    # 选择第一个目的地
    selected_destination = ranked[0]['destination']
    results['selected_destination'] = selected_destination
    print(f"    → 用户选择: {selected_destination}\n")

except Exception as e:
    print(f"│ [ERROR] A3 失败: {e}\n│")
    print("└─\n")
    selected_destination = "成都"

# ==================== 组B: 风格方案设计 ====================
print("\n" + "=" * 80)
print("  【组B】风格方案设计")
print("=" * 80)

dest_data = {
    "tags": portrait.get("primary_interests", []),
    "highlights": ["景点1", "景点2", "景点3"],
    "budget_level": {"medium": 500}
}

designers = [
    ("ImmersiveDesigner", "沉浸式", ImmersiveDesignerAgent),
    ("ExplorationDesigner", "探索式", ExplorationDesignerAgent),
    ("RelaxationDesigner", "松弛式", RelaxationDesignerAgent),
    ("HiddenGemDesigner", "小众宝藏", HiddenGemDesignerAgent)
]

proposals = []

for class_name, style_name, DesignerClass in designers:
    print(f"\n┌─ B{len(proposals)+1}: {class_name} ({style_name}方案设计师)")
    print("│")
    print("│ 输入: 目的地 + 用户画像")
    print("│")

    try:
        designer = DesignerClass(llm=llm)
        designer.initialize()

        proposal = designer.create_proposal(selected_destination, dest_data, portrait, 5)
        proposals.append(proposal)

        print(f"│ 输出: {style_name}方案")
        print("│ " + "─" * 70)
        print(f"│   方案名称: {proposal.get('style_name')}")
        print(f"│   风格类型: {proposal.get('style_type')}")
        print(f"│   方案描述: {proposal.get('description')[:80]}...")
        print(f"│   每日节奏: {proposal.get('daily_pace')}")
        print(f"│   预计费用: {proposal.get('estimated_cost')} CNY")
        print(f"│   活动强度: {proposal.get('intensity')}/5")

        # 显示每日行程摘要
        daily_itinerary = proposal.get('daily_itinerary', [])
        if daily_itinerary:
            print(f"│   每日安排:")
            for day_plan in daily_itinerary[:3]:
                day_num = day_plan.get('day', 0)
                attractions = day_plan.get('attractions', [])
                pace = day_plan.get('pace', '')
                print(f"│     Day {day_num}: {len(attractions)}个景点 ({pace})")

        print("│ " + "─" * 70)

        designer.shutdown()
        print("│")
        print("└─ [OK] 完成\n")

    except Exception as e:
        print(f"│ [ERROR] 失败: {e}\n│")
        print("└─\n")

results['style_proposals'] = proposals

# 选择沉浸式方案
selected_proposal = proposals[0] if proposals else {}
selected_style = selected_proposal.get('style_type', 'immersive')
results['selected_style'] = selected_style

print(f"    → 用户选择: {selected_proposal.get('style_name', '沉浸式')}\n")

# ==================== 组C: 详细攻略生成 ====================
print("\n" + "=" * 80)
print("  【组C】详细攻略生成")
print("=" * 80)

# C1: 景点排程
print("\n┌─ C1: AttractionScheduler (景点排程师)")
print("│")
print("│ 输入: 目的地 + 风格方案")
print("│")

try:
    scheduler = AttractionSchedulerAgent(llm=llm)
    scheduler.initialize()

    scheduled_attractions = scheduler.create_schedule(
        selected_destination, dest_data, selected_proposal, 5, requirements['start_date']
    )
    results['scheduled_attractions'] = scheduled_attractions

    schedule_list = scheduled_attractions.get('scheduled_attractions', [])
    print(f"│ 输出: 景点时间表 ({len(schedule_list)}天)")
    print("│ " + "─" * 70)

    for day_schedule in schedule_list[:3]:
        day_num = day_schedule.get('day', 0)
        schedule = day_schedule.get('schedule', [])
        print(f"│   Day {day_num}:")
        for item in schedule[:4]:
            period = item.get('period', '')
            activity = item.get('activity', '')
            location = item.get('location', '')
            time_slot = item.get('time', '')
            print(f"│     {time_slot} [{period}] {activity} @ {location}")

    print("│ " + "─" * 70)

    scheduler.shutdown()
    print("│")
    print("└─ [OK] C1 完成\n")

except Exception as e:
    print(f"│ [ERROR] C1 失败: {e}\n│")
    print("└─\n")

# C2: 交通规划
print("┌─ C2: TransportPlanner (交通规划师)")
print("│")
print("│ 输入: 景点时间表")
print("│")

try:
    transport_planner = TransportPlannerAgent(llm=llm)
    transport_planner.initialize()

    budget_level = portrait.get('budget_level', 'medium')
    transport_plan = transport_planner.create_plan(
        selected_destination, scheduled_attractions, budget_level
    )
    results['transport_plan'] = transport_plan

    daily_transport = transport_plan.get('daily_transport', [])
    print(f"│ 输出: 交通规划")
    print("│ " + "─" * 70)
    print(f"│   总交通费用: {transport_plan.get('total_transport_cost', 0)} CNY")

    for day_transport in daily_transport[:2]:
        day_num = day_transport.get('day', 0)
        segments = day_transport.get('transport_segments', [])
        print(f"│   Day {day_num}: {len(segments)}段交通")

    recommendations = transport_plan.get('transport_recommendations', [])
    if recommendations:
        print(f"│   交通建议: {recommendations[0] if isinstance(recommendations, list) else recommendations}")

    print("│ " + "─" * 70)

    transport_planner.shutdown()
    print("│")
    print("└─ [OK] C2 完成\n")

except Exception as e:
    print(f"│ [ERROR] C2 失败: {e}\n│")
    print("└─\n")

# C3: 餐饮推荐
print("┌─ C3: DiningRecommender (餐饮推荐师)")
print("│")
print("│ 输入: 景点时间表")
print("│")

try:
    dining_recommender = DiningRecommenderAgent(llm=llm)
    dining_recommender.initialize()

    dining_plan = dining_recommender.create_recommendations(
        selected_destination, scheduled_attractions, budget_level
    )
    results['dining_plan'] = dining_plan

    daily_dining = dining_plan.get('daily_dining', [])
    print(f"│ 输出: 餐饮推荐")
    print("│ " + "─" * 70)
    print(f"│   总餐饮费用: {dining_plan.get('total_dining_cost', 0)} CNY")
    print(f"│   推荐餐厅数: {dining_plan.get('total_restaurants', 0)} 家")

    for day_dining in daily_dining[:2]:
        day_num = day_dining.get('day', 0)
        meals = day_dining.get('meals', [])
        print(f"│   Day {day_num}:")
        for meal in meals[:2]:
            meal_type = meal.get('meal_type', '')
            restaurant = meal.get('recommended_restaurant', {})
            name = restaurant.get('name', '待定') if isinstance(restaurant, dict) else '待定'
            print(f"│     {meal_type}: {name}")

    print("│ " + "─" * 70)

    dining_recommender.shutdown()
    print("│")
    print("└─ [OK] C3 完成\n")

except Exception as e:
    print(f"│ [ERROR] C3 失败: {e}\n│")
    print("└─\n")

# C4: 住宿推荐
print("┌─ C4: AccommodationAdvisor (住宿顾问)")
print("│")
print("│ 输入: 目的地 + 天数")
print("│")

try:
    accommodation_advisor = AccommodationAdvisorAgent(llm=llm)
    accommodation_advisor.initialize()

    travelers = requirements.get('adults', 2) + requirements.get('children', 0)
    accommodation_plan = accommodation_advisor.create_recommendations(
        selected_destination, 5, budget_level, travelers
    )
    results['accommodation_plan'] = accommodation_plan

    print(f"│ 输出: 住宿推荐")
    print("│ " + "─" * 70)
    print(f"│   总住宿费用: {accommodation_plan.get('total_accommodation_cost', 0)} CNY")
    print(f"│   推荐住宿: {len(accommodation_plan.get('accommodations', []))} 个区域")

    for accom in accommodation_plan.get('accommodations', [])[:3]:
        area = accom.get('area', '')
        price_range = accom.get('price_range', '')
        description = accom.get('description', '')[:50]
        print(f"│   - {area}: {price_range}")
        print(f"│     {description}...")

    print("│ " + "─" * 70)

    accommodation_advisor.shutdown()
    print("│")
    print("└─ [OK] C4 完成\n")

except Exception as e:
    print(f"│ [ERROR] C4 失败: {e}\n│")
    print("└─\n")

# C5: 攻略生成
print("┌─ C5: LLMGuideWriter (LLM攻略写作师)")
print("│")
print("│ 输入: 所有上述输出")
print("│")

try:
    guide_writer = LLMGuideWriterAgent(llm=llm)
    guide_writer.initialize()

    user_requirements = {
        "user_portrait": portrait,
        "start_date": requirements['start_date']
    }

    detailed_guide = guide_writer.write_guide(
        selected_destination, selected_proposal, scheduled_attractions,
        transport_plan, dining_plan, accommodation_plan, user_requirements
    )
    results['detailed_guide'] = detailed_guide

    print(f"│ 输出: 详细攻略")
    print("│ " + "─" * 70)
    print(f"│   目的地: {detailed_guide.get('destination', '')}")
    print(f"│   天数: {detailed_guide.get('days', 0)} 天")
    print(f"│   风格: {detailed_guide.get('style', '')}")
    print(f"│   总预算: {detailed_guide.get('total_budget', 0)} CNY")
    print(f"│")
    print(f"│   行程亮点:")
    for highlight in detailed_guide.get('highlights', [])[:3]:
        print(f"│   - {highlight}")
    print(f"│")
    print(f"│   费用明细:")
    budget_breakdown = detailed_guide.get('budget_breakdown', {})
    for key, value in budget_breakdown.items():
        print(f"│   - {key}: {value}")
    print("│ " + "─" * 70)

    guide_writer.shutdown()
    print("│")
    print("└─ [OK] C5 完成\n")

except Exception as e:
    print(f"│ [ERROR] C5 失败: {e}\n│")
    import traceback
    traceback.print_exc()
    print("└─\n")

# ==================== 保存完整结果 ====================
print("\n" + "=" * 80)
print("  保存完整结果")
print("=" * 80)

output_file = f"agent_workflow_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n完整结果已保存到: {output_file}")
except Exception as e:
    print(f"\n保存失败: {e}")

# ==================== 总结 ====================
print("\n" + "=" * 80)
print("  流程总结")
print("=" * 80)

print(f"""
智能体执行完成:

【组A - 需求分析与目的地推荐】
  [OK] A1: UserRequirementAnalyst - 生成用户画像
  [OK] A2: DestinationMatcher - 匹配 {len(candidates)} 个目的地
  [OK] A3: RankingScorer - 排名 Top {len(ranked)}

【组B - 风格方案设计】
  [OK] B1: ImmersiveDesigner - 沉浸式方案
  [OK] B2: ExplorationDesigner - 探索式方案
  [OK] B3: RelaxationDesigner - 松弛式方案
  [OK] B4: HiddenGemDesigner - 小众宝藏方案

【组C - 详细攻略生成】
  [OK] C1: AttractionScheduler - 景点排程
  [OK] C2: TransportPlanner - 交通规划
  [OK] C3: DiningRecommender - 餐饮推荐
  [OK] C4: AccommodationAdvisor - 住宿建议
  [OK] C5: LLMGuideWriter - 攻略写作

最终结果:
  目的地: {selected_destination}
  风格: {selected_proposal.get('style_name', 'N/A')}
  天数: {requirements['days']} 天
  总预算: {detailed_guide.get('total_budget', 0)} CNY
""")

print("=" * 80)
print("  测试完成")
print("=" * 80)
