"""
测试热门目的地图片缓存功能
"""

import requests
import time
import json

API_BASE = "http://localhost:8005/api/travel/images"


def print_json(data):
    """格式化打印JSON"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def test_cache_stats():
    """测试1: 获取缓存统计"""
    print("\n" + "="*60)
    print("测试1: 缓存统计信息")
    print("="*60)

    response = requests.get(f"{API_BASE}/cache/stats")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"缓存大小: {data['cache']['size']}条")
        print(f"缓存命中: {data['cache']['hits']}次")
        print(f"缓存未命中: {data['cache']['misses']}次")
        print(f"命中率: {data['cache']['hit_rate']}")
        print(f"最后刷新: {data['cache'].get('last_refresh', 'N/A')}")
        print(f"下次刷新: {data['cache'].get('next_refresh', 'N/A')}")
        print(f"TTL: {data['cache']['ttl_hours']}小时")
        return data['cache']
    else:
        print(f"错误: {response.text}")
        return None


def test_cache_list():
    """测试2: 获取缓存列表"""
    print("\n" + "="*60)
    print("测试2: 缓存列表")
    print("="*60)

    response = requests.get(f"{API_BASE}/cache/list", params={"limit": 10})

    if response.status_code == 200:
        data = response.json()
        print(f"总缓存数: {data['total']}")
        print(f"返回数: {data['returned']}")
        print("\n前10条缓存:")
        for item in data['items']:
            updated = item['updated_at']
            print(f"  - {item['city']}: {item['source']}")
        return data
    else:
        print(f"错误: {response.text}")
        return None


def test_destination_api_with_cache():
    """测试3: 测试目的地API（使用缓存）"""
    print("\n" + "="*60)
    print("测试3: 目的地API缓存效果")
    print("="*60)

    test_cities = ["三亚", "曼谷", "东京"]

    for city in test_cities:
        # 第一次请求（可能从缓存）
        start = time.time()
        response = requests.get(f"{API_BASE}/destination/{city}", params={"width": 600, "height": 400})
        first_time = time.time() - start

        if response.status_code == 200:
            data = response.json()
            cached = data.get('cached', False)
            source = data.get('source', 'unknown')

            # 第二次请求（应该从缓存）
            start = time.time()
            response = requests.get(f"{API_BASE}/destination/{city}", params={"width": 600, "height": 400})
            second_time = time.time() - start

            data2 = response.json()
            cached2 = data2.get('cached', False)

            print(f"{city}:")
            print(f"  第1次: {first_time:.3f}秒 (缓存: {cached})")
            print(f"  第2次: {second_time:.3f}秒 (缓存: {cached2})")
            print(f"  来源: {source}")
        else:
            print(f"{city}: 请求失败")


def test_preload_api_with_cache():
    """测试4: 测试预加载API（使用缓存）"""
    print("\n" + "="*60)
    print("测试4: 预加载API缓存效果")
    print("="*60)

    start = time.time()
    response = requests.get(f"{API_BASE}/preload/top", params={"limit": 20})
    elapsed = time.time() - start

    if response.status_code == 200:
        data = response.json()
        print(f"总耗时: {elapsed:.2f}秒")
        print(f"返回数量: {data['total']}")
        print(f"缓存命中: {data.get('cache_hits', 0)}")
        print(f"缓存命中率: {data.get('cache_hit_rate', 'N/A')}")

        # 统计图片来源
        sources = {}
        for dest in data['destinations']:
            source = dest['source']
            sources[source] = sources.get(source, 0) + 1

        print("\n图片来源分布:")
        for source, count in sources.items():
            print(f"  - {source}: {count}个")
    else:
        print(f"错误: {response.text}")


def test_cache_refresh():
    """测试5: 测试缓存刷新"""
    print("\n" + "="*60)
    print("测试5: 缓存刷新")
    print("="*60)

    print("正在刷新缓存...")
    start = time.time()
    response = requests.post(f"{API_BASE}/cache/refresh", params={"force": True})
    elapsed = time.time() - start

    if response.status_code == 200:
        data = response.json()
        print(f"刷新完成，耗时: {elapsed:.1f}秒")
        print(f"成功: {data['result']['success']}")
        print(f"失败: {data['result']['failed']}")
        print(f"总计: {data['result']['total']}")
    else:
        print(f"错误: {response.text}")


def test_cache_delete():
    """测试6: 测试删除缓存"""
    print("\n" + "="*60)
    print("测试6: 删除指定城市缓存")
    print("="*60)

    # 先查看缓存统计
    stats_before = requests.get(f"{API_BASE}/cache/stats").json()
    size_before = stats_before['cache']['size']
    print(f"删除前缓存大小: {size_before}")

    # 删除一个城市的缓存
    test_city = "三亚"
    response = requests.delete(f"{API_BASE}/cache/{test_city}")

    if response.status_code == 200:
        print(f"成功删除 {test_city} 的缓存")
    else:
        print(f"删除失败: {response.text}")

    # 再次查看缓存统计
    stats_after = requests.get(f"{API_BASE}/cache/stats").json()
    size_after = stats_after['cache']['size']
    print(f"删除后缓存大小: {size_after}")


def main():
    print("\n" + "="*60)
    print("热门目的地图片缓存功能测试")
    print("="*60)
    print(f"API地址: {API_BASE}")

    try:
        # 测试1: 缓存统计
        cache_stats = test_cache_stats()

        # 测试2: 缓存列表
        test_cache_list()

        # 测试3: 目的地API缓存效果
        test_destination_api_with_cache()

        # 测试4: 预加载API缓存效果
        test_preload_api_with_cache()

        # 测试5: 缓存刷新（可选，耗时较长）
        print("\n" + "="*60)
        print("是否测试缓存刷新? (耗时约30-60秒)")
        choice = input("输入 y 继续，其他键跳过: ").strip().lower()
        if choice == 'y':
            test_cache_refresh()

        # 测试6: 删除缓存
        print("\n" + "="*60)
        print("是否测试删除缓存?")
        choice = input("输入 y 继续，其他键跳过: ").strip().lower()
        if choice == 'y':
            test_cache_delete()

        # 最终统计
        print("\n" + "="*60)
        print("最终缓存统计")
        print("="*60)
        test_cache_stats()

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
