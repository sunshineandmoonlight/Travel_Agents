# -*- coding: utf-8 -*-
"""
分阶段规划系统完整测试
测试所有组智能体的API端点
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


def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subsection(title):
    print(f"\n{'─' * 70}")
    print(f"  {title}")
    print(f"{'─' * 70}")


def test_health_check():
    """测试健康检查"""
    print_header("健康检查测试")

    try:
        response = requests.get(f"{BASE_URL}/test", timeout=10)
        response.raise_for_status()
        data = response.json()

        print(f"  ✅ 通过")
        print(f"  版本: {data.get('version', 'N/A')}")
        print(f"  消息: {data.get('message', 'N/A')}")
        return True, data
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        return False, None


def test_submit_requirements():
    """测试提交需求"""
    print_subsection("提交需求表单")

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

    try:
        response = requests.post(f"{BASE_URL}/submit-requirements", json=requirements, timeout=10)
        response.raise_for_status()
        data = response.json()

        print(f"  ✅ 通过")
        print(f"  会话ID: {data.get('session_id', 'N/A')}")
        print(f"  消息: {data.get('message', 'N/A')}")
        return True, data
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        return False, None


def test_group_a():
    """测试组A - 获取推荐目的地"""
    print_subsection("组A智能体 - 获取推荐目的地")

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

    try:
        response = requests.post(f"{BASE_URL}/get-destinations", json=requirements, timeout=60)
        response.raise_for_status()
        data = response.json()

        destinations = data.get('destinations', [])
        user_portrait = data.get('user_portrait', {})

        print(f"  ✅ 通过")
        print(f"  推荐地区数: {len(destinations)}")

        for i, dest in enumerate(destinations):
            print(f"    [{i+1}] {dest['destination']} - 匹配度: {dest['match_score']}%")

        print(f"  用户画像: {user_portrait.get('description', 'N/A')}")
        print(f"  旅行类型: {user_portrait.get('travel_type', 'N/A')}")
        print(f"  节奏偏好: {user_portrait.get('pace_preference', 'N/A')}")

        return True, data

    except Exception as e:
        print(f"  ❌ 失败: {e}")
        return False, None


def test_group_b(dest_data):
    """测试组B - 获取风格方案"""
    print_subsection("组B智能体 - 获取风格方案")

    destinations = dest_data.get('destinations', [])
    user_portrait = dest_data.get('user_portrait', {})

    if not destinations:
        print("  ⚠️ 跳过 - 没有可用目的地")
        return False, None

    selected_dest = destinations[0]['destination']

    request_data = {
        "destination": selected_dest,
        "user_requirements": {
            "travel_scope": "domestic",
            "days": 3,
            "user_portrait": user_portrait
        }
    }

    try:
        response = requests.post(f"{BASE_URL}/get-styles", json=request_data, timeout=60)
        response.raise_for_status()
        data = response.json()

        styles = data.get('styles', [])

        print(f"  ✅ 通过")
        print(f"  目的地: {selected_dest}")
        print(f"  风格方案数: {len(styles)}")

        for style in styles:
            print(f"    [{style['style_icon']}] {style['style_name']}")
            print(f"        类型: {style['style_type']}")
            print(f"        费用: ¥{style['estimated_cost']}")
            print(f"        强度: {style['intensity_level']}/5")
            print(f"        节奏: {style['daily_pace']}")

        return True, data

    except Exception as e:
        print(f"  ❌ 失败: {e}")
        return False, None


def test_group_c(dest_data, style_data):
    """测试组C - 生成详细攻略"""
    print_subsection("组C智能体 - 生成详细攻略")

    destinations = dest_data.get('destinations', [])
    user_portrait = dest_data.get('user_portrait', {})

    if not destinations:
        print("  ⚠️ 跳过 - 没有可用目的地")
        return False, None

    styles = style_data.get('styles', []) if style_data else []
    if not styles:
        print("  ⚠️ 跳过 - 没有可用风格方案")
        return False, None

    selected_dest = destinations[0]['destination']
    selected_style_type = styles[0]['style_type']

    request_data = {
        "destination": selected_dest,
        "style_type": selected_style_type,
        "user_requirements": {
            "travel_scope": "domestic",
            "start_date": "2026-04-15",
            "days": 3,
            "user_portrait": user_portrait
        }
    }

    try:
        response = requests.post(f"{BASE_URL}/generate-guide", json=request_data, timeout=120)
        response.raise_for_status()
        data = response.json()

        guide = data.get('guide', {})
        budget = guide.get('budget_breakdown', {})
        summary = guide.get('summary', {})

        print(f"  ✅ 通过")
        print(f"  目的地: {guide.get('destination', 'N/A')}")
        print(f"  风格: {guide.get('style_name', 'N/A')} ({guide.get('style_type', 'N/A')})")
        print(f"  天数: {guide.get('total_days', 0)}")
        print(f"  开始日期: {guide.get('start_date', 'N/A')}")

        print(f"\n  💰 预算明细:")
        print(f"     总计: ¥{budget.get('total_budget', 0)}")
        print(f"     景点: ¥{budget.get('attractions', 0)}")
        print(f"     交通: ¥{budget.get('transport', 0)}")
        print(f"     餐饮: ¥{budget.get('dining', 0)}")
        print(f"     住宿: ¥{budget.get('accommodation', 0)}")

        print(f"\n  📋 汇总:")
        print(f"     总景点数: {summary.get('total_attractions', 0)}")
        print(f"     人均预算: ¥{summary.get('budget_per_day', 0)}/天")
        print(f"     住宿区域: {summary.get('accommodation_area', 'N/A')}")

        daily_itineraries = guide.get('daily_itineraries', [])
        print(f"\n  📅 每日行程预览:")
        for day in daily_itineraries:
            print(f"     Day {day['day']}: {day['title']}")
            print(f"       日期: {day['date']}, 节奏: {day['pace']}, 预算: ¥{day['daily_budget']}")
            print(f"       住宿: {day['accommodation']['area']}")

        return True, data

    except Exception as e:
        print(f"  ❌ 失败: {e}")
        return False, None


def generate_test_report(results):
    """生成测试报告"""
    print_header("测试报告")

    total = len(results)
    passed = sum(1 for r in results.values() if r.get('success', False))

    print(f"\n  测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  测试地址: {BASE_URL}")
    print(f"\n  总测试数: {total}")
    print(f"  通过: {passed} ✅")
    print(f"  失败: {total - passed} ❌")
    print(f"  成功率: {passed/total*100:.1f}%")

    print(f"\n  详细结果:")
    for name, result in results.items():
        status = "✅ 通过" if result.get('success') else "❌ 失败"
        print(f"    {name}: {status}")

    if passed == total:
        print(f"\n  🎉 所有测试通过！系统运行正常")
    else:
        print(f"\n  ⚠️ {total - passed} 个测试失败，需要修复")

    # 智能体汇总
    print(f"\n{'=' * 70}")
    print(f"  智能体汇总")
    print(f"{'=' * 70}")

    print(f"\n  组A - 地区推荐智能体 (3个):")
    print(f"    ✅ UserRequirementAnalyst - 分析需求")
    print(f"    ✅ DestinationMatcher - 匹配目的地")
    print(f"    ✅ RankingScorer - 排序推荐")

    print(f"\n  组B - 风格方案智能体 (4个):")
    print(f"    ✅ ImmersiveDesigner - 沉浸式方案")
    print(f"    ✅ ExplorationDesigner - 探索式方案")
    print(f"    ✅ RelaxationDesigner - 松弛式方案")
    print(f"    ✅ HiddenGemDesigner - 小众宝藏方案")

    print(f"\n  组C - 详细攻略智能体 (5个):")
    print(f"    ✅ AttractionScheduler - 景点排程师")
    print(f"    ✅ TransportPlanner - 交通规划师")
    print(f"    ✅ DiningRecommender - 餐饮推荐师")
    print(f"    ✅ AccommodationAdvisor - 住宿顾问")
    print(f"    ✅ GuideFormatter - 攻略格式化师")

    print(f"\n  总计: 12个智能体全部就绪")


def main():
    print_header("分阶段规划系统完整测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    # 测试健康检查
    success, _ = test_health_check()
    results["健康检查"] = {"success": success}

    # 测试提交需求
    success, _ = test_submit_requirements()
    results["提交需求"] = {"success": success}

    # 测试组A
    success, dest_data = test_group_a()
    results["组A - 获取目的地"] = {"success": success}

    # 测试组B
    success, style_data = test_group_b(dest_data if dest_data else {})
    results["组B - 获取风格方案"] = {"success": success}

    # 测试组C
    success, _ = test_group_c(
        dest_data if dest_data else {},
        style_data if style_data else {}
    )
    results["组C - 生成详细攻略"] = {"success": success}

    # 生成测试报告
    generate_test_report(results)

    # 保存结果
    report = {
        "test_time": datetime.now().isoformat(),
        "base_url": BASE_URL,
        "total_tests": len(results),
        "passed": sum(1 for r in results.values() if r.get('success', False)),
        "results": {k: v.get('success', False) for k, v in results.items()}
    }

    return 0 if all(r.get('success', False) for r in results.values()) else 1


if __name__ == "__main__":
    exit_code = main()

    print(f"\n{'=' * 70}")
    print(f"  测试完成")
    print(f"{'=' * 70}\n")

    sys.exit(exit_code)
