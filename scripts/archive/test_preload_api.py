"""
测试热门城市图片预加载API
"""

import requests
import time
import concurrent.futures

API_BASE = "http://localhost:8005/api/travel/images"


def test_top_destinations_api():
    """测试TOP热门城市API"""
    print("\n" + "="*60)
    print("测试1: TOP热门城市图片API")
    print("="*60)

    start = time.time()
    response = requests.get(f"{API_BASE}/preload/top", params={"limit": 20}, timeout=60)
    elapsed = time.time() - start

    print(f"状态码: {response.status_code}")
    print(f"耗时: {elapsed:.2f}秒")

    if response.status_code == 200:
        data = response.json()
        print(f"返回数量: {data['total']}")
        print("\n前5个城市:")
        for dest in data['destinations'][:5]:
            print(f"  - {dest['city']}: {dest['source']}")
            print(f"    URL: {dest['url'][:60]}...")
        return data
    else:
        print(f"错误: {response.text}")
        return None


def test_popular_destinations_api():
    """测试热门城市API（按地区）"""
    print("\n" + "="*60)
    print("测试2: 热门城市图片API（按地区）")
    print("="*60)

    regions = ["china", "southeast_asia", "east_asia", "europe"]

    for region in regions:
        start = time.time()
        response = requests.get(
            f"{API_BASE}/preload/popular",
            params={"limit": 10, "region": region},
            timeout=60
        )
        elapsed = time.time() - start

        if response.status_code == 200:
            data = response.json()
            print(f"{region}: {data['total']}个城市, {elapsed:.2f}秒")
        else:
            print(f"{region}: 失败")


def test_destinations_list_api():
    """测试城市列表API"""
    print("\n" + "="*60)
    print("测试3: 城市列表API")
    print("="*60)

    start = time.time()
    response = requests.get(f"{API_BASE}/destinations/list", timeout=10)
    elapsed = time.time() - start

    print(f"状态码: {response.status_code}")
    print(f"耗时: {elapsed:.2f}秒")

    if response.status_code == 200:
        data = response.json()
        print(f"总城市数: {data['total']}")
        print(f"地区数: {len(data['regions'])}")
        print(f"地区: {', '.join(data['regions'])}")


def test_parallel_preload():
    """测试并行预加载性能"""
    print("\n" + "="*60)
    print("测试4: 并行预加载性能")
    print("="*60)

    # 获取TOP 20城市
    start = time.time()
    response = requests.get(f"{API_BASE}/preload/top", params={"limit": 20}, timeout=60)
    data = response.json()
    api_time = time.time() - start

    print(f"API返回时间: {api_time:.2f}秒")
    print(f"返回图片数: {len(data['destinations'])}")

    # 模拟预加载图片（只测试HEAD请求，不下载完整图片）
    print("\n测试图片URL可访问性...")
    urls = [d['url'] for d in data['destinations'][:5]]  # 只测试前5个

    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(requests.head, url, timeout=10)
            for url in urls
        ]
        results = concurrent.futures.as_completed(futures)

    elapsed = time.time() - start

    success = sum(1 for r in results if r.result().status_code == 200)
    print(f"前5个图片HEAD请求: {success}/5 成功, {elapsed:.2f}秒")


def main():
    print("\n" + "="*60)
    print("热门城市图片预加载API测试")
    print("="*60)
    print(f"API地址: {API_BASE}")

    try:
        # 测试1: TOP热门城市API
        top_data = test_top_destinations_api()

        # 测试2: 按地区获取
        test_popular_destinations_api()

        # 测试3: 城市列表
        test_destinations_list_api()

        # 测试4: 并行预加载性能
        if top_data:
            test_parallel_preload()

        print("\n" + "="*60)
        print("测试完成!")
        print("="*60)

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
