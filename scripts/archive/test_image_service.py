# -*- coding: utf-8 -*-
"""
测试图片服务（支持回退机制）

测试主图片服务，验证Unsplash和回退机制
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_api_status():
    """测试API状态"""
    print("=" * 60)
    print("Test 1: Unsplash API Status")
    print("=" * 60)

    from tradingagents.services.unsplash_search_service import get_unsplash_service

    service = get_unsplash_service()
    status = service.check_api_status()

    print(f"Configured: {status.get('configured')}")

    if status.get('configured'):
        print(f"Working: {status.get('working')}")
        if status.get('rate_limit'):
            print(f"Rate Limit: {status.get('rate_limit')}")
    else:
        print(f"Message: {status.get('message')}")
        print(f"Setup URL: {status.get('setup_url')}")

    print()
    return status.get('working', False)


def test_main_service():
    """测试主服务（带回退）"""
    print("=" * 60)
    print("Test 2: Main Image Service (with fallback)")
    print("=" * 60)

    from tradingagents.services.attraction_image_service import get_attraction_image

    test_attractions = [
        ("Eiffel Tower", "Paris"),
        ("Forbidden City", "Beijing"),
        ("Statue of Liberty", "New York"),
        ("Colosseum", "Rome"),
    ]

    for attraction, city in test_attractions:
        print(f"\nAttraction: {attraction} ({city})")

        url = get_attraction_image(attraction, city)
        print(f"  URL: {url[:80]}...")

        # 判断图片来源
        if "unsplash.com" in url:
            print(f"  [OK] Real image from Unsplash")
        elif "placehold.co" in url:
            print(f"  [FALLBACK] Placeholder image")
        elif "picsum.photos" in url:
            print(f"  [FALLBACK] Picsum random image")
        else:
            print(f"  [UNKNOWN] Unknown source")

    print()


def test_themed_images():
    """测试主题色图片"""
    print("=" * 60)
    print("Test 3: Themed Images")
    print("=" * 60)

    from tradingagents.services.attraction_image_service import get_themed_image, CITY_COLORS

    print("City Theme Colors:")
    for city, color in CITY_COLORS.items():
        print(f"  {city}: #{color}")

    print("\nThemed Images:")

    test_cases = [
        ("Eiffel Tower", "Paris"),
        ("Forbidden City", "Beijing"),
        ("Big Ben", "London"),
        ("Statue of Liberty", "New York"),
    ]

    for attraction, city in test_cases:
        url = get_themed_image(attraction, city)
        print(f"\n{attraction} ({city}):")
        print(f"  {url[:80]}...")

        # 判断来源
        if "unsplash.com" in url:
            print(f"  [Real] Unsplash image")
        elif "placehold.co" in url:
            # 提取颜色
            import re
            color_match = re.search(r'/([0-9A-Fa-f]{6})/', url)
            if color_match:
                color = color_match.group(1)
                print(f"  [Themed] Placeholder with color #{color}")
            else:
                print(f"  [Themed] Placeholder image")
        else:
            print(f"  [Unknown] Unknown source")

    print()


def test_service_class():
    """测试服务类"""
    print("=" * 60)
    print("Test 4: Service Class")
    print("=" * 60)

    from tradingagents.services.attraction_image_service import get_image_service

    service = get_image_service()

    # 检查API状态
    status = service.check_api_status()
    print(f"API Status: {status}")

    # 批量获取图片
    print("\nBatch Get Images:")
    attractions = [
        {"name": "Eiffel Tower", "city": "Paris"},
        {"name": "Great Wall", "city": "Beijing"},
        {"name": "Colosseum", "city": "Rome"},
    ]

    results = service.batch_get_images(attractions)

    for name, url in results.items():
        print(f"  {name}: {url[:60]}...")

    print()


def test_chinese_attractions():
    """测试中文景点名称"""
    print("=" * 60)
    print("Test 5: Chinese Attraction Names")
    print("=" * 60)

    from tradingagents.services.attraction_image_service import get_attraction_image

    test_attractions = [
        ("埃菲尔铁塔", "巴黎"),
        ("故宫", "北京"),
        ("长城", "北京"),
        ("兵马俑", "西安"),
    ]

    for attraction, city in test_attractions:
        url = get_attraction_image(attraction, city)
        print(f"{attraction} ({city}):")
        print(f"  {url[:70]}...")

    print()


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("Image Service Integration Test")
    print("=" * 60 + "\n")

    # 测试1: API状态
    test_api_status()

    # 测试2: 主服务
    test_main_service()

    # 测试3: 主题色图片
    test_themed_images()

    # 测试4: 服务类
    test_service_class()

    # 测试5: 中文景点
    test_chinese_attractions()

    print("=" * 60)
    print("All Tests Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
