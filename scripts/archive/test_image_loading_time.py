"""
测试图片API加载时间
模拟前端加载4个攻略封面图片的场景
"""

import asyncio
import time
import requests
from typing import List, Dict
import concurrent.futures

# API配置
API_BASE = "http://localhost:8005/api/travel/images"

# 测试城市列表（模拟4个攻略）
TEST_CITIES = ["三亚", "曼谷", "东京", "巴黎"]


def fetch_image(city: str, index: int) -> Dict:
    """获取单个城市图片并计时"""
    start_time = time.time()

    try:
        response = requests.get(
            f"{API_BASE}/destination/{city}",
            params={"width": 600, "height": 400},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        elapsed = time.time() - start_time

        return {
            "index": index,
            "city": city,
            "success": True,
            "url": data.get("url", ""),
            "source": data.get("source", "unknown"),
            "time": elapsed,
            "error": None
        }

    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "index": index,
            "city": city,
            "success": False,
            "url": "",
            "source": "error",
            "time": elapsed,
            "error": str(e)
        }


def test_sequential_loading():
    """测试顺序加载（一个接一个）"""
    print("\n" + "="*60)
    print("测试1: 顺序加载（模拟串行请求）")
    print("="*60)

    results = []
    total_start = time.time()

    for i, city in enumerate(TEST_CITIES, 1):
        print(f"\n[{i}/4] 正在加载 {city} 的图片...")
        result = fetch_image(city, i)
        results.append(result)

        if result["success"]:
            print(f"  [OK] 成功! 来源: {result['source']}, 耗时: {result['time']:.2f}秒")
            print(f"    URL: {result['url'][:80]}...")
        else:
            print(f"  [FAIL] 失败! 耗时: {result['time']:.2f}秒, 错误: {result['error']}")

    total_time = time.time() - total_start

    print("\n" + "-"*60)
    print(f"顺序加载总时间: {total_time:.2f}秒")
    print(f"平均每个图片: {total_time/len(TEST_CITIES):.2f}秒")

    return results, total_time


def test_parallel_loading():
    """测试并行加载（同时发起所有请求）"""
    print("\n" + "="*60)
    print("测试2: 并行加载（模拟浏览器同时加载）")
    print("="*60)

    total_start = time.time()

    # 使用线程池并行请求
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_city = {
            executor.submit(fetch_image, city, i): (city, i)
            for i, city in enumerate(TEST_CITIES, 1)
        }

        results = []
        for future in concurrent.futures.as_completed(future_to_city):
            result = future.result()
            results.append(result)

    total_time = time.time() - total_start

    # 打印结果
    for result in sorted(results, key=lambda x: x["time"]):
        if result["success"]:
            print(f"[{result['index']}/4] {result['city']}: {result['time']:.2f}秒 [OK] ({result['source']})")
        else:
            print(f"[{result['index']}/4] {result['city']}: {result['time']:.2f}秒 [FAIL] ({result['error']})")

    print("\n" + "-"*60)
    print(f"并行加载总时间: {total_time:.2f}秒")
    print(f"最快的图片: {min(r['time'] for r in results):.2f}秒")
    print(f"最慢的图片: {max(r['time'] for r in results):.2f}秒")

    return results, total_time


def test_with_cache():
    """测试带缓存的加载"""
    print("\n" + "="*60)
    print("测试3: 缓存效果（第二次加载相同城市）")
    print("="*60)

    # 第一次加载（无缓存）
    print("\n第一次加载（无缓存）:")
    total_start = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        first_results = list(executor.map(fetch_image, TEST_CITIES, [1,2,3,4]))

    first_time = time.time() - total_start

    # 等待一下
    time.sleep(0.5)

    # 第二次加载（可能有缓存）
    print("\n第二次加载（可能命中缓存）:")
    total_start = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        second_results = list(executor.map(fetch_image, TEST_CITIES, [1,2,3,4]))

    second_time = time.time() - total_start

    print("\n" + "-"*60)
    print(f"第一次加载（无缓存）: {first_time:.2f}秒")
    print(f"第二次加载（有缓存）: {second_time:.2f}秒")
    print(f"缓存加速: {first_time - second_time:.2f}秒 ({(1-second_time/first_time)*100:.1f}%)")

    return first_results, second_results, first_time, second_time


def print_summary(results: List[Dict]):
    """打印结果统计"""
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    print("\n" + "="*60)
    print("结果统计")
    print("="*60)
    print(f"成功: {len(successful)}/{len(results)}")
    print(f"失败: {len(failed)}/{len(results)}")

    if successful:
        sources = {}
        for r in successful:
            source = r["source"]
            sources[source] = sources.get(source, 0) + 1
        print(f"\n图片来源分布:")
        for source, count in sources.items():
            print(f"  - {source}: {count}个")


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("图片API加载时间测试")
    print("="*60)
    print(f"测试城市: {', '.join(TEST_CITIES)}")
    print(f"API地址: {API_BASE}")

    try:
        # 测试1: 顺序加载
        seq_results, seq_time = test_sequential_loading()
        print_summary(seq_results)

        # 等待一下
        time.sleep(1)

        # 测试2: 并行加载
        par_results, par_time = test_parallel_loading()
        print_summary(par_results)

        # 等待一下
        time.sleep(1)

        # 测试3: 缓存效果
        test_with_cache()

        print("\n" + "="*60)
        print("结论")
        print("="*60)
        print(f"顺序加载4张图片: 约 {seq_time:.1f}秒")
        print(f"并行加载4张图片: 约 {par_time:.1f}秒")
        print(f"并行加速比: {seq_time/par_time:.2f}x")
        print("\n注意: 实际浏览器加载时间还需要加上图片下载时间")
        print("      (API只返回URL，浏览器需要额外时间下载图片)")

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
