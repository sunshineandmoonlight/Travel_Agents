# -*- coding: utf-8 -*-
"""
测试组A智能体（地区推荐）- 简化版
"""

import sys
import os
import json

# 设置输出编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tradingagents.agents.group_a import recommend_destinations


def test_group_a():
    print("=" * 60)
    print("  Group A Agents Test - Destination Recommendation")
    print("=" * 60)

    # 测试用例1
    print("\n[Test 1] Domestic - Xi'an Cultural Trip")
    print("-" * 60)

    requirements = {
        "travel_scope": "domestic",
        "start_date": "2026-04-01",
        "days": 5,
        "adults": 2,
        "children": 0,
        "budget": "medium",
        "interests": ["历史文化", "美食"],
        "special_requests": ""
    }

    result = recommend_destinations(requirements)

    print(f"User Portrait: {result['user_portrait']['description']}")
    print(f"\nRecommended Destinations (TOP 4):")

    for i, dest in enumerate(result['destinations'], 1):
        print(f"\n  [{i}] {dest['destination']}")
        print(f"      Match Score: {dest['match_score']}%")
        print(f"      Reason: {dest['recommendation_reason']}")
        print(f"      Budget: {dest['estimated_budget']['per_person']} CNY/person")
        print(f"      Best Season: {dest['best_season']}")
        print(f"      Highlights: {', '.join(dest['highlights'][:3])}")

    # 测试用例2
    print("\n\n" + "=" * 60)
    print("[Test 2] International - Japan Trip")
    print("-" * 60)

    requirements2 = {
        "travel_scope": "international",
        "start_date": "2026-04-01",
        "days": 7,
        "adults": 2,
        "children": 0,
        "budget": "luxury",
        "interests": ["文化", "美食", "购物"],
        "special_requests": "想看樱花"
    }

    result2 = recommend_destinations(requirements2)

    print(f"User Portrait: {result2['user_portrait']['description']}")
    print(f"\nRecommended Destinations (TOP 4):")

    for i, dest in enumerate(result2['destinations'], 1):
        print(f"\n  [{i}] {dest['destination']}")
        print(f"      Match Score: {dest['match_score']}%")
        print(f"      Reason: {dest['recommendation_reason']}")
        print(f"      Budget: {dest['estimated_budget']['per_person']} CNY/person")
        print(f"      Best Season: {dest['best_season']}")
        print(f"      Highlights: {', '.join(dest['highlights'][:3])}")

    print("\n" + "=" * 60)
    print("  Group A Agents Test Complete!")
    print("=" * 60)

    # 返回测试结果
    return {
        "test_1": {
            "success": True,
            "destinations": [d["destination"] for d in result["destinations"]]
        },
        "test_2": {
            "success": True,
            "destinations": [d["destination"] for d in result2["destinations"]]
        }
    }


if __name__ == "__main__":
    test_results = test_group_a()
    print("\n\nTest Results Summary:")
    print(json.dumps(test_results, ensure_ascii=False, indent=2))
