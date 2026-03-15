"""
测试组A智能体（地区推荐）

测试流程：
1. UserRequirementAnalyst - 分析需求
2. DestinationMatcher - 匹配目的地
3. RankingScorer - 排序推荐
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tradingagents.agents.group_a import recommend_destinations


def test_group_a_agents():
    """测试组A智能体"""
    print("=" * 60)
    print("  组A智能体测试 - 地区推荐")
    print("=" * 60)

    # 测试用例1: 国内游
    print("\n【测试1】国内游 - 西安历史文化之旅")
    print("-" * 60)

    requirements_1 = {
        "travel_scope": "domestic",
        "start_date": "2026-04-01",
        "days": 5,
        "adults": 2,
        "children": 0,
        "budget": "medium",
        "interests": ["历史文化", "美食"],
        "special_requests": ""
    }

    print(f"输入: {requirements_1}")
    print()

    result_1 = recommend_destinations(requirements_1)

    print(f"[OK] 推荐完成!")
    print(f"用户画像: {result_1['user_portrait']['description']}")
    print(f"\n推荐目的地 (TOP 4):")
    for i, dest in enumerate(result_1['destinations'], 1):
        print(f"\n  [{i}] {dest['destination']}")
        print(f"      匹配度: {dest['match_score']}%")
        print(f"      推荐理由: {dest['recommendation_reason']}")
        print(f"      预估费用: ¥{dest['estimated_budget']['per_person']}/人")
        print(f"      最佳季节: {dest['best_season']}")
        print(f"      热门景点: {', '.join(dest['highlights'][:3])}")

    # 测试用例2: 国际游
    print("\n\n" + "=" * 60)
    print("【测试2】国际游 - 日本樱花之旅")
    print("-" * 60)

    requirements_2 = {
        "travel_scope": "international",
        "start_date": "2026-04-01",
        "days": 7,
        "adults": 2,
        "children": 0,
        "budget": "luxury",
        "interests": ["文化", "美食", "购物"],
        "special_requests": "想看樱花"
    }

    print(f"输入: {requirements_2}")
    print()

    result_2 = recommend_destinations(requirements_2)

    print(f"[OK] 推荐完成!")
    print(f"用户画像: {result_2['user_portrait']['description']}")
    print(f"\n推荐目的地 (TOP 4):")
    for i, dest in enumerate(result_2['destinations'], 1):
        print(f"\n  [{i}] {dest['destination']}")
        print(f"      匹配度: {dest['match_score']}%")
        print(f"      推荐理由: {dest['recommendation_reason']}")
        print(f"      预估费用: ¥{dest['estimated_budget']['per_person']}/人")
        print(f"      最佳季节: {dest['best_season']}")
        print(f"      热门景点: {', '.join(dest['highlights'][:3])}")

    # 测试用例3: 亲子游
    print("\n\n" + "=" * 60)
    print("【测试3】亲子游 - 三亚海滨度假")
    print("-" * 60)

    requirements_3 = {
        "travel_scope": "domestic",
        "start_date": "2026-07-01",
        "days": 4,
        "adults": 2,
        "children": 1,
        "budget": "medium",
        "interests": ["海滨", "休闲", "亲子娱乐"],
        "special_requests": ""
    }

    print(f"输入: {requirements_3}")
    print()

    result_3 = recommend_destinations(requirements_3)

    print(f"[OK] 推荐完成!")
    print(f"用户画像: {result_3['user_portrait']['description']}")
    print(f"\n推荐目的地 (TOP 4):")
    for i, dest in enumerate(result_3['destinations'], 1):
        print(f"\n  [{i}] {dest['destination']}")
        print(f"      匹配度: {dest['match_score']}%")
        print(f"      推荐理由: {dest['recommendation_reason']}")
        print(f"      预估费用: ¥{dest['estimated_budget']['per_person']}/人")
        print(f"      最佳季节: {dest['best_season']}")
        print(f"      热门景点: {', '.join(dest['highlights'][:3])}")

    print("\n" + "=" * 60)
    print("  组A智能体测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    test_group_a_agents()
