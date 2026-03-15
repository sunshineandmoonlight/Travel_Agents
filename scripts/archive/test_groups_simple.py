"""
测试A组、B组、C组的性能和LLM调用次数
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_groups():
    """测试所有组的性能"""
    print("="*70)
    print("旅行规划完整流程性能测试")
    print("="*70)

    from tradingagents.agents.group_a import recommend_destinations
    from tradingagents.agents.group_b import generate_style_proposals
    from tradingagents.agents.group_c import get_specialist_agents
    from langchain_openai import ChatOpenAI

    requirements = {
        'travel_scope': 'domestic',
        'start_date': '2025-05-01',
        'days': 3,
        'adults': 2,
        'children': 0,
        'budget': 'medium',
        'interests': ['文化', '美食', '历史'],
        'special_requests': '希望行程不要太紧凑'
    }

    # 创建LLM
    llm = ChatOpenAI(
        model='Qwen/Qwen2.5-7B-Instruct',
        api_key=os.getenv('SILICONFLOW_API_KEY', ''),
        base_url='https://api.siliconflow.cn/v1',
        temperature=0.7,
        max_tokens=2000,
        timeout=60
    )

    # 追踪LLM调用
    llm_calls = []
    original_invoke = llm.invoke

    def tracked_invoke(messages):
        start = time.time()
        try:
            result = original_invoke(messages)
            duration = time.time() - start
            llm_calls.append({'duration': duration, 'step': 'LLM调用'})
            return result
        except Exception as e:
            error_msg = "ERROR:" + str(e)[:20]
            llm_calls.append({'duration': time.time() - start, 'step': error_msg})
            raise

    llm.invoke = tracked_invoke

    # A组：获取目的地推荐
    print("\n[A组] 获取目的地推荐...")
    start_a = time.time()
    result_a = recommend_destinations(requirements, llm=llm)
    duration_a = time.time() - start_a
    calls_a = len(llm_calls)

    print(f"✅ A组完成")
    print(f"   耗时: {duration_a:.2f}秒")
    print(f"   LLM调用: {calls_a}次")

    # B组：获取风格方案
    destination = result_a['destinations'][0]['destination']
    print(f"\n[B组] 获取风格方案 (目的地: {destination})...")

    llm_calls_before_b = len(llm_calls)
    start_b = time.time()
    result_b = generate_style_proposals(
        destination=destination,
        user_requirements={
            'travel_scope': requirements['travel_scope'],
            'days': requirements['days'],
            'user_portrait': result_a['user_portrait']
        },
        llm=llm
    )
    duration_b = time.time() - start_b
    calls_b = len(llm_calls) - llm_calls_before_b

    print(f"✅ B组完成")
    print(f"   耗时: {duration_b:.2f}秒")
    print(f"   LLM调用: {calls_b}次")
    print(f"   风格方案: {len(result_b.get('styles', []))}个")

    # C组：生成详细攻略
    print(f"\n[C组] 生成详细攻略...")
    specialists = get_specialist_agents()

    print(f"   涉及专家: {len(specialists)}个")
    print(f"   专家列表: {[s.__class__.__name__ for s in specialists]}")

    # 汇总A+B
    total_ab = duration_a + duration_b

    print("\n" + "="*70)
    print("性能测试汇总报告")
    print("="*70)

    print(f"\n{'组别':<10} {'耗时':<15} {'LLM调用':<15} {'说明'}")
    print("-"*70)
    print(f"{'A组':<10} {duration_a:<15.2f} {calls_a:<15} 目的地推荐")
    print(f"{'B组':<10} {duration_b:<15.2f} {calls_b:<15} 风格方案生成")
    print(f"{'C组':<10} {'预计20-30秒':<15} {'预计20-30次':<15} 详细攻略")
    print("-"*70)
    print(f"{'A+B总计':<10} {total_ab:<15.2f} {len(llm_calls):<15} ")
    print("="*70)

    # 详细LLM调用
    print(f"\nLLM调用明细:")
    cumulative = 0
    for i, call in enumerate(llm_calls, 1):
        cumulative += call['duration']
        print(f"  {i}. {call['duration']:.2f}秒 (累计{cumulative:.2f}秒)")

    # C组估算
    print(f"\nC组估算:")
    print(f"  专家数量: {len(specialists)}个")
    print(f"  预计LLM调用: {len(specialists) * 2}-{len(specialists) * 4}次")
    print(f"  预计耗时: 20-30秒")


if __name__ == "__main__":
    test_groups()
