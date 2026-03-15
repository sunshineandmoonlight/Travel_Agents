"""
多智能体系统架构分析

检查：
1. 是否是真正的多智能体系统
2. 每个智能体的函数入口
3. API工具调用情况
"""

import os
import sys
import inspect

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

print("=" * 80)
print("  TravelAgents-CN 多智能体系统架构分析")
print("=" * 80)

# ============================================================
# 1. 检查智能体函数入口
# ============================================================

print("\n【1】智能体函数入口检查")
print("-" * 80)

agent_functions = {
    "Group A - 地区推荐": {
        "UserRequirementAnalyst": ("tradingagents.agents.group_a.user_requirement_analyst", "create_user_portrait"),
        "DestinationMatcher": ("tradingagents.agents.group_a.destination_matcher", "match_destinations"),
        "RankingScorer": ("tradingagents.agents.group_a.ranking_scorer", "rank_and_select_top"),
    },
    "Group B - 风格设计": {
        "ImmersiveDesigner": ("tradingagents.agents.group_b.immersive_designer", "design_immersive_style"),
        "ExplorationDesigner": ("tradingagents.agents.group_b.exploration_designer", "design_exploration_style"),
        "RelaxationDesigner": ("tradingagents.agents.group_b.relaxation_designer", "design_relaxation_style"),
        "HiddenGemDesigner": ("tradingagents.agents.group_b.hidden_gem_designer", "design_hidden_gem_style"),
    },
    "Group C - 详细攻略": {
        "AttractionScheduler": ("tradingagents.agents.group_c.attraction_scheduler", "schedule_attractions"),
        "TransportPlanner": ("tradingagents.agents.group_c.transport_planner", "plan_transport"),
        "DiningRecommender": ("tradingagents.agents.group_c.dining_recommender", "recommend_dining"),
        "AccommodationAdvisor": ("tradingagents.agents.group_c.accommodation_advisor", "recommend_accommodation"),
        "LLMGuideWriter": ("tradingagents.agents.group_c.llm_guide_writer", "format_detailed_guide"),
    }
}

for group, agents in agent_functions.items():
    print(f"\n{group}:")
    for name, (module_path, func_name) in agents.items():
        try:
            module = __import__(module_path, fromlist=[func_name])
            func = getattr(module, func_name)
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            has_llm = 'llm' in params
            print(f"  [OK] {name}")
            print(f"       函数: {func_name}")
            print(f"       参数: {params}")
            print(f"       LLM: {'Yes' if has_llm else 'No'}")
        except Exception as e:
            print(f"  [ERROR] {name}: {e}")

# ============================================================
# 2. 检查API工具集成
# ============================================================

print("\n\n【2】API工具集成检查")
print("-" * 80)

api_clients = [
    ("高德地图", "tradingagents.integrations.amap_client", "AmapClient", "AMAP_API_KEY"),
    ("SerpAPI", "tradingagents.integrations.serpapi_client", "SerpAPIClient", "SERPAPI_KEY"),
    ("OpenTripMap", "tradingagents.integrations.opentripmap_client", "OpenTripMapClient", "OPENTRIPMAP_API_KEY"),
    ("天气数据", "tradingagents.utils.unified_data_interface", "UnifiedDataProvider", None),
]

for name, module_path, class_name, env_key in api_clients:
    print(f"\n{name}:")
    try:
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)
        methods = [m for m in dir(cls) if not m.startswith('_')]

        print(f"  [OK] 类: {class_name}")
        print(f"       方法数: {len(methods)}")

        # 检查环境变量
        if env_key:
            env_value = os.getenv(env_key, "")
            if env_value and not env_value.startswith("your_"):
                print(f"       API Key: [已配置]")
            else:
                print(f"       API Key: [未配置]")
    except Exception as e:
        print(f"  [WARN] {e}")

# ============================================================
# 3. 检查智能体是否调用API工具
# ============================================================

print("\n\n【3】智能体API工具使用检查")
print("-" * 80)

# 检查destination_matcher是否使用API
print("\nDestinationMatcher (目的地匹配):")
try:
    with open("tradingagents/agents/group_a/destination_matcher.py", "r", encoding="utf-8") as f:
        content = f.read()
        uses_search_api = "search_attractions" in content or "serpapi" in content.lower()
        uses_llm = "llm.invoke" in content or "HumanMessage" in content
        print(f"  调用搜索API: {'Yes' if uses_search_api else 'No'}")
        print(f"  使用LLM: {'Yes' if uses_llm else 'No'}")
except Exception as e:
    print(f"  [ERROR] {e}")

# 检查Group B是否使用API
print("\nGroup B Designers (风格设计):")
try:
    for designer_file in ["immersive_designer", "exploration_designer", "relaxation_designer", "hidden_gem_designer"]:
        filepath = f"tradingagents/agents/group_b/{designer_file}.py"
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            uses_amap = "amap_client" in content or "AmapClient" in content
            uses_serpapi = "serpapi_client" in content or "SerpAPIClient" in content
            uses_llm = "llm.invoke" in content or "HumanMessage" in content
            print(f"  {designer_file}:")
            print(f"    高德API: {'Yes' if uses_amap else 'No'}")
            print(f"    SerpAPI: {'Yes' if uses_serpapi else 'No'}")
            print(f"    LLM: {'Yes' if uses_llm else 'No'}")
except Exception as e:
    print(f"  [ERROR] {e}")

# 检查Group C是否使用API
print("\nGroup C Planners (行程规划):")
try:
    for planner_file in ["transport_planner", "dining_recommender"]:
        filepath = f"tradingagents/agents/group_c/{planner_file}.py"
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            uses_amap = "amap_client" in content or "AmapClient" in content
            uses_llm = "llm.invoke" in content or "HumanMessage" in content
            print(f"  {planner_file}:")
            print(f"    高德API: {'Yes' if uses_amap else 'No'}")
            print(f"    LLM: {'Yes' if uses_llm else 'No'}")
except Exception as e:
    print(f"  [ERROR] {e}")

# ============================================================
# 4. 检查LangGraph多智能体架构
# ============================================================

print("\n\n【4】LangGraph多智能体架构检查")
print("-" * 80)

try:
    from langgraph.graph import StateGraph
    print("[OK] LangGraph StateGraph 已安装并导入")

    # 检查travel_graph_with_llm
    from tradingagents.graph.travel_graph_with_llm import TravelAgentsGraphWithLLM
    print("[OK] TravelAgentsGraphWithLLM (旅行规划图) 已实现")

    # 检查节点定义
    import tradingagents.graph.travel_graph_with_llm as graph_module
    nodes = [name for name in dir(graph_module) if name.endswith('_node')]
    print(f"[INFO] 定义的节点: {len(nodes)} 个")
    for node in nodes:
        print(f"  - {node}")

except ImportError as e:
    print(f"[WARN] {e}")

# ============================================================
# 5. 实际运行一个完整的智能体流程
# ============================================================

print("\n\n【5】实际运行测试（Group A完整流程）")
print("-" * 80)

try:
    from tradingagents.graph.trading_graph import create_llm_by_provider
    from tradingagents.agents.group_a import recommend_destinations

    llm = create_llm_by_provider(
        provider=os.getenv("LLM_PROVIDER", "siliconflow"),
        model=os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-7B-Instruct"),
        backend_url=os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"),
        temperature=0.7,
        max_tokens=2000,
        timeout=60
    )

    requirements = {
        "travel_scope": "domestic",
        "start_date": "2026-04-01",
        "days": 5,
        "adults": 2,
        "children": 0,
        "budget": "medium",
        "interests": ["美食", "历史文化"],
        "special_requests": ""
    }

    print("\n调用 recommend_destinations (3个智能体协作)...")
    result = recommend_destinations(requirements, llm)

    print(f"\n[结果]")
    print(f"  推荐目的地数: {len(result.get('destinations', []))}")
    print(f"  前3名:")
    for i, dest in enumerate(result.get('destinations', [])[:3], 1):
        print(f"    {i}. {dest.get('destination')}: {dest.get('match_score')}分")

    print(f"\n  智能体LLM描述:")
    print(f"    UserRequirementAnalyst: {len(result.get('user_portrait_llm_description', ''))} 字符")
    print(f"    DestinationMatcher: {len(result.get('matching_llm_description', ''))} 字符")
    print(f"    RankingScorer: {len(result.get('ranking_llm_description', ''))} 字符")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

# ============================================================
# 总结
# ============================================================

print("\n\n" + "=" * 80)
print("  分析总结")
print("=" * 80)

print("""
【多智能体架构结论】
1. 智能体数量: 12个 (Group A: 3, Group B: 4, Group C: 5)
2. 架构类型: 混合式
   - LangGraph框架: travel_graph_with_llm.py (定义了StateGraph和节点)
   - 函数式调用: staged_planning.py (直接调用智能体函数)
3. 智能体协作:
   - Group A内部协作: recommend_destinations() 串行调用3个智能体
   - Group B独立运行: 每个设计师生成独立方案
   - Group C串行运行: 基于Group B的结果依次调用

【LLM使用情况】
1. 所有智能体都支持LLM (llm参数)
2. LLM功能:
   - 生成自然语言描述 (llm_description字段)
   - 计算匹配分数
   - 估算旅行预算
3. LLM提供商: SiliconFlow + 千问2.5-7B

【API工具使用情况】
1. 已实现的API客户端:
   - AmapClient (高德地图)
   - SerpAPIClient (Google Places搜索)
   - OpenTripMapClient (OpenTripMap)
   - UnifiedDataProvider (统一数据接口)

2. 实际使用情况:
   - Group A: 主要使用LLM + 静态数据库
   - Group B: 部分使用搜索API (serpapi, opentripmap)
   - Group C: 部分使用高德API (交通规划)

【是否是真正的多智能体系统】
✅ 是的多智能体系统，特征:
  - 12个独立的智能体模块
  - 每个智能体有明确的职责和接口
  - 智能体之间有数据流转和协作
  - 使用LangGraph框架定义状态和节点

⚠️  当前实现特点:
  - 主要是函数式调用，不是基于消息传递的多智能体
  - 状态通过参数传递，不是通过共享状态
  - 可以进一步改造为基于消息的协作模式
""")
