# -*- coding: utf-8 -*-
"""
测试分阶段规划API完整流程
Step 1: 获取推荐目的地 (Group A)
Step 2: 获取风格方案 (Group B)
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
    print("=" * 60)
    print("  Testing Full Staged Planning API Flow")
    print("=" * 60)

    # Step 1: Get destinations (Group A)
    print("\n[Step 1/2] Getting destinations and user portrait...")

    body1 = {
        "travel_scope": "domestic",
        "start_date": "2026-04-01",
        "days": 5,
        "adults": 2,
        "children": 0,
        "budget": "medium",
        "interests": ["历史文化", "美食"],
        "special_requests": ""
    }

    try:
        response1 = requests.post(
            f"{BASE_URL}/get-destinations",
            json=body1,
            timeout=60
        )
        response1.raise_for_status()
        data1 = response1.json()

        print(f"  SUCCESS: {len(data1['destinations'])} destinations")

        # Extract first destination
        selected_dest = data1['destinations'][0]['destination']
        user_portrait = data1['user_portrait']

        print(f"  Selected: {selected_dest}")
        print(f"  User Portrait: {user_portrait['description']}")

        # Step 2: Get styles (Group B)
        print("\n[Step 2/2] Getting style proposals...")

        body2 = {
            "destination": selected_dest,
            "user_requirements": {
                "travel_scope": "domestic",
                "days": 5,
                "user_portrait": user_portrait
            }
        }

        response2 = requests.post(
            f"{BASE_URL}/get-styles",
            json=body2,
            timeout=60
        )
        response2.raise_for_status()
        data2 = response2.json()

        print(f"  SUCCESS: {len(data2['styles'])} style proposals")
        print("\n  Style Proposals:")

        for style in data2['styles']:
            print(f"\n    [{style['style_icon']}] {style['style_name']}")
            print(f"      Cost: {style['estimated_cost']} CNY")
            print(f"      Intensity: {style['intensity_level']}/5")
            print(f"      Best For: {style['best_for']}")

        print("\n" + "=" * 60)
        print("  Test Complete - All APIs Working!")
        print("=" * 60)

        return {
            "success": True,
            "destinations": [d['destination'] for d in data1['destinations']],
            "styles": [s['style_type'] for s in data2['styles']]
        }

    except requests.exceptions.RequestException as e:
        print(f"  FAILED: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Response: {e.response.text}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    results = test_full_flow()
    print("\n\nTest Results Summary:")
    print(json.dumps(results, ensure_ascii=False, indent=2))
