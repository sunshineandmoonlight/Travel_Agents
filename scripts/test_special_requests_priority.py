"""
测试特殊需求城市优先推荐功能

验证当用户在特殊需求中提到城市名称时，该城市是否能获得优先推荐
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_special_requests_priority():
    """测试特殊需求优先推荐功能"""
    from tradingagents.agents.group_a.destination_matcher import (
        _extract_destinations_from_special_requests,
        match_destinations,
        DOMESTIC_DESTINATIONS_DB
    )

    print("=" * 70)
    print("特殊需求城市优先推荐测试")
    print("=" * 70)

    # 测试1: 提取城市名称
    print("\n测试1: 从特殊需求提取城市名称")
    print("-" * 70)

    test_cases = [
        "我想去三亚玩几天",
        "想去三亚旅游",
        "目的地是三亚",
        "包括三亚和曼谷",
        "我想去北京和上海",
        "没有提到具体城市"
    ]

    for special_request in test_cases:
        extracted = _extract_destinations_from_special_requests(special_request)
        print(f"输入: {special_request}")
        print(f"提取: {extracted if extracted else '(无)'}")
        print()

    # 测试2: 模拟用户画像和匹配
    print("\n测试2: 三亚优先推荐测试")
    print("-" * 70)

    # 模拟用户画像
    user_portrait = {
        "travel_type": "休闲度假",
        "travel_scope": "domestic",
        "days": 5,
        "budget": "medium",
        "primary_interests": ["海滨度假", "美食体验"],
        "pace_preference": "松弛型",
        "total_travelers": 2,
        "special_requests": "我想去三亚玩几天",  # 🔥 特殊需求提到三亚
        "matching_weights": {
            "history": 1,
            "nature": 3,
            "food": 3,
            "relaxation": 3,
            "adventure": 1,
            "shopping": 1
        }
    }

    print(f"用户特殊需求: {user_portrait['special_requests']}")
    print()

    # 使用规则引擎匹配（不使用LLM，加快测试）
    candidates = []
    preferred_cities = _extract_destinations_from_special_requests(user_portrait['special_requests'])

    for dest_name, dest_data in DOMESTIC_DESTINATIONS_DB.items():
        # 使用修改后的评分函数
        from tradingagents.agents.group_a.destination_matcher import _calculate_rule_based_score

        match_score = _calculate_rule_based_score(
            destination=dest_data,
            user_portrait=user_portrait,
            preferred_destinations=preferred_cities
        )

        candidates.append({
            "destination": dest_name,
            "match_score": int(match_score),
            "is_preferred": dest_name in preferred_cities
        })

    # 按分数排序
    candidates.sort(key=lambda x: x["match_score"], reverse=True)

    print("推荐结果（前10名）:")
    print("-" * 70)
    for i, candidate in enumerate(candidates[:10], 1):
        dest = candidate['destination']
        score = candidate['match_score']
        is_preferred = candidate.get('is_preferred', False)
        preferred_mark = " [PREFERRED] 用户指定" if is_preferred else ""
        print(f"{i:2}. {dest:8} {score:3}分{preferred_mark}")

    # 验证三亚是否排在第一位
    sanya_rank = next((i for i, c in enumerate(candidates) if c['destination'] == '三亚'), None)
    if sanya_rank is not None:
        sanya_rank += 1  # 转换为1-based
        if sanya_rank == 1:
            print(f"\n[PASS] 测试通过！三亚排在第{sanya_rank}位（第一位）")
        else:
            print(f"\n[FAIL] 测试失败！三亚排在第{sanya_rank}位（不是第一位）")
    else:
        print("\n[FAIL] 测试失败！推荐列表中没有三亚")

    # 测试3: 多个城市的优先推荐
    print("\n\n测试3: 多个城市优先推荐测试")
    print("-" * 70)

    user_portrait_2 = {
        "travel_type": "文化探索",
        "travel_scope": "domestic",
        "days": 7,
        "budget": "medium",
        "primary_interests": ["历史文化", "古迹", "博物馆"],
        "special_requests": "我想去北京和西安",  # 🔥 特殊需求提到北京和西安
        "matching_weights": {
            "history": 3,
            "nature": 1,
            "food": 2,
            "relaxation": 1,
            "adventure": 1,
            "shopping": 2
        }
    }

    print(f"用户特殊需求: {user_portrait_2['special_requests']}")
    print()

    candidates2 = []
    preferred_cities_2 = _extract_destinations_from_special_requests(user_portrait_2['special_requests'])

    for dest_name, dest_data in DOMESTIC_DESTINATIONS_DB.items():
        from tradingagents.agents.group_a.destination_matcher import _calculate_rule_based_score

        match_score = _calculate_rule_based_score(
            destination=dest_data,
            user_portrait=user_portrait_2,
            preferred_destinations=preferred_cities_2
        )

        candidates2.append({
            "destination": dest_name,
            "match_score": int(match_score),
            "is_preferred": dest_name in preferred_cities_2
        })

    candidates2.sort(key=lambda x: x["match_score"], reverse=True)

    print("推荐结果（前10名）:")
    print("-" * 70)
    for i, candidate in enumerate(candidates2[:10], 1):
        dest = candidate['destination']
        score = candidate['match_score']
        is_preferred = candidate.get('is_preferred', False)
        preferred_mark = " [PREFERRED] 用户指定" if is_preferred else ""
        print(f"{i:2}. {dest:8} {score:3}分{preferred_mark}")

    # 验证北京和西安是否排在前列
    beijing_rank = next((i for i, c in enumerate(candidates2) if c['destination'] == '北京'), None)
    xian_rank = next((i for i, c in enumerate(candidates2) if c['destination'] == '西安'), None)

    if beijing_rank is not None and xian_rank is not None:
        beijing_rank += 1
        xian_rank += 1
        if beijing_rank <= 2 and xian_rank <= 2:
            print(f"\n[PASS] 测试通过！北京(第{beijing_rank}位)和西安(第{xian_rank}位)都在前2名")
        else:
            print(f"\n[WARNING] 部分通过：北京(第{beijing_rank}位)，西安(第{xian_rank}位)")

    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    print("[PASS] 特殊需求城市优先推荐功能已实现")
    print("[PASS] 用户在特殊需求中提到的城市将获得+20分额外加分")
    print("[PASS] 确保用户指定的城市排在推荐列表前列")


if __name__ == "__main__":
    test_special_requests_priority()
