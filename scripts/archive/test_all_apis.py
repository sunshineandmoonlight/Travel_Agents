# -*- coding: utf-8 -*-
"""
测试所有已实现的分阶段规划API接口
"""

import sys
import os
import json
import requests
from datetime import datetime

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8006/api/travel/staged"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_endpoint(name, method, endpoint, data=None):
    """测试单个端点"""
    print(f"\n[{name}] {method} {endpoint}")

    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        else:
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=60)

        response.raise_for_status()
        result = response.json()

        print(f"  ✅ SUCCESS")

        if isinstance(result, dict):
            if "success" in result:
                print(f"  success: {result.get('success')}")
            if "message" in result:
                print(f"  message: {result.get('message')}")
            if "version" in result:
                print(f"  version: {result.get('version')}")
            if "session_id" in result:
                print(f"  session_id: {result.get('session_id')}")
            if "destinations" in result:
                print(f"  destinations: {len(result.get('destinations', []))} 个")
                for i, dest in enumerate(result.get('destinations', [])[:3]):
                    print(f"    [{i+1}] {dest.get('destination', 'N/A')} (匹配度: {dest.get('match_score', 0)}%)")
            if "styles" in result:
                print(f"  styles: {len(result.get('styles', []))} 个")
                for style in result.get('styles', []):
                    print(f"    [{style.get('style_icon', '?')}] {style.get('style_name', 'N/A')} - {style.get('estimated_cost', 0)} CNY")

        return True, result

    except requests.exceptions.RequestException as e:
        print(f"  ❌ FAILED: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Response: {e.response.text[:200]}")
        return False, None

def main():
    print_section("分阶段规划API测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试地址: {BASE_URL}")

    results = {}

    # 测试1: 健康检查
    print_section("测试1: 健康检查")
    success, _ = test_endpoint("健康检查", "GET", "/test")
    results["health_check"] = success

    # 测试2: 提交需求表单
    print_section("测试2: 提交需求表单")
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
    success, result = test_endpoint("提交需求", "POST", "/submit-requirements", requirements)
    results["submit_requirements"] = success

    # 测试3: 获取推荐目的地 (组A智能体)
    print_section("测试3: 获取推荐目的地 (组A智能体)")
    success, result = test_endpoint("获取目的地", "POST", "/get-destinations", requirements)
    results["get_destinations"] = success

    # 提取目的地和用户画像，用于后续测试
    selected_dest = None
    user_portrait = None
    if success and result:
        destinations = result.get("destinations", [])
        if destinations:
            selected_dest = destinations[0]["destination"]
            user_portrait = result.get("user_portrait", {})
            print(f"\n  选中的目的地: {selected_dest}")
            print(f"  用户画像: {user_portrait.get('description', 'N/A')}")

    # 测试4: 获取风格方案 (组B智能体)
    if selected_dest and user_portrait:
        print_section("测试4: 获取风格方案 (组B智能体)")
        styles_request = {
            "destination": selected_dest,
            "user_requirements": {
                "travel_scope": "domestic",
                "days": 5,
                "user_portrait": user_portrait
            }
        }
        success, result = test_endpoint("获取风格方案", "POST", "/get-styles", styles_request)
        results["get_styles"] = success

        if success and result:
            styles = result.get("styles", [])
            print(f"\n  详细风格信息:")
            for style in styles:
                print(f"    [{style['style_icon']}] {style['style_name']} ({style['style_type']})")
                print(f"      - 描述: {style['style_description']}")
                print(f"      - 节奏: {style['daily_pace']}")
                print(f"      - 强度: {style['intensity_level']}/5")
                print(f"      - 费用: {style['estimated_cost']} CNY")
                print(f"      - 适合: {style['best_for']}")
                print(f"      - 亮点: {', '.join(style['highlights'][:2])}...")
    else:
        print("\n[跳过] 无法测试风格方案 - 前置测试失败")
        results["get_styles"] = False

    # 汇总结果
    print_section("测试结果汇总")

    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed

    print(f"\n总计: {total} 个测试")
    print(f"通过: {passed} ✅")
    print(f"失败: {failed} ❌")
    print(f"成功率: {passed/total*100:.1f}%")

    print("\n详细结果:")
    for name, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {name}: {status}")

    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️ {failed} 个测试失败，需要修复")

    return results

if __name__ == "__main__":
    results = main()
    sys.exit(0 if all(results.values()) else 1)
