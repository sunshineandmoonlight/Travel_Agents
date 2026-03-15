# -*- coding: utf-8 -*-
"""
测试组B智能体（风格方案设计师）

测试流程：
1. ImmersiveDesigner - 沉浸式方案
2. ExplorationDesigner - 探索式方案
3. RelaxationDesigner - 松弛式方案
4. HiddenGemDesigner - 小众宝藏方案
"""

import sys
import os
import json

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tradingagents.agents.group_b import generate_style_proposals
from tradingagents.agents.group_a import DOMESTIC_DESTINATIONS_DB


def test_group_b_agents():
    """测试组B智能体"""
    print("=" * 60)
    print("  Group B Agents Test - Style Proposal Designers")
    print("=" * 60)

    # 测试用例
    print("\n[Test] Generating 4 Style Proposals for Beijing")
    print("-" * 60)

    # 模拟用户选择
    destination = "北京"
    dest_data = DOMESTIC_DESTINATIONS_DB[destination]

    user_portrait = {
        "travel_type": "情侣游",
        "travel_scope": "domestic",
        "total_travelers": 2,
        "adults": 2,
        "children": 0,
        "days": 5,
        "budget": "medium",
        "budget_level": "舒适型",
        "primary_interests": ["历史文化", "美食"],
        "pace_preference": "均衡型",
        "description": "情侣游、喜欢历史文化,美食、均衡型节奏的旅行者"
    }

    print(f"Destination: {destination}")
    print(f"Days: {user_portrait['days']}")
    print(f"Budget: {user_portrait['budget_level']}")
    print(f"Interests: {', '.join(user_portrait['primary_interests'])}")
    print()

    # 生成4种风格方案
    proposals = generate_style_proposals(destination, dest_data, user_portrait, 5)

    print(f"[OK] Generated {len(proposals)} style proposals:")
    print()

    for proposal in proposals:
        print(f"\n  [{proposal['style_icon']}] {proposal['style_name']}")
        print(f"      Type: {proposal['style_type']}")
        print(f"      Description: {proposal['style_description']}")
        print(f"      Pace: {proposal['daily_pace']}")
        print(f"      Intensity: {proposal['intensity_level']}/5")
        print(f"      Cost: {proposal['estimated_cost']} CNY total")
        print(f"      Best For: {proposal['best_for']}")
        print(f"      Highlights:")
        for h in proposal['highlights'][:3]:
            print(f"        - {h}")
        print(f"      Preview:")
        for preview_item in proposal['preview_itinerary'][:2]:
            print(f"        Day {preview_item['day']}: {preview_item['title']}")
            print(f"          Attractions: {', '.join(preview_item['attractions'][:2])}")

    print("\n" + "=" * 60)
    print("  Group B Agents Test Complete!")
    print("=" * 60)

    # 返回测试结果
    return {
        "success": True,
        "styles": [p["style_type"] for p in proposals],
        "total_cost": {
            p["style_type"]: p["estimated_cost"] for p in proposals
        }
    }


if __name__ == "__main__":
    test_results = test_group_b_agents()
    print("\n\nTest Results Summary:")
    print(json.dumps(test_results, ensure_ascii=False, indent=2))
