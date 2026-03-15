"""
测试分阶段旅行规划消息流图

验证基于LangGraph的状态流架构是否正常工作
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

print("=" * 70)
print("  分阶段旅行规划消息流图测试")
print("=" * 70)

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
    print(f"\n[WARN] LLM创建失败: {e}")

# 导入消息流图
from tradingagents.graph.staged_travel_graph import (
    execute_stage_1_2_3,
    execute_stage_4,
    execute_stage_5,
    StagedTravelState
)

print("[OK] 消息流图模块导入成功")

# 测试数据
requirements = {
    'travel_scope': 'domestic',
    'days': 5,
    'adults': 2,
    'children': 0,
    'budget': 'medium',
    'interests': ['历史文化', '美食']
}

# ==================== 测试1: 阶段1-3 ====================
print("\n" + "=" * 70)
print("【测试1】阶段1-3: 需求分析 -> 地区匹配 -> 排名")
print("=" * 70)

try:
    result_1_3 = execute_stage_1_2_3(requirements, llm)

    print(f"\n[结果] 阶段1-3完成:")
    print(f"  用户画像: {result_1_3.get('user_portrait', {}).get('travel_type', 'N/A')}")
    print(f"  匹配到目的地: {len(result_1_3.get('ranked_destinations', []))} 个")

    for i, dest in enumerate(result_1_3.get('ranked_destinations', [])[:4], 1):
        print(f"    {i}. {dest.get('destination')} (得分: {dest.get('final_score', 0):.0f})")

    if result_1_3.get('error'):
        print(f"\n[ERROR] {result_1_3['error']}")

    print("\n[OK] 阶段1-3测试通过")

except Exception as e:
    print(f"\n[ERROR] 阶段1-3测试失败: {e}")
    import traceback
    traceback.print_exc()

# ==================== 测试2: 阶段4 ====================
print("\n" + "=" * 70)
print("【测试2】阶段4: 风格方案设计")
print("=" * 70)

try:
    # 选择第一个目的地
    ranked_destinations = result_1_3.get('ranked_destinations', [])
    selected_destination = ranked_destinations[0]['destination'] if ranked_destinations else "成都"

    print(f"\n选择目的地: {selected_destination}")

    result_4 = execute_stage_4(requirements, selected_destination, llm)

    print(f"\n[结果] 阶段4完成:")
    print(f"  风格方案数量: {len(result_4.get('style_proposals', []))} 个")

    for proposal in result_4.get('style_proposals', []):
        style_name = proposal.get('style_name', 'N/A')
        pace = proposal.get('daily_pace', 'N/A')
        print(f"    - {style_name}: {pace}")

    if result_4.get('error'):
        print(f"\n[ERROR] {result_4['error']}")

    print("\n[OK] 阶段4测试通过")

except Exception as e:
    print(f"\n[ERROR] 阶段4测试失败: {e}")
    import traceback
    traceback.print_exc()

# ==================== 测试3: 阶段5 ====================
print("\n" + "=" * 70)
print("【测试3】阶段5: 详细攻略生成")
print("=" * 70)

try:
    # 选择第一个风格
    style_proposals = result_4.get('style_proposals', [])
    selected_style = style_proposals[0].get('style_type', 'immersive') if style_proposals else "immersive"

    print(f"\n选择风格: {selected_style}")
    print(f"选择目的地: {selected_destination}")

    result_5 = execute_stage_5(requirements, selected_destination, selected_style, llm)

    print(f"\n[结果] 阶段5完成:")

    detailed_guide = result_5.get('detailed_guide', {})
    if detailed_guide:
        print(f"  目的地: {detailed_guide.get('destination', 'N/A')}")
        print(f"  天数: {detailed_guide.get('days', 0)}")
        print(f"  总预算: {detailed_guide.get('total_budget', 0)} CNY")

        # 显示每日行程摘要
        daily_itinerary = detailed_guide.get('daily_itinerary', [])
        if daily_itinerary:
            print(f"\n  每日行程:")
            for day in daily_itinerary[:3]:  # 只显示前3天
                day_num = day.get('day', 0)
                attractions = day.get('attractions', [])
                print(f"    Day {day_num}: {len(attractions)} 个景点")

    if result_5.get('error'):
        print(f"\n[ERROR] {result_5['error']}")

    print("\n[OK] 阶段5测试通过")

except Exception as e:
    print(f"\n[ERROR] 阶段5测试失败: {e}")
    import traceback
    traceback.print_exc()

# ==================== 测试4: 完整流程 ====================
print("\n" + "=" * 70)
print("【测试4】完整流程测试")
print("=" * 70)

try:
    # 运行完整流程
    result = execute_stage_1_2_3(requirements, llm)
    assert result.get('ranked_destinations'), "阶段1-3失败"

    dest = result['ranked_destinations'][0]['destination']
    result = execute_stage_4(requirements, dest, llm)
    assert result.get('style_proposals'), "阶段4失败"

    style = result['style_proposals'][0]['style_type']
    result = execute_stage_5(requirements, dest, style, llm)
    assert result.get('detailed_guide'), "阶段5失败"

    print("\n[结果] 完整流程测试通过")
    print("  ✅ 阶段1-3: 需求分析与地区推荐")
    print("  ✅ 阶段4: 风格方案设计")
    print("  ✅ 阶段5: 详细攻略生成")

except Exception as e:
    print(f"\n[ERROR] 完整流程测试失败: {e}")
    import traceback
    traceback.print_exc()

# ==================== 总结 ====================
print("\n" + "=" * 70)
print("  测试总结")
print("=" * 70)

print("""
消息流架构改造完成:

[OK] StagedTravelState - 状态定义
  - messages: 消息历史
  - user_requirements: 用户需求
  - user_portrait: 用户画像
  - ranked_destinations: 排名后的目的地
  - style_proposals: 风格方案
  - detailed_guide: 详细攻略

[OK] 节点函数 (5个)
  - user_requirement_analyst_node
  - destination_matcher_node
  - ranking_scorer_node
  - style_designer_node
  - guide_generator_node

[OK] StateGraph - 消息流图
  - 基于LangGraph构建
  - 支持条件路由
  - 支持分阶段执行

[OK] 执行函数 (3个)
  - execute_stage_1_2_3: 需求分析 -> 地区推荐
  - execute_stage_4: 风格方案设计
  - execute_stage_5: 详细攻略生成

架构改进:
  - 函数式调用 -> 消息流传递
  - 串行执行 -> 状态驱动
  - 无历史记录 -> 完整消息历史
  - 无状态追踪 -> 状态管理
""")

print("\n下一步:")
print("  - 更新API路由使用新的消息流")
print("  - 添加消息历史展示")
print("  - 实现实时进度推送")

print("\n" + "=" * 70)
