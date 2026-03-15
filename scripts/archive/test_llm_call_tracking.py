"""
测试并监控完整流程中的LLM调用
"""

import sys
import os
import time
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 测试请求数据
TEST_REQUIREMENTS = {
    "travel_scope": "domestic",
    "start_date": "2025-05-01",
    "days": 3,
    "adults": 2,
    "children": 0,
    "budget": "medium",
    "interests": ["文化", "美食", "历史"],
    "special_requests": "希望行程不要太紧凑"
}

# LLM调用追踪
llm_calls = []

def track_llm_call(func_name, duration, details=""):
    """记录LLM调用"""
    llm_calls.append({
        "function": func_name,
        "duration": duration,
        "details": details
    })
    print(f"  [LLM调用] {func_name}: {duration:.2f}秒 - {details}")

def test_complete_flow():
    """测试完整流程并追踪LLM调用"""
    print("="*70)
    print("完整流程LLM调用追踪测试")
    print("="*70)

    # 导入必要的模块
    from tradingagents.agents.group_a import recommend_destinations
    from app.routers.staged_planning import get_llm_instance

    # 获取LLM实例
    print("\n[1] 获取LLM实例...")
    llm = get_llm_instance()
    if not llm:
        print("错误: LLM实例为None")
        return

    print(f"LLM类型: {type(llm).__name__}")

    # 测试完整流程
    print("\n[2] 开始完整流程测试...")
    print("    函数: recommend_destinations")

    start_time = time.time()

    # 包装LLM调用追踪
    original_invoke = llm.invoke
    call_count = [0]

    def tracked_invoke(messages):
        call_count[0] += 1
        call_start = time.time()
        try:
            result = original_invoke(messages)
            call_duration = time.time() - call_start

            # 尝试从消息中提取prompt的前50个字符
            prompt_preview = str(messages[0].content)[:50] if messages else ""

            track_llm_call(
                f"LLM调用#{call_count[0]}",
                call_duration,
                prompt_preview
            )
            return result
        except Exception as e:
            track_llm_call(
                f"LLM调用#{call_count[0]}(失败)",
                time.time() - call_start,
                f"错误: {str(e)[:30]}"
            )
            raise

    # 替换LLM的invoke方法
    llm.invoke = tracked_invoke

    # 执行完整流程
    try:
        result = recommend_destinations(TEST_REQUIREMENTS, llm=llm)
        total_duration = time.time() - start_time

        print(f"\n[3] 流程完成！")
        print(f"总耗时: {total_duration:.2f}秒")
        print(f"LLM调用次数: {len(llm_calls)}")

        # 显示所有LLM调用
        print(f"\n[4] LLM调用明细:")
        print(f"{'序号':<5} {'函数':<25} {'耗时':<10} {'详情'}")
        print("-" * 70)
        for i, call in enumerate(llm_calls, 1):
            print(f"{i:<5} {call['function']:<25} {call['duration']:<10.2f} {call['details'][:40]}")

        # 分析
        total_llm_time = sum(c['duration'] for c in llm_calls)
        print(f"\n[5] 性能分析:")
        print(f"  总耗时: {total_duration:.2f}秒")
        print(f"  LLM调用总耗时: {total_llm_time:.2f}秒 ({total_llm_time/total_duration*100:.1f}%)")
        print(f"  其他耗时: {total_duration - total_llm_time:.2f}秒 ({(total_duration - total_llm_time)/total_duration*100:.1f}%)")
        print(f"  LLM调用次数: {len(llm_calls)}")
        print(f"  平均每次LLM调用: {total_llm_time/len(llm_calls):.2f}秒")

        # 检查是否使用了批量调用
        batch_calls = [c for c in llm_calls if '批量' in c['details']]
        if batch_calls:
            print(f"\n✅ 检测到批量LLM调用: {len(batch_calls)}次")
        else:
            print(f"\n⚠️ 未检测到批量LLM调用，可能还在使用逐个调用")

        # 显示结果
        print(f"\n[6] 推荐结果:")
        destinations = result.get('destinations', [])
        for i, dest in enumerate(destinations[:4], 1):
            print(f"  {i}. {dest['destination']} - {dest['match_score']}分")

    except Exception as e:
        print(f"\n[ERROR] 流程失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_complete_flow()
