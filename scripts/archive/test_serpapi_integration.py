"""
测试SerpAPI国际旅游功能集成

验证扩展后的SerpAPI集成功能
"""

import sys
import os
import io
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 修复Windows编码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import logging
from tradingagents.tools.travel_tools import DestinationSearchTool
from tradingagents.utils.unified_data_interface import InternationalDataProvider

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def test_international_destination_search():
    """测试国际目的地搜索"""
    print("=" * 60)
    print("测试1: 国际目的地实时搜索")
    print("=" * 60)

    tool = DestinationSearchTool()

    # 测试不同关键词的搜索
    keywords = ["海滨", "历史", "美食", "都市"]

    for keyword in keywords:
        print(f"\n🔍 搜索关键词: {keyword}")
        print("-" * 40)

        results = tool.search_destinations(keyword, scope="international")

        if results:
            print(f"✅ 找到 {len(results)} 个目的地:")
            for i, dest in enumerate(results[:4], 1):
                print(f"\n  [{i}] {dest.get('destination', 'N/A')}")
                print(f"      类型: {dest.get('type', 'N/A')}")
                print(f"      描述: {dest.get('description', 'N/A')[:60]}...")
                if dest.get('image_url'):
                    print(f"      图片: ✅ 有图片")
                else:
                    print(f"      图片: ❌ 无图片")
        else:
            print("❌ 未找到结果")


def test_international_attraction_search():
    """测试国际景点搜索"""
    print("\n" + "=" * 60)
    print("测试2: 国际景点搜索")
    print("=" * 60)

    provider = InternationalDataProvider()

    # 测试不同城市的景点搜索
    test_cases = [
        ("Tokyo", "历史"),
        ("Paris", ""),
        ("Bangkok", "美食"),
        ("Rome", "历史"),
    ]

    for city, interest in test_cases:
        print(f"\n🔍 搜索 {city} 的景点" + (f" (兴趣: {interest})" if interest else ""))
        print("-" * 40)

        result = provider.search_attractions(city, interest)

        if result.get("success"):
            attractions = result.get("attractions", [])
            print(f"✅ 找到 {len(attractions)} 个景点:")
            for i, attr in enumerate(attractions[:3], 1):
                print(f"\n  [{i}] {attr.get('name', 'N/A')}")
                print(f"      地址: {attr.get('address', 'N/A')[:50]}...")
                if attr.get('rating'):
                    print(f"      评分: ⭐ {attr.get('rating', 0)}")
                if attr.get('description'):
                    print(f"      描述: {attr.get('description', '')[:60]}...")
        else:
            print(f"❌ 搜索失败: {result.get('error', 'Unknown error')}")


def test_international_restaurant_search():
    """测试国际餐厅搜索"""
    print("\n" + "=" * 60)
    print("测试3: 国际餐厅搜索")
    print("=" * 60)

    provider = InternationalDataProvider()

    test_cases = ["Tokyo", "Paris", "Bangkok"]

    for city in test_cases:
        print(f"\n🔍 搜索 {city} 的餐厅")
        print("-" * 40)

        result = provider.search_restaurants(city, limit=3)

        if result.get("success"):
            restaurants = result.get("restaurants", [])
            print(f"✅ 找到 {len(restaurants)} 家餐厅:")
            for i, rest in enumerate(restaurants[:3], 1):
                print(f"\n  [{i}] {rest.get('name', 'N/A')}")
                print(f"      类型: {rest.get('cuisine_type', 'N/A')}")
                if rest.get('rating'):
                    print(f"      评分: ⭐ {rest.get('rating', 0)}")
        else:
            print(f"❌ 搜索失败: {result.get('error', 'Unknown error')}")


def test_international_route_planning():
    """测试国际路线规划"""
    print("\n" + "=" * 60)
    print("测试4: 国际路线规划")
    print("=" * 60)

    provider = InternationalDataProvider()

    test_cases = [
        ("Tokyo", "Kyoto"),
        ("Paris", "London"),
        ("Bangkok", "Phuket"),
        ("Rome", "Florence"),
    ]

    for origin, dest in test_cases:
        print(f"\n🗺️  规划路线: {origin} → {dest}")
        print("-" * 40)

        result = provider.plan_route(origin, dest)

        if result.get("success"):
            print(f"✅ 距离: {result.get('distance_km', 0)} 公里")
            print(f"推荐交通方式:")
            recommended = result.get("recommended")
            if recommended:
                print(f"  🚀 {recommended.get('method', 'N/A')}")
                print(f"  ⏱️  耗时: {recommended.get('duration', 'N/A')}")
                print(f"  💰 费用: ${recommended.get('cost', 0):.0f} 估算")
        else:
            print(f"❌ 规划失败: {result.get('error', 'Unknown error')}")


def test_international_hotel_search():
    """测试国际酒店搜索"""
    print("\n" + "=" * 60)
    print("测试5: 国际酒店搜索")
    print("=" * 60)

    provider = InternationalDataProvider()

    test_cases = ["Tokyo", "Paris", "Singapore"]

    for city in test_cases:
        print(f"\n🏨 搜索 {city} 的酒店")
        print("-" * 40)

        result = provider.search_hotels(city, limit=3)

        if result.get("success"):
            hotels = result.get("hotels", [])
            print(f"✅ 找到 {len(hotels)} 家酒店:")
            for i, hotel in enumerate(hotels[:2], 1):
                print(f"\n  [{i}] {hotel.get('name', 'N/A')}")
                if hotel.get('price'):
                    print(f"      价格: {hotel.get('price', 'N/A')}")
                if hotel.get('rating'):
                    print(f"      评分: ⭐ {hotel.get('rating', 0)}")
                print(f"      货币: {hotel.get('local_currency', 'N/A')}")
        else:
            print(f"❌ 搜索失败: {result.get('error', 'Unknown error')}")


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("🌍 SerpAPI 国际旅游功能集成测试")
    print("=" * 60)

    try:
        # 运行所有测试
        test_international_destination_search()
        test_international_attraction_search()
        test_international_restaurant_search()
        test_international_route_planning()
        test_international_hotel_search()

        print("\n" + "=" * 60)
        print("✅ 所有测试完成!")
        print("=" * 60)

    except Exception as e:
        logger.error(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
