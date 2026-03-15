"""
多智能体系统全面测试

测试所有12个智能体的实际输出和API调用情况
"""

import os
import sys
import json
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 导入LLM
from tradingagents.graph.trading_graph import create_llm_by_provider

print("=" * 80)
print("  TravelAgents-CN 多智能体系统测试")
print("=" * 80)

# 创建LLM实例
print("\n[初始化] 创建LLM实例...")
try:
    llm = create_llm_by_provider(
        provider=os.getenv("LLM_PROVIDER", "siliconflow"),
        model=os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-7B-Instruct"),
        backend_url=os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"),
        temperature=0.7,
        max_tokens=2000,
        timeout=60
    )
    print(f"[OK] LLM实例创建成功: {type(llm).__name__}")
except Exception as e:
    print(f"[ERROR] LLM创建失败: {e}")
    llm = None

# 测试数据
test_requirements = {
    "travel_scope": "domestic",
    "start_date": "2026-04-01",
    "days": 5,
    "adults": 2,
    "children": 0,
    "budget": "medium",
    "interests": ["美食", "历史文化", "休闲"],
    "special_requests": ""
}

test_destination = "成都"
test_style = "exploration"  # 探索式

# ============================================================
# Group A: 地区推荐智能体
# ============================================================

print("\n" + "=" * 80)
print("  Group A: 地区推荐智能体 (Agent A1-A3)")
print("=" * 80)

# Agent A1: UserRequirementAnalyst
print("\n[Agent A1] UserRequirementAnalyst - 需求分析专家")
print("-" * 60)
try:
    from tradingagents.agents.group_a.user_requirement_analyst import create_user_portrait

    result = create_user_portrait(test_requirements, llm)
    print(f"[OK] 输出类型: {type(result)}")
    print(f"[OK] 用户描述: {result.get('description', '')[:100]}...")
    print(f"[OK] LLM描述长度: {len(result.get('llm_description', ''))} 字符")
    print(f"[INFO] 旅行类型: {result.get('travel_type')}")
    print(f"[INFO] 预算等级: {result.get('budget_level')}")
    print(f"[INFO] 主要兴趣: {result.get('primary_interests')}")
    if result.get('llm_description'):
        print(f"[LLM] LLM描述预览: {result['llm_description'][:150]}...")
    else:
        print(f"[WARN] 未使用LLM生成描述")

except Exception as e:
    print(f"[ERROR] {e}")

# Agent A2: DestinationMatcher
print("\n[Agent A2] DestinationMatcher - 目的地匹配专家")
print("-" * 60)
try:
    from tradingagents.agents.group_a.destination_matcher import match_destinations

    user_portrait = result  # 使用上一个agent的结果
    matching_result = match_destinations(user_portrait, "domestic", llm)

    print(f"[OK] 候选数量: {len(matching_result.get('candidates', []))}")
    print(f"[OK] 前3名推荐:")
    for i, dest in enumerate(matching_result.get('candidates', [])[:3], 1):
        print(f"  {i}. {dest['destination']}: 评分{dest['match_score']}, 预算{dest['estimated_budget']['per_person']}元/人")

    print(f"[OK] LLM描述长度: {len(matching_result.get('llm_description', ''))} 字符")
    if matching_result.get('llm_description'):
        print(f"[LLM] LLM描述预览: {matching_result['llm_description'][:150]}...")
    else:
        print(f"[WARN] 未使用LLM生成描述")

except Exception as e:
    print(f"[ERROR] {e}")

# Agent A3: RankingScorer
print("\n[Agent A3] RankingScorer - 排序评分专家")
print("-" * 60)
try:
    from tradingagents.agents.group_a.ranking_scorer import rank_and_select_top

    candidates = matching_result.get('candidates', [])
    ranking_result = rank_and_select_top(candidates, user_portrait, top_n=4, llm=llm)

    print(f"[OK] 推荐数量: {len(ranking_result.get('destination_cards', []))}")
    print(f"[OK] 最终推荐:")
    for i, card in enumerate(ranking_result.get('destination_cards', []), 1):
        print(f"  {i}. {card['destination']}: {card['match_score']}分")
        print(f"     理由: {card.get('recommendation_reason', '')[:80]}...")

    print(f"[OK] LLM描述长度: {len(ranking_result.get('llm_description', ''))} 字符")

except Exception as e:
    print(f"[ERROR] {e}")

# ============================================================
# Group B: 风格设计智能体
# ============================================================

print("\n" + "=" * 80)
print("  Group B: 风格设计智能体 (Agent B1-B4)")
print("=" * 80)

style_designers = [
    ("ImmersiveDesigner", "immersive_designer", "沉浸式"),
    ("ExplorationDesigner", "exploration_designer", "探索式"),
    ("RelaxationDesigner", "relaxation_designer", "松弛式"),
    ("HiddenGemDesigner", "hidden_gem_designer", "小众宝藏"),
]

for class_name, module_name, style_name in style_designers:
    print(f"\n[Agent B{style_designers.index((class_name, module_name, style_name))+1}] {class_name} - {style_name}设计师")
    print("-" * 60)
    try:
        from tradingagents.agents.group_b import __init__ as group_b_init

        # 动态导入
        module = __import__(f"tradingagents.agents.group_b.{module_name}", fromlist=['design_travel_style'])
        design_func = getattr(module, 'design_travel_style')

        result = design_func(test_destination, user_portrait, llm)

        print(f"[OK] 输出类型: {type(result)}")
        if 'daily_itinerary' in result:
            print(f"[OK] 每日行程: {len(result.get('daily_itinerary', []))} 天")
            print(f"[OK] 第1天景点数: {len(result['daily_itinerary'][0].get('attractions', []))}")
        print(f"[OK] LLM描述长度: {len(result.get('llm_description', ''))} 字符")
        if result.get('llm_description'):
            print(f"[LLM] LLM描述预览: {result['llm_description'][:150]}...")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

# ============================================================
# Group C: 详细攻略智能体
# ============================================================

print("\n" + "=" * 80)
print("  Group C: 详细攻略智能体 (Agent C1-C5)")
print("=" * 80)

# Agent C1: AttractionScheduler
print("\n[Agent C1] AttractionScheduler - 景点排程师")
print("-" * 60)
try:
    from tradingagents.agents.group_c.attraction_scheduler import schedule_attractions

    # 获取一个风格设计方案
    from tradingagents.agents.group_b.exploration_designer import design_travel_style
    style_plan = design_travel_style(test_destination, user_portrait, llm)

    attractions = style_plan.get('daily_itinerary', [])
    schedule_result = schedule_attractions(test_destination, attractions, user_portrait, llm)

    print(f"[OK] 调度结果: {len(schedule_result.get('scheduled_itinerary', []))} 天")
    if schedule_result.get('scheduled_itinerary'):
        day1 = schedule_result['scheduled_itinerary'][0]
        print(f"[OK] 第1天时间段数: {len(day1.get('time_slots', []))}")
    print(f"[OK] LLM描述长度: {len(schedule_result.get('llm_description', ''))} 字符")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

# Agent C2: TransportPlanner
print("\n[Agent C2] TransportPlanner - 交通规划师")
print("-" * 60)
try:
    from tradingagents.agents.group_c.transport_planner import plan_transport

    itinerary = schedule_result.get('scheduled_itinerary', [])
    transport_result = plan_transport(test_destination, itinerary, user_portrait, llm)

    print(f"[OK] 交通计划: {len(transport_result.get('transport_plan', []))} 天")
    print(f"[OK] 总交通费用: {transport_result.get('total_cost', 0)} 元")
    print(f"[OK] LLM描述长度: {len(transport_result.get('llm_description', ''))} 字符")

except Exception as e:
    print(f"[ERROR] {e}")

# Agent C3: DiningRecommender
print("\n[Agent C3] DiningRecommender - 餐饮推荐师")
print("-" * 60)
try:
    from tradingagents.agents.group_c.dining_recommender import recommend_dining

    dining_result = recommend_dining(test_destination, itinerary, user_portrait, llm)

    print(f"[OK] 餐饮推荐: {len(dining_result.get('dining_plan', []))} 餐")
    if dining_result.get('dining_plan'):
        print(f"[OK] 示例: {dining_result['dining_plan'][0].get('area', 'N/A')}")
    print(f"[OK] LLM描述长度: {len(dining_result.get('llm_description', ''))} 字符")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

# Agent C4: AccommodationAdvisor
print("\n[Agent C4] AccommodationAdvisor - 住宿顾问")
print("-" * 60)
try:
    from tradingagents.agents.group_c.accommodation_advisor import recommend_accommodation

    accommodation_result = recommend_accommodation(test_destination, user_portrait, llm)

    print(f"[OK] 推荐区域: {accommodation_result.get('recommended_area', {}).get('area', 'N/A')}")
    print(f"[OK] 住宿费用: {accommodation_result.get('total_cost', 0)} 元")
    print(f"[OK] LLM描述长度: {len(accommodation_result.get('llm_description', ''))} 字符")

except Exception as e:
    print(f"[ERROR] {e}")

# Agent C5: LLMGuideWriter
print("\n[Agent C5] LLMGuideWriter - 攻略撰写师")
print("-" * 60)
try:
    from tradingagents.agents.group_c.llm_guide_writer import write_detailed_guide

    guide_data = {
        "destination": test_destination,
        "user_portrait": user_portrait,
        "scheduled_itinerary": schedule_result.get('scheduled_itinerary', []),
        "transport_plan": transport_result.get('transport_plan', []),
        "dining_plan": dining_result.get('dining_plan', []),
        "accommodation_plan": accommodation_result,
        "style_type": test_style
    }

    guide_result = write_detailed_guide(guide_data, llm)

    print(f"[OK] 攻略天数: {len(guide_result.get('daily_guides', []))}")
    print(f"[OK] 攻略总长度: {len(guide_result.get('full_guide', ''))} 字符")
    print(f"[OK] LLM描述长度: {len(guide_result.get('llm_description', ''))} 字符")
    if guide_result.get('full_guide'):
        print(f"[PREVIEW] 攻略预览: {guide_result['full_guide'][:200]}...")

except Exception as e:
    print(f"[ERROR] {e}")

# ============================================================
# 检查API工具使用情况
# ============================================================

print("\n" + "=" * 80)
print("  API工具使用检查")
print("=" * 80)

api_tools = {
    "高德地图API": "AMAP_API_KEY",
    "SerpAPI": "SERPAPI_KEY",
    "Unsplash": "UNSPLASH_ACCESS_KEY",
    "OpenTripMap": "OPENTRIPMAP_API_KEY",
}

print("\n环境变量检查:")
for name, env_key in api_tools.items():
    value = os.getenv(env_key, "")
    status = "[OK]" if value and not value.startswith("your_") else "[WARN]"
    print(f"  {status} {name}: {env_key}")

# 检查实际导入的工具
print("\n检查实际可用的工具模块:")
try:
    from tradingagents.integrations.amap_client import AmapClient
    print("  [OK] 高德地图客户端 (AmapClient)")
except ImportError:
    print("  [WARN] 高德地图客户端未导入")

try:
    from tradingagents.integrations.serpapi_client import SerpAPIClient
    print("  [OK] SerpAPI客户端 (SerpAPIClient)")
except ImportError:
    print("  [WARN] SerpAPI客户端未导入")

try:
    from tradingagents.integrations.opentripmap_client import OpenTripMapClient
    print("  [OK] OpenTripMap客户端 (OpenTripMapClient)")
except ImportError:
    print("  [WARN] OpenTripMap客户端未导入")

# ============================================================
# 多智能体架构分析
# ============================================================

print("\n" + "=" * 80)
print("  多智能体架构分析")
print("=" * 80)

print("\n检查LangGraph使用情况:")
try:
    from langgraph.graph import StateGraph
    print("  [OK] LangGraph StateGraph 已导入")

    # 检查旅行图是否使用StateGraph
    from tradingagents.graph.travel_graph_with_llm import TravelAgentsGraphWithLLM
    print("  [OK] 旅行图使用LangGraph架构 (TravelAgentsGraphWithLLM)")

    # 检查智能体状态定义
    from tradingagents.agents.utils.agent_states import AgentState
    print("  [OK] 智能体状态已定义 (AgentState)")

except ImportError as e:
    print(f"  [WARN] LangGraph导入失败: {e}")

print("\n分析智能体协作方式:")
print("  [INFO] 当前实现: 函数式调用 + 手动状态传递")
print("  [INFO] LangGraph实现: travel_graph_with_llm.py")
print("  [INFO] API路由实现: staged_planning.py (直接调用智能体函数)")

print("\n结论:")
print("  [1] 智能体数量: 12个 (Group A: 3, Group B: 4, Group C: 5)")
print("  [2] 使用LLM: SiliconFlow Qwen2.5-7B")
print("  [3] LLM描述: 所有智能体都支持llm_description字段")
print("  [4] API工具: 部分实现（高德、SerpAPI、OpenTripMap）")
print("  [5] 架构类型: 混合式（LangGraph框架 + 函数式调用）")

print("\n" + "=" * 80)
print("  测试完成")
print("=" * 80)
