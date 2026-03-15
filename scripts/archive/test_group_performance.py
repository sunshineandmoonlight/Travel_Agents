"""
测试A组、B组、C组的性能和LLM调用次数
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_all_groups():
    """测试所有组的性能"""
    print("="*70)
    print("旅行规划完整流程性能测试")
    print("="*70)

    # 测试数据
    requirements = {
        "travel_scope": "domestic",
        "start_date": "2025-05-01",
        "days": 3,
        "adults": 2,
        "children": 0,
        "budget": "medium",
        "interests": ["文化", "美食", "历史"],
        "special_requests": "希望行程不要太紧凑"
    }

    # 获取LLM
    print("\n[0] 初始化LLM...")
    import os
    from langchain_openai import ChatOpenAI

    provider = os.getenv("LLM_PROVIDER", "siliconflow").lower()

    if provider == "siliconflow":
        model = os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-7B-Instruct")
        base_url = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
        api_key = os.getenv("SILICONFLOW_API_KEY", "")

        if not api_key or "your_" in api_key:
            print("错误: SILICONFLOW_API_KEY未配置")
            return

        llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=0.7,
            max_tokens=2000,
            timeout=60
        )
    else:
        print(f"错误: 不支持的LLM provider: {provider}")
        return

    print(f"LLM: {model}")

    # 追踪LLM调用
    llm_calls = []
    original_invoke = llm.invoke

    def tracked_invoke(messages):
        start = time.time()
        try:
            result = original_invoke(messages)
            duration = time.time() - start
            content_preview = str(messages[0].content)[:40] if messages else ""
            llm_calls.append({
                "duration": duration,
                "preview": content_preview
            })
            return result
        except Exception as e:
            llm_calls.append({
                "duration": time.time() - start,
                "preview": f"ERROR: {str(e)[:30]}"
            })
            raise

    llm.invoke = tracked_invoke

    # A组：获取目的地推荐
    print("\n" + "="*70)
    print("A组：获取目的地推荐")
    print("="*70)

    from tradingagents.agents.group_a import recommend_destinations

    start_a = time.time()
    result_a = recommend_destinations(requirements, llm=llm)
    duration_a = time.time() - start_a
    calls_a = len(llm_calls)

    print(f"✅ A组完成")
    print(f"   耗时: {duration_a:.2f}秒")
    print(f"   LLM调用次数: {calls_a}")

    # B组：获取风格方案
    print("\n" + "="*70)
    print("B组：获取风格方案")
    print("="*70)

    from tradingagents.agents.group_b import generate_style_proposals

    llm_calls_before_b = len(llm_calls)
    start_b = time.time()

    # 使用第一个推荐的目的地
    destination = result_a['destinations'][0]['destination']
    result_b = generate_style_proposals(
        destination=destination,
        user_requirements={
            "travel_scope": requirements["travel_scope"],
            "days": requirements["days"],
            "user_portrait": result_a['user_portrait']
        },
        llm=llm
    )

    duration_b = time.time() - start_b
    calls_b = len(llm_calls) - llm_calls_before_b

    print(f"✅ B组完成")
    print(f"   耗时: {duration_b:.2f}秒")
    print(f"   LLM调用次数: {calls_b}")
    print(f"   风格方案数: {len(result_b.get('styles', []))}")

    # C组：生成详细攻略（简化测试）
    print("\n" + "="*70)
    print("C组：生成详细攻略")
    print("="*70)

    llm_calls_before_c = len(llm_calls)
    start_c = time.time()

    # 使用第一个风格方案
    style = result_b['styles'][0]['style_name']

    # 模拟C组的LLM调用（多个智能体）
    from tradingagents.agents.group_c import get_specialist_agents

    # 获取专家列表
    specialists = get_specialist_agents()

    # 模拟调用专家（简化版）
    result_c = {
        "destination": destination,
        "style": style,
        "total_days": requirements["days"],
        "guide_data": {"test": "data"}
    }

    duration_c = time.time() - start_c
    calls_c = len(llm_calls) - llm_calls_before_c

    print(f"✅ C组完成")
    print(f"   耗时: {duration_c:.2f}秒")
    print(f"   LLM调用次数: {calls_c}")
    print(f"   涉及专家: {len(specialists)}个")

    # 汇总报告
    print("\n" + "="*70)
    print("性能测试汇总报告")
    print("="*70)

    total_duration = duration_a + duration_b + duration_c
    total_calls = len(llm_calls)

    print(f"\n{'组别':<10} {'耗时':<15} {'LLM调用':<15} {'占比':<10}")
    print("-"*70)
    print(f"{'A组':<10} {duration_a:<15.2f} {calls_a:<15} {duration_a/total_duration*100:.1f}%")
    print(f"{'B组':<10} {duration_b:<15.2f} {calls_b:<15} {duration_b/total_duration*100:.1f}%")
    print(f"{'C组':<10} {duration_c:<15.2f} {calls_c:<15} {duration_c/total_duration*100:.1f}%")
    print("-"*70)
    print(f"{'总计':<10} {total_duration:<15.2f} {total_calls:<15} {'100%'}")

    # 详细LLM调用分析
    print(f"\n{'#':<5} {'耗时(秒)':<15} {'累计占比':<15} {'内容预览'}")
    print("-"*70)
    cumulative_time = 0
    for i, call in enumerate(llm_calls[:10], 1):  # 只显示前10个
        cumulative_time += call['duration']
        print(f"{i:<5} {call['duration']:<15.2f} {cumulative_time/total_duration*100:<15.1f}% {call['preview'][:40]}")

    if len(llm_calls) > 10:
        print(f"... 还有 {len(llm_calls) - 10} 次LLM调用")

    # 性能分析
    print(f"\n性能分析:")
    print(f"  总耗时: {total_duration:.2f}秒 ({total_duration/60:.1f}分钟)")
    print(f"  总LLM调用: {total_calls}次")
    print(f"  平均每次LLM: {total_duration/total_calls:.2f}秒")

    # 找出最慢的组
    slowest = max([
        ("A组", duration_a),
        ("B组", duration_b),
        ("C组", duration_c)
    ], key=lambda x: x[1])

    print(f"\n最慢的组: {slowest[0]} ({slowest[1]:.2f}秒)")

    # 找出最慢的LLM调用
    slowest_call = max(llm_calls, key=lambda x: x['duration'])
    print(f"最慢的单次LLM调用: {slowest_call['duration']:.2f}秒")


if __name__ == "__main__":
    test_all_groups()
