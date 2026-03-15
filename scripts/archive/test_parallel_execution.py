"""
并行执行测试脚本

测试Group B和Group C的并行执行是否正常工作
"""

import os
import sys
import time

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

from tradingagents.graph.trading_graph import create_llm_by_provider


def test_group_b_parallel():
    """测试Group B的并行执行"""
    print("=" * 60)
    print("测试 Group B (风格设计) 并行执行")
    print("=" * 60)

    # 创建LLM
    llm = create_llm_by_provider(
        provider=os.getenv("LLM_PROVIDER", "siliconflow"),
        model=os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-7B-Instruct"),
        backend_url=os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"),
        temperature=0.7,
        max_tokens=2000,
        timeout=60
    )

    from tradingagents.graph.parallel_execution import ParallelStyleDesigners

    # 测试数据
    destination = "西安"
    dest_data = {
        "tags": ["历史文化", "美食"],
        "highlights": ["兵马俑", "大雁塔"],
        "budget_level": {"medium": 500}
    }
    user_portrait = {
        "travel_type": "情侣游",
        "primary_interests": ["历史文化", "美食"],
        "budget_level": "medium",
        "pace_preference": "沉浸型"
    }
    days = 5

    print(f"\n目的地: {destination}")
    print(f"旅行天数: {days}天")
    print(f"用户偏好: {user_portrait['primary_interests']}")

    # 并行生成4种风格方案
    print("\n开始并行生成4种风格方案...")
    start = time.time()

    parallel_designers = ParallelStyleDesigners(llm)
    proposals = parallel_designers.create_all_proposals(
        destination, dest_data, user_portrait, days
    )

    elapsed = time.time() - start

    print(f"\n完成! 耗时: {elapsed:.2f}秒")
    print(f"生成方案数: {len(proposals)}")

    for proposal in proposals:
        style_name = proposal.get("style_name", "未知")
        intensity = proposal.get("intensity_level", 0)
        print(f"  - {style_name} (强度: {intensity})")

    print(f"\n预估提速: ~4倍 (顺序执行预计{elapsed*4:.1f}秒)")

    return proposals


def test_group_c_parallel():
    """测试Group C的并行执行"""
    print("\n" + "=" * 60)
    print("测试 Group C (详细攻略) 并行执行")
    print("=" * 60)

    # 创建LLM
    llm = create_llm_by_provider(
        provider=os.getenv("LLM_PROVIDER", "siliconflow"),
        model=os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-7B-Instruct"),
        backend_url=os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"),
        temperature=0.7,
        max_tokens=2000,
        timeout=60
    )

    from tradingagents.graph.parallel_execution import ParallelGroupC

    # 测试数据
    destination = "西安"
    dest_data = {
        "tags": ["历史文化", "美食"],
        "highlights": ["兵马俑", "大雁塔"],
        "budget_level": {"medium": 500}
    }
    style_proposal = {
        "style_name": "沉浸式",
        "style_type": "immersive",
        "daily_pace": "慢节奏",
        "intensity_level": 2,
        "estimated_cost": 5000
    }
    user_portrait = {
        "travel_type": "情侣游",
        "primary_interests": ["历史文化", "美食"],
        "budget_level": "medium",
        "pace_preference": "沉浸型",
        "total_travelers": 2
    }
    days = 3  # 使用较少天数以加快测试
    start_date = "2024-04-01"

    print(f"\n目的地: {destination}")
    print(f"旅行天数: {days}天")
    print(f"风格: {style_proposal['style_name']}")

    # 并行执行Group C
    print("\n开始并行执行Group C...")
    print("  阶段1: C1(景点) + C4(住宿) 并行")
    print("  阶段2: C2(交通) + C3(餐饮) 并行")
    print("  阶段3: C5(攻略) 顺序")
    print()

    start = time.time()

    parallel_c = ParallelGroupC(llm)
    results = parallel_c.execute_all(
        destination, dest_data, style_proposal, days, start_date, user_portrait
    )

    elapsed = time.time() - start

    print(f"\n完成! 总耗时: {elapsed:.2f}秒")

    # 显示结果
    if "error" in results:
        print(f"错误: {results['error']}")
    else:
        print(f"\nC1 景点排程: {'✅' if results.get('scheduled_attractions') else '❌'}")
        print(f"C4 住宿建议: {'✅' if results.get('accommodation_plan') else '❌'}")
        print(f"C2 交通规划: {'✅' if results.get('transport_plan') else '❌'}")
        print(f"C3 餐饮推荐: {'✅' if results.get('dining_plan') else '❌'}")
        print(f"C5 攻略生成: {'✅' if results.get('guide_content') else '❌'}")

        if results.get('scheduled_attractions'):
            days_count = len(results['scheduled_attractions'])
            print(f"\n景点排程: {days_count}天")

        if results.get('transport_plan'):
            cost = results['transport_plan'].get('total_transport_cost', 0)
            print(f"交通费用: {cost}元")

    print(f"\n预估提速: ~1.25倍 (顺序执行预计{elapsed*1.25:.1f}秒)")

    return results


def test_parallel_vs_sequential():
    """对比并行和顺序执行的性能"""
    print("\n" + "=" * 60)
    print("性能对比: 并行 vs 顺序")
    print("=" * 60)

    # 创建LLM
    llm = create_llm_by_provider(
        provider=os.getenv("LLM_PROVIDER", "siliconflow"),
        model=os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-7B-Instruct"),
        backend_url=os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"),
        temperature=0.7,
        max_tokens=2000,
        timeout=60
    )

    from tradingagents.agents.group_b import generate_style_proposals, generate_style_proposals_parallel

    destination = "西安"
    dest_data = {
        "tags": ["历史文化"],
        "highlights": [],
        "budget_level": {"medium": 500}
    }
    user_portrait = {
        "travel_type": "情侣游",
        "primary_interests": ["历史文化"],
        "budget_level": "medium",
        "pace_preference": "沉浸型"
    }
    days = 5

    # 顺序执行
    print("\n[顺序执行] 生成4种风格方案...")
    start = time.time()
    sequential_proposals = generate_style_proposals(destination, dest_data, user_portrait, days, llm)
    sequential_time = time.time() - start
    print(f"完成! 耗时: {sequential_time:.2f}秒")

    # 并行执行
    print("\n[并行执行] 生成4种风格方案...")
    import asyncio

    start = time.time()
    parallel_proposals = asyncio.run(generate_style_proposals_parallel(destination, dest_data, user_portrait, days, llm))
    parallel_time = time.time() - start
    print(f"完成! 耗时: {parallel_time:.2f}秒")

    # 结果对比
    speedup = sequential_time / parallel_time
    print(f"\n性能提升: {speedup:.2f}倍")
    print(f"时间节省: {sequential_time - parallel_time:.2f}秒 ({(1-parallel_time/sequential_time)*100:.1f}%)")


if __name__ == "__main__":
    import asyncio

    print("智能体并行执行测试")
    print("=" * 60)

    # 测试Group B
    try:
        test_group_b_parallel()
    except Exception as e:
        print(f"\nGroup B 测试失败: {e}")
        import traceback
        traceback.print_exc()

    # 测试Group C
    try:
        test_group_c_parallel()
    except Exception as e:
        print(f"\nGroup C 测试失败: {e}")
        import traceback
        traceback.print_exc()

    # 性能对比
    try:
        test_parallel_vs_sequential()
    except Exception as e:
        print(f"\n性能对比测试失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
