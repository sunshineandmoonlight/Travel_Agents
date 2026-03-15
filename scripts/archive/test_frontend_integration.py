"""
分阶段旅行规划系统 - 前后端集成测试

测试完整的API流程，确保前后端集成正常
"""

import requests
import json
import sys
from typing import Dict, Any, List

# 配置
BACKEND_URL = "http://localhost:8006"
FRONTEND_URL = "http://localhost:4002"
API_BASE = f"{BACKEND_URL}/api/travel/staged"

# 颜色输出
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

def print_success(msg: str):
    print(f"{Colors.GREEN}[OK] {msg}{Colors.RESET}")

def print_error(msg: str):
    print(f"{Colors.RED}[FAIL] {msg}{Colors.RESET}")

def print_info(msg: str):
    print(f"{Colors.BLUE}[INFO] {msg}{Colors.RESET}")

def print_section(msg: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*50}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{msg:^50}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*50}{Colors.RESET}\n")

def test_backend_connection() -> bool:
    """测试后端连接"""
    print_section("测试1: 后端连接")
    try:
        response = requests.get(f"{API_BASE}/test", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"后端连接成功 (v{data.get('version', 'N/A')})")
            print_info(f"时间戳: {data.get('timestamp', 'N/A')}")
            return True
        else:
            print_error(f"后端返回错误状态码: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"无法连接到后端: {e}")
        print_info(f"请确保后端运行在 {BACKEND_URL}")
        return False

def test_destinations_api() -> tuple[bool, Dict[str, Any]]:
    """测试获取目的地API"""
    print_section("测试2: 获取推荐目的地")

    req_data = {
        'travel_scope': 'domestic',
        'start_date': '2026-04-15',
        'days': 3,
        'adults': 2,
        'children': 0,
        'budget': 'medium',
        'interests': ['历史文化', '美食'],
        'special_requests': ''
    }

    try:
        response = requests.post(f"{API_BASE}/get-destinations", json=req_data, timeout=30)
        if response.status_code != 200:
            print_error(f"API返回错误状态码: {response.status_code}")
            return False, {}

        data = response.json()
        if not data.get('success'):
            print_error("API返回success=false")
            return False, {}

        destinations = data.get('destinations', [])
        user_portrait = data.get('user_portrait', {})

        print_success(f"获取到 {len(destinations)} 个目的地推荐")

        for i, dest in enumerate(destinations, 1):
            print(f"\n  {Colors.BOLD}Destination {i}: {dest['destination']}{Colors.RESET}")
            print(f"  - Match: {Colors.GREEN}{dest['match_score']}%{Colors.RESET}")
            print(f"  - Budget: CNY{dest['estimated_budget']['total']} (CNY{dest['estimated_budget'].get('per_person', 'N/A')}/person)")
            print(f"  - Best Season: {dest['best_season']}")
            print(f"  - Suitable for: {', '.join(dest.get('suitableFor', dest.get('suitable_for', []))[:2])}")

        print(f"\n  {Colors.BOLD}User Portrait:{Colors.RESET}")
        print(f"  - Type: {user_portrait.get('travel_type', 'N/A')}")
        print(f"  - Pace: {user_portrait.get('pace_preference', 'N/A')}")
        print(f"  - Budget: {user_portrait.get('budget_level', 'N/A')}")

        return True, {'destinations': destinations, 'user_portrait': user_portrait}

    except Exception as e:
        print_error(f"请求失败: {e}")
        return False, {}

def test_styles_api(dest_name: str, user_portrait: Dict[str, Any]) -> tuple[bool, List]:
    """测试获取风格方案API"""
    print_section("测试3: 获取风格方案")

    req_data = {
        'destination': dest_name,
        'user_requirements': {
            'travel_scope': 'domestic',
            'days': 3,
            'user_portrait': user_portrait
        }
    }

    try:
        response = requests.post(f"{API_BASE}/get-styles", json=req_data, timeout=30)
        if response.status_code != 200:
            print_error(f"API返回错误状态码: {response.status_code}")
            return False, []

        data = response.json()
        if not data.get('success'):
            print_error("API返回success=false")
            return False, []

        styles = data.get('styles', [])
        print_success(f"获取到 {len(styles)} 种风格方案")

        for style in styles:
            intensity = '#' * style['intensity_level'] + '-' * (5 - style['intensity_level'])
            # Handle emoji encoding issues
            icon = style.get('style_icon', '?')
            try:
                icon.encode('gbk')
            except:
                icon = '[ICON]'
            print(f"\n  {Colors.BOLD}{icon} {style['style_name']}{Colors.RESET}")
            print(f"  - Type: {style['style_type']}")
            print(f"  - Intensity: {Colors.GREEN}{intensity}{Colors.RESET}")
            print(f"  - Pace: {style['daily_pace']}")
            print(f"  - Cost: CNY{style['estimated_cost']}")
            print(f"  - Best for: {style['best_for']}")

        return True, styles

    except Exception as e:
        print_error(f"请求失败: {e}")
        return False, []

def test_generate_guide_api(dest_name: str, style_type: str, user_portrait: Dict[str, Any]) -> bool:
    """测试生成详细攻略API"""
    print_section("测试4: 生成详细攻略")

    req_data = {
        'destination': dest_name,
        'style_type': style_type,
        'user_requirements': {
            'travel_scope': 'domestic',
            'start_date': '2026-04-15',
            'days': 3,
            'user_portrait': user_portrait
        }
    }

    try:
        response = requests.post(f"{API_BASE}/generate-guide", json=req_data, timeout=60)
        if response.status_code != 200:
            print_error(f"API返回错误状态码: {response.status_code}")
            return False

        data = response.json()
        if not data.get('success'):
            print_error("API返回success=false")
            return False

        guide = data.get('guide', {})
        print_success(f"成功生成 {guide['total_days']} 天详细攻略")
        print_info(f"目的地: {guide['destination']}")
        print_info(f"风格: {guide['style_name']}")

        # 预算分解
        budget = guide.get('budget_breakdown', {})
        print(f"\n  {Colors.BOLD}Budget Breakdown:{Colors.RESET}")
        print(f"  - Total: {Colors.GREEN}CNY{budget.get('total_budget', 0)}{Colors.RESET}")
        print(f"  - Attractions: CNY{budget.get('attractions', 0)}")
        print(f"  - Transport: CNY{budget.get('transport', 0)}")
        print(f"  - Dining: CNY{budget.get('dining', 0)}")
        print(f"  - Accommodation: CNY{budget.get('accommodation', 0)}")

        # 每日行程
        itineraries = guide.get('daily_itineraries', [])
        print(f"\n  {Colors.BOLD}Daily Itinerary:{Colors.RESET}")
        for day in itineraries:
            print(f"\n  {Colors.BOLD}Day {day['day']}: {day['title']}{Colors.RESET}")
            print(f"  - Date: {day.get('date', 'N/A')}")
            print(f"  - Pace: {day.get('pace', 'N/A')}")
            print(f"  - Budget: CNY{day.get('daily_budget', 0)}")

        # 汇总信息
        summary = guide.get('summary', {})
        print(f"\n  {Colors.BOLD}Summary:{Colors.RESET}")
        print(f"  - Total Attractions: {summary.get('total_attractions', 0)}")
        print(f"  - Avg Daily Budget: CNY{summary.get('budget_per_day', 0)}")
        print(f"  - Accommodation Area: {summary.get('accommodation_area', 'N/A')}")

        # 打包清单
        packing_list = guide.get('packing_list', [])
        if packing_list:
            print(f"\n  {Colors.BOLD}Packing List ({len(packing_list)} items):{Colors.RESET}")
            for item in packing_list[:5]:
                print(f"  - {item}")
            if len(packing_list) > 5:
                print(f"  - ... and {len(packing_list) - 5} more items")

        return True

    except Exception as e:
        print_error(f"请求失败: {e}")
        return False

def test_frontend_connection() -> bool:
    """测试前端连接"""
    print_section("测试5: 前端连接")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print_success(f"前端页面可访问")
            print_info(f"访问地址: {FRONTEND_URL}/travel/staged")
            return True
        else:
            print_error(f"前端返回错误状态码: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"无法连接到前端: {e}")
        print_info(f"请确保前端运行在 {FRONTEND_URL}")
        return False

def main():
    """主测试函数"""
    print(f"\n{Colors.BOLD}{Colors.PURPLE}{'='*50}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{'分阶段旅行规划系统 - 集成测试':^50}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{'='*50}{Colors.RESET}\n")

    print_info(f"后端地址: {BACKEND_URL}")
    print_info(f"前端地址: {FRONTEND_URL}")
    print_info(f"测试时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = []

    # Test 1: Backend connection
    results.append(("后端连接", test_backend_connection()))

    if not results[-1][1]:
        print_error("\n后端未运行，测试终止")
        sys.exit(1)

    # Test 2: Destinations API
    success, data = test_destinations_api()
    results.append(("获取目的地", success))

    if not success:
        print_error("\n获取目的地失败，测试终止")
        sys.exit(1)

    dest_name = data['destinations'][0]['destination']
    user_portrait = data['user_portrait']

    # Test 3: Styles API
    success, styles = test_styles_api(dest_name, user_portrait)
    results.append(("获取风格方案", success))

    if not success or not styles:
        print_error("\n获取风格方案失败，测试终止")
        sys.exit(1)

    style_type = styles[0]['style_type']

    # Test 4: Generate Guide API
    results.append(("生成详细攻略", test_generate_guide_api(dest_name, style_type, user_portrait)))

    # Test 5: Frontend connection
    results.append(("前端连接", test_frontend_connection()))

    # Summary
    print_section("测试结果汇总")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        if result:
            print_success(f"{name}")
        else:
            print_error(f"{name}")

    print(f"\n{Colors.BOLD}通过率: {passed}/{total} ({passed*100//total}%){Colors.RESET}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}[SUCCESS] All tests passed! System is ready to use.{Colors.RESET}\n")
        print(f"{Colors.BOLD}Next steps:{Colors.RESET}")
        print(f"  1. Visit {FRONTEND_URL}/travel/staged for manual testing")
        print(f"  2. Test the complete 5-stage user flow")
        print(f"  3. Verify UI interactions and animations")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}[FAILED] Some tests failed. Please check error messages.{Colors.RESET}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
