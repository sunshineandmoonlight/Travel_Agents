"""
测试批量LLM评分功能
"""

import sys
import os
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.agents.group_a.destination_matcher import (
    DOMESTIC_DESTINATIONS_DB,
    _batch_calculate_match_scores_with_llm
)

def test_batch_scoring():
    """测试批量LLM评分"""
    from tradingagents.agents.group_a.user_requirement_analyst import create_user_portrait

    # 测试用户需求
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

    print("=" * 70)
    print("批量LLM评分测试")
    print("=" * 70)

    # 1. 创建用户画像
    print("\n[1] 创建用户画像...")
    user_portrait = create_user_portrait(requirements, llm=None)
    print(f"用户画像: {user_portrait.get('description', 'N/A')}")

    # 2. 获取LLM实例
    print("\n[2] 获取LLM实例...")
    from app.routers.staged_planning import get_llm_instance
    llm = get_llm_instance()
    if llm:
        print(f"LLM实例: {type(llm).__name__}")
    else:
        print("警告: LLM实例为None，测试将失败")

    # 3. 测试批量评分
    print("\n[3] 开始批量LLM评分...")
    print(f"目的地数量: {len(DOMESTIC_DESTINATIONS_DB)}")

    start_time = time.time()

    try:
        candidates = _batch_calculate_match_scores_with_llm(
            DOMESTIC_DESTINATIONS_DB,
            user_portrait,
            llm
        )

        elapsed = time.time() - start_time

        print(f"\n[4] 批量评分完成！")
        print(f"耗时: {elapsed:.2f}秒")
        print(f"候选目的地数量: {len(candidates)}")

        # 显示TOP5
        print("\n[5] TOP5推荐目的地:")
        for i, candidate in enumerate(candidates[:5], 1):
            print(f"  {i}. {candidate['destination']} - {candidate['match_score']}分")

        # 性能分析
        print(f"\n[6] 性能分析:")
        print(f"  批量评分耗时: {elapsed:.2f}秒")
        print(f"  平均每个目的地: {elapsed/len(candidates):.2f}秒")
        print(f"  对比逐个调用(14个): ~{14*2.5}秒")

        if elapsed < 10:
            print(f"  ✅ 性能优秀！")
        elif elapsed < 20:
            print(f"  ⚠️  性能一般，可以接受")
        else:
            print(f"  ❌ 性能较差，需要优化")

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n[ERROR] 批量评分失败: {e}")
        print(f"耗时: {elapsed:.2f}秒")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_batch_scoring()
