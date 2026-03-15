"""
简单测试SerpAPI功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.integrations.serpapi_client import SerpAPIClient

def test_search_attractions():
    print("测试景点搜索...")
    client = SerpAPIClient()

    result = client.search_attractions(
        "tourist attractions in Tokyo",
        "Tokyo, Japan",
        5
    )

    print(f"成功: {result.get('success')}")
    if result.get('success'):
        print(f"找到 {result.get('count', 0)} 个景点")
        for attr in result.get('attractions', [])[:3]:
            print(f"  - {attr.get('name')}")
    else:
        print(f"错误: {result.get('error')}")
    print()


def test_search_restaurants():
    print("测试餐厅搜索...")
    client = SerpAPIClient()

    result = client.search_restaurants(
        "restaurants in Tokyo",
        "Tokyo, Japan",
        3
    )

    print(f"成功: {result.get('success')}")
    if result.get('success'):
        print(f"找到 {result.get('count', 0)} 家餐厅")
        for rest in result.get('restaurants', [])[:3]:
            print(f"  - {rest.get('name')}")
    else:
        print(f"错误: {result.get('error')}")
    print()


def test_search_hotels():
    print("测试酒店搜索...")
    client = SerpAPIClient()

    result = client.search_hotels(
        "hotels in Tokyo",
        "Tokyo, Japan",
        3
    )

    print(f"成功: {result.get('success')}")
    if result.get('success'):
        print(f"找到 {result.get('count', 0)} 家酒店")
        for hotel in result.get('hotels', [])[:3]:
            print(f"  - {hotel.get('name')}")
    else:
        print(f"错误: {result.get('error')}")
    print()


if __name__ == "__main__":
    test_search_attractions()
    test_search_restaurants()
    test_search_hotels()
