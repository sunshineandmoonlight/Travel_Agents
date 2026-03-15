# -*- coding: utf-8 -*-
"""
测试分阶段规划API完整流程
Step 1: 获取推荐目的地 (Group A)
Step 2: 获取风格方案 (Group B)
Step 3: 生成详细攻略 (Group C)
"""

import sys
import os
import json
import requests

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8006/api/travel/staged"


def test_full_flow():
    """测试完整的API流程"""
    print("=" * 70)
    print("  Testing Complete Staged Planning API Flow (Group A -> B -> C)")
    print("=" * 70)

    # 测试参数
    requirements = {
        "travel_scope": "domestic",
        "start_date": "2026-04-15",
        "days": 3,
        "adults": 2,
        "children": 0,
        "budget": "medium",
        "interests": ["历史文化", "美食"],
        "special_requests": ""
    }

    print(f"\n[Input Parameters]")
    print(f"  Travel Scope: {requirements['travel_scope']}")
    print(f"  Start Date: {requirements['start_date']}")
    print(f"  Days: {requirements['days']}")
    print(f"  Budget: {requirements['budget']}")
    print(f"  Interests: {', '.join(requirements['interests'])}")

    # Step 1: Get destinations (Group A)
    print(f"\n{'=' * 70}")
    print(f"  [Step 1/3] Get Destinations (Group A Agents)")
    print(f"{'=' * 70}")

    try:
        response1 = requests.post(
            f"{BASE_URL}/get-destinations",
            json=requirements,
            timeout=60
        )
        response1.raise_for_status()
        data1 = response1.json()

        print(f"  ✅ SUCCESS: {len(data1['destinations'])} destinations")

        # 选择第一个目的地
        selected_dest = data1['destinations'][0]['destination']
        user_portrait = data1['user_portrait']

        print(f"\n  Selected Destination: {selected_dest}")
        print(f"  Match Score: {data1['destinations'][0]['match_score']}%")
        print(f"  User Portrait: {user_portrait['description']}")

    except requests.exceptions.RequestException as e:
        print(f"  ❌ FAILED: {e}")
        return {"success": False, "error": "Step 1 failed"}

    # Step 2: Get styles (Group B)
    print(f"\n{'=' * 70}")
    print(f"  [Step 2/3] Get Style Proposals (Group B Agents)")
    print(f"{'=' * 70}")

    try:
        styles_request = {
            "destination": selected_dest,
            "user_requirements": {
                "travel_scope": "domestic",
                "days": requirements['days'],
                "user_portrait": user_portrait
            }
        }

        response2 = requests.post(
            f"{BASE_URL}/get-styles",
            json=styles_request,
            timeout=60
        )
        response2.raise_for_status()
        data2 = response2.json()

        print(f"  ✅ SUCCESS: {len(data2['styles'])} style proposals")

        # 选择沉浸式风格
        selected_style_type = "immersive"
        selected_style = None
        for style in data2['styles']:
            if style['style_type'] == selected_style_type:
                selected_style = style
                break

        if not selected_style:
            selected_style = data2['styles'][0]
            selected_style_type = selected_style['style_type']

        print(f"\n  Selected Style: {selected_style['style_name']} ({selected_style['style_type']})")
        print(f"  Icon: {selected_style['style_icon']}")
        print(f"  Cost: {selected_style['estimated_cost']} CNY")
        print(f"  Intensity: {selected_style['intensity_level']}/5")
        print(f"  Pace: {selected_style['daily_pace']}")

    except requests.exceptions.RequestException as e:
        print(f"  ❌ FAILED: {e}")
        return {"success": False, "error": "Step 2 failed"}

    # Step 3: Generate detailed guide (Group C)
    print(f"\n{'=' * 70}")
    print(f"  [Step 3/3] Generate Detailed Guide (Group C Agents)")
    print(f"{'=' * 70}")

    try:
        guide_request = {
            "destination": selected_dest,
            "style_type": selected_style_type,
            "user_requirements": {
                "travel_scope": "domestic",
                "start_date": requirements['start_date'],
                "days": requirements['days'],
                "user_portrait": user_portrait
            }
        }

        response3 = requests.post(
            f"{BASE_URL}/generate-guide",
            json=guide_request,
            timeout=120
        )
        response3.raise_for_status()
        data3 = response3.json()

        print(f"  ✅ SUCCESS: Detailed guide generated")

        guide = data3['guide']

        # 显示攻略概要
        print(f"\n  📊 Guide Summary:")
        print(f"     Destination: {guide['destination']}")
        print(f"     Style: {guide['style_name']} ({guide['style_type']})")
        print(f"     Total Days: {guide['total_days']}")
        print(f"     Start Date: {guide['start_date']}")

        # 预算明细
        budget = guide['budget_breakdown']
        print(f"\n  💰 Budget Breakdown:")
        print(f"     Total: ¥{budget['total_budget']}")
        print(f"     Attractions: ¥{budget['attractions']}")
        print(f"     Transport: ¥{budget['transport']}")
        print(f"     Dining: ¥{budget['dining']}")
        print(f"     Accommodation: ¥{budget['accommodation']}")

        # 每日行程
        print(f"\n  📅 Daily Itineraries:")
        for day in guide['daily_itineraries']:
            print(f"\n     Day {day['day']}: {day['title']}")
            print(f"       Date: {day['date']}")
            print(f"       Pace: {day['pace']}")
            print(f"       Budget: ¥{day['daily_budget']}")
            print(f"       Accommodation: {day['accommodation']['area']}")

            # 显示行程安排
            for item in day['schedule'][:4]:  # 只显示前4个
                period_emoji = {
                    "morning": "☀️",
                    "lunch": "🍜",
                    "afternoon": "🌤️",
                    "dinner": "🍽️",
                    "evening": "🌙"
                }
                emoji = period_emoji.get(item['period'], "📍")
                print(f"         {emoji} {item['time_range']} - {item['activity']}")
                if item.get('location'):
                    print(f"            @ {item['location']}")
                if item.get('dining'):
                    dining = item['dining']
                    if dining and dining.get('recommended_area'):
                        print(f"            🍴 {dining['recommended_area']}")

        # 汇总信息
        summary = guide['summary']
        print(f"\n  📋 Summary:")
        print(f"     Total Attractions: {summary['total_attractions']}")
        print(f"     Budget Per Day: ¥{summary['budget_per_day']}")
        print(f"     Accommodation: {summary['accommodation_area']}")

        # 打包清单 (前5项)
        print(f"\n  🎒 Packing List (first 5):")
        for item in guide['packing_list'][:5]:
            print(f"     ☐ {item}")

        # 旅行贴士 (前3条)
        print(f"\n  💡 Travel Tips (first 3):")
        for tip in guide['travel_tips'][:3]:
            print(f"     • {tip}")

    except requests.exceptions.RequestException as e:
        print(f"  ❌ FAILED: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Response: {e.response.text[:500]}")
        return {"success": False, "error": "Step 3 failed"}

    # 完成
    print(f"\n{'=' * 70}")
    print(f"  🎉 Complete Flow Test - ALL STEPS PASSED!")
    print(f"{'=' * 70}")

    return {
        "success": True,
        "destination": selected_dest,
        "style_type": selected_style_type,
        "total_days": requirements['days'],
        "total_budget": budget['total_budget'],
        "total_attractions": summary['total_attractions']
    }


if __name__ == "__main__":
    results = test_full_flow()
    print("\n\n" + "=" * 70)
    print("  FINAL RESULTS")
    print("=" * 70)
    print(json.dumps(results, ensure_ascii=False, indent=2))
