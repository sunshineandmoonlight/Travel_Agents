# -*- coding: utf-8 -*-
"""
测试组C智能体（详细攻略生成）

测试流程：
1. AttractionScheduler - 景点排程师
2. TransportPlanner - 交通规划师
3. DiningRecommender - 餐饮推荐师
4. AccommodationAdvisor - 住宿顾问
5. GuideFormatter - 攻略格式化师
"""

import sys
import os
import json

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tradingagents.agents.group_c import generate_detailed_guide
from tradingagents.agents.group_a import DOMESTIC_DESTINATIONS_DB
from tradingagents.agents.group_b import generate_style_proposals


def test_group_c_agents():
    """测试组C智能体"""
    print("=" * 60)
    print("  Group C Agents Test - Detailed Guide Generation")
    print("=" * 60)

    # 测试参数
    destination = "北京"
    dest_data = DOMESTIC_DESTINATIONS_DB[destination]
    days = 3  # 使用3天测试，输出更简洁
    start_date = "2026-04-15"

    user_requirements = {
        "travel_scope": "domestic",
        "start_date": start_date,
        "days": days,
        "adults": 2,
        "children": 0,
        "budget": "medium",
        "interests": ["历史文化", "美食"],
        "special_requests": ""
    }

    user_portrait = {
        "travel_type": "情侣游",
        "travel_scope": "domestic",
        "total_travelers": 2,
        "adults": 2,
        "children": 0,
        "days": days,
        "budget": "medium",
        "budget_level": "舒适型",
        "primary_interests": ["历史文化", "美食"],
        "pace_preference": "均衡型",
        "description": "情侣游、喜欢历史文化,美食、均衡型节奏的旅行者"
    }

    user_requirements["user_portrait"] = user_portrait

    print(f"\n[Setup]")
    print(f"  Destination: {destination}")
    print(f"  Days: {days}")
    print(f"  Start Date: {start_date}")
    print(f"  Budget: {user_portrait['budget_level']}")
    print(f"  Travelers: {user_portrait['total_travelers']}")
    print(f"  Interests: {', '.join(user_portrait['primary_interests'])}")

    # 首先获取风格方案（来自组B）
    print(f"\n[Step 0] Getting style proposals from Group B...")
    style_proposals = generate_style_proposals(destination, dest_data, user_portrait, days)

    # 选择沉浸式风格
    selected_style = style_proposals[0]  # 沉浸式
    print(f"  Selected Style: {selected_style['style_name']} ({selected_style['style_type']})")
    print(f"  Intensity: {selected_style['intensity_level']}/5")
    print(f"  Cost: {selected_style['estimated_cost']} CNY")

    # 测试组C智能体
    print(f"\n[Step 1-5] Running Group C agents...")

    detailed_guide = generate_detailed_guide(
        destination=destination,
        dest_data=dest_data,
        style_proposal=selected_style,
        user_requirements=user_requirements,
        days=days,
        start_date=start_date,
        llm=None
    )

    # 输出结果
    print(f"\n[OK] Detailed guide generated successfully!")

    print(f"\n{'=' * 60}")
    print(f"  DETAILED GUIDE SUMMARY")
    print(f"{'=' * 60}")

    print(f"\nDestination: {detailed_guide['destination']}")
    print(f"Style: {detailed_guide['style_name']} ({detailed_guide['style_type']})")
    print(f"Total Days: {detailed_guide['total_days']}")
    print(f"Start Date: {detailed_guide['start_date']}")

    # 预算明细
    budget = detailed_guide['budget_breakdown']
    print(f"\nBudget Breakdown:")
    print(f"  Total: ¥{budget['total_budget']}")
    print(f"  Attractions: ¥{budget['attractions']}")
    print(f"  Transport: ¥{budget['transport']}")
    print(f"  Dining: ¥{budget['dining']}")
    print(f"  Accommodation: ¥{budget['accommodation']}")

    # 每日行程预览
    print(f"\nDaily Itineraries:")
    for day in detailed_guide['daily_itineraries']:
        print(f"\n  Day {day['day']}: {day['title']}")
        print(f"    Date: {day['date']}")
        print(f"    Pace: {day['pace']}")
        print(f"    Budget: ¥{day['daily_budget']}")
        print(f"    Schedule Items: {len(day['schedule'])}")

        # 显示每个时间段
        for item in day['schedule']:
            print(f"      {item['period']}: {item['activity']}")
            if item.get('location'):
                print(f"        @ {item['location']}")
            if item.get('dining'):
                dining = item['dining']
                if dining:
                    print(f"        🍴 {dining.get('recommended_area', '')}")

    # 汇总信息
    summary = detailed_guide['summary']
    print(f"\nSummary:")
    print(f"  Total Attractions: {summary['total_attractions']}")
    print(f"  Budget Per Day: ¥{summary['budget_per_day']}")
    print(f"  Accommodation: {summary['accommodation_area']}")

    # 打包清单
    print(f"\nPacking List (first 10 items):")
    for item in detailed_guide['packing_list'][:10]:
        print(f"  ☐ {item}")

    # 旅行贴士
    print(f"\nTravel Tips (first 5):")
    for tip in detailed_guide['travel_tips'][:5]:
        print(f"  • {tip}")

    print(f"\n{'=' * 60}")
    print(f"  Group C Agents Test Complete!")
    print(f"{'=' * 60}")

    # 返回测试结果
    return {
        "success": True,
        "guide_generated": True,
        "total_days": detailed_guide['total_days'],
        "total_budget": detailed_guide['budget_breakdown']['total_budget'],
        "total_attractions": summary['total_attractions']
    }


if __name__ == "__main__":
    test_results = test_group_c_agents()
    print("\n\nTest Results Summary:")
    print(json.dumps(test_results, ensure_ascii=False, indent=2))
