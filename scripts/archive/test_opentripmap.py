"""
测试OpenTripMap API集成

验证国际景点搜索功能
"""

import sys
import os
import io
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from tradingagents.integrations.opentripmap_client import OpenTripMapClient
from tradingagents.utils.unified_data_interface import InternationalDataProvider

print("=" * 70)
print(" OpenTripMap API 集成测试")
print("=" * 70)


def test_search_by_city():
    """测试按城市搜索景点"""
    print("\n1. 按城市搜索景点")
    print("=" * 70)

    client = OpenTripMapClient()

    cities = ["Paris", "Rome", "Tokyo", "Bangkok"]

    for city in cities:
        print(f"\n🌍 搜索: {city}")
        print("-" * 50)

        result = client.search_attractions_by_name(city, limit=5)

        if result.get("success"):
            print(f"✅ 找到 {result['count']} 个景点:")
            for attr in result["attractions"][:3]:
                print(f"  • {attr['name']}")
                print(f"    类型: {attr['kind']}")
                if attr.get('description'):
                    desc = attr['description'][:80] + "..." if len(attr['description']) > 80 else attr['description']
                    print(f"    描述: {desc}")
                if attr.get('distance'):
                    print(f"    距离: {attr['distance']}米")
        else:
            print(f"❌ 错误: {result.get('error')}")


def test_search_by_type():
    """测试按类型搜索景点"""
    print("\n2. 按类型搜索景点")
    print("=" * 70)

    client = OpenTripMapClient()

    test_cases = [
        ("Rome", "historic", "历史古迹"),
        ("Paris", "museums", "博物馆"),
        ("Tokyo", "religious", "宗教场所"),
    ]

    for city, attr_type, type_name in test_cases:
        print(f"\n🏛️  {city} 的{type_name}")
        print("-" * 50)

        result = client.search_by_type(city, attr_type, limit=3)

        if result.get("success"):
            print(f"✅ 找到 {result['count']} 个景点:")
            for attr in result["attractions"]:
                print(f"  • {attr['name']}")
                if attr.get('address'):
                    print(f"    地址: {attr['address']}")
        else:
            print(f"❌ 错误: {result.get('error')}")


def test_attraction_details():
    """测试获取景点详情"""
    print("\n3. 获取景点详情")
    print("=" * 70)

    client = OpenTripMapClient()

    # 先搜索一个景点获取xid
    search_result = client.search_attractions_by_name("Paris", limit=1)

    if search_result.get("success") and search_result.get("attractions"):
        xid = search_result["attractions"][0].get("xid")
        name = search_result["attractions"][0].get("name")

        print(f"\n📖 获取详情: {name} (xid: {xid})")
        print("-" * 50)

        details = client.get_attraction_details(xid)

        if details.get("success"):
            print(f"  名称: {details.get('name')}")
            print(f"  类型: {details.get('kind')}")
            print(f"  地址: {details.get('address')}")
            if details.get('description'):
                desc = details['description'][:150] + "..." if len(details['description']) > 150 else details['description']
                print(f"  描述: {desc}")
            if details.get('opening_hours'):
                print(f"  开放时间: {details.get('opening_hours')}")
            if details.get('wikipedia'):
                print(f"  维基百科: {details.get('wikipedia')}")
            if details.get('phone'):
                print(f"  电话: {details.get('phone')}")
            if details.get('email'):
                print(f"  邮箱: {details.get('email')}")
        else:
            print(f"❌ 错误: {details.get('error')}")
    else:
        print("❌ 无法获取景点列表")


def test_international_provider():
    """测试InternationalDataProvider集成"""
    print("\n4. InternationalDataProvider 统一接口")
    print("=" * 70)

    provider = InternationalDataProvider()

    test_cases = [
        ("Paris", ""),
        ("Rome", "历史"),
        ("Tokyo", "自然"),
        ("Bangkok", "美食"),
    ]

    for city, interest in test_cases:
        print(f"\n🔍 搜索: {city}" + (f" (兴趣: {interest})" if interest else ""))
        print("-" * 50)

        result = provider.search_attractions(city, interest)

        if result.get("success"):
            attractions = result.get("attractions", [])
            print(f"✅ 找到 {len(attractions)} 个景点 (来源: {result.get('source', 'Unknown')})")
            for attr in attractions[:2]:
                print(f"  • {attr.get('name', 'N/A')}")
                if attr.get('type'):
                    print(f"    类型: {attr.get('type')}")
                if attr.get('distance'):
                    print(f"    距离: {attr.get('distance')}米")
        else:
            print(f"❌ 错误: {result.get('error')}")


def main():
    """主测试函数"""
    try:
        test_search_by_city()
        test_search_by_type()
        test_attraction_details()
        test_international_provider()

        print("\n" + "=" * 70)
        print("✅ OpenTripMap API 测试完成!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
