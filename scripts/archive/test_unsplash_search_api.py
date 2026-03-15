"""
测试Unsplash Search API集成

验证真实景点图片获取功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.services.unsplash_search_service import (
    get_unsplash_service,
    UnsplashSearchService
)
from tradingagents.services.attraction_image_service import (
    get_attraction_image,
    get_image_service,
    get_themed_image
)


def test_api_status():
    """测试API状态"""
    print("=" * 60)
    print("测试1: 检查Unsplash API状态")
    print("=" * 60)

    service = get_unsplash_service()
    status = service.check_api_status()

    print(f"配置状态: {'已配置' if status.get('configured') else '未配置'}")

    if status.get('configured'):
        print(f"工作状态: {'正常' if status.get('working') else '异常'}")
        if status.get('rate_limit'):
            print(f"速率限制: {status.get('rate_limit')}")
    else:
        print(f"提示: {status.get('message')}")
        print(f"注册地址: {status.get('setup_url')}")

    print()
    return status.get('working', False)


def test_search_photos():
    """测试图片搜索"""
    print("=" * 60)
    print("测试2: 搜索景点图片")
    print("=" * 60)

    service = get_unsplash_service()

    test_queries = [
        ("eiffel tower", "paris"),
        ("great wall", "beijing"),
        ("colosseum", "rome"),
        ("statue of liberty", "new york"),
    ]

    for query, city in test_queries:
        print(f"\n搜索: {query} ({city})")

        result = service.search_photos(
            query=f"{query} {city}",
            per_page=1,
            orientation="landscape"
        )

        if result:
            print(f"  ✅ 成功获取图片")
            print(f"  ID: {result.get('id')}")
            print(f"  URL: {result.get('url', '')[:80]}...")
            print(f"  尺寸: {result.get('width')}x{result.get('height')}")
            if result.get('description'):
                print(f"  描述: {result.get('description')[:60]}...")
        else:
            print(f"  ❌ 未找到图片")

    print()


def test_attraction_images():
    """测试景点图片获取（中文支持）"""
    print("=" * 60)
    print("测试3: 获取景点图片（中英文）")
    print("=" * 60)

    service = get_unsplash_service()

    test_attractions = [
        ("埃菲尔铁塔", "巴黎"),
        ("故宫", "北京"),
        ("长城", "北京"),
        ("Eiffel Tower", "Paris"),
        ("Great Wall", "Beijing"),
    ]

    for attraction, city in test_attractions:
        print(f"\n景点: {attraction} ({city})")

        # 构建搜索词
        query = service._build_search_query(attraction, city)
        print(f"  搜索词: {query}")

        # 获取图片
        url = service.get_attraction_image(attraction, city)
        if url:
            print(f"  ✅ {url[:80]}...")
        else:
            print(f"  ❌ 未找到图片")

    print()


def test_main_service():
    """测试主服务（带回退机制）"""
    print("=" * 60)
    print("测试4: 主服务（带回退）")
    print("=" * 60)

    test_attractions = [
        ("埃菲尔铁塔", "巴黎"),
        ("卢浮宫", "巴黎"),
        ("自由女神", "纽约"),
    ]

    for attraction, city in test_attractions:
        print(f"\n景点: {attraction} ({city})")

        # 使用主服务获取图片（会先尝试Unsplash，失败则用占位图）
        url = get_attraction_image(attraction, city)
        print(f"  URL: {url[:80]}...")

        # 判断是真实图片还是占位图
        if "unsplash" in url:
            print(f"  ✅ 真实图片（Unsplash）")
        elif "placehold.co" in url:
            print(f"  ⚠️ 占位图（Unsplash未配置或失败）")
        elif "picsum" in url:
            print(f"  ⚠️ 随机图（Picsum）")
        else:
            print(f"  ❓ 未知来源")

    print()


def test_themed_images():
    """测试主题色图片"""
    print("=" * 60)
    print("测试5: 主题色图片")
    print("=" * 60)

    from tradingagents.services.attraction_image_service import CITY_COLORS

    print("城市主题色:")
    for city, color in CITY_COLORS.items():
        print(f"  {city}: #{color}")

    print("\n获取主题色图片:")

    test_cases = [
        ("埃菲尔铁塔", "巴黎"),
        ("故宫", "北京"),
        ("大本钟", "伦敦"),
    ]

    for attraction, city in test_cases:
        url = get_themed_image(attraction, city)
        print(f"\n{attraction} ({city}):")
        print(f"  {url[:80]}...")

    print()


def test_batch_search():
    """测试批量搜索"""
    print("=" * 60)
    print("测试6: 批量搜索")
    print("=" * 60)

    service = get_unsplash_service()

    queries = [
        "paris eiffel tower",
        "beijing forbidden city",
        "rome colosseum",
        "new york statue of liberty",
    ]

    print(f"批量搜索 {len(queries)} 个景点...")
    results = service.batch_search(queries, per_page=1)

    for query, url in results.items():
        status = "✅" if url else "❌"
        print(f"  {status} {query}: {url[:60] if url else '未找到'}...")

    print()


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("Unsplash Search API 集成测试")
    print("=" * 60 + "\n")

    # 测试1: API状态
    api_working = test_api_status()

    # 如果API未配置，跳过部分测试
    if not api_working:
        print("⚠️ Unsplash API未配置或未工作")
        print("请设置环境变量 UNSPLASH_ACCESS_KEY")
        print("注册地址: https://unsplash.com/developers")
        print()

    # 测试2: 图片搜索（需要API密钥）
    if api_working:
        test_search_photos()
        test_attraction_images()
        test_batch_search()

    # 测试3: 主服务（始终可测试，包含回退机制）
    test_main_service()

    # 测试4: 主题色图片
    test_themed_images()

    print("=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
