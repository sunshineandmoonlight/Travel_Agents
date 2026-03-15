"""
测试A组、B组、C组API性能
"""

import requests
import time
import json

def test_group_a():
    """测试A组：获取目的地推荐"""
    print("[A组] 获取目的地推荐...")

    request = {
        "travel_scope": "domestic",
        "start_date": "2025-05-01",
        "days": 3,
        "adults": 2,
        "children": 0,
        "budget": "medium",
        "interests": ["文化", "美食", "历史"],
        "special_requests": "希望行程不要太紧凑"
    }

    start = time.time()
    response = requests.post(
        'http://localhost:8005/api/travel/staged/get-destinations-stream',
        json=request,
        stream=True,
        timeout=300
    )

    llm_count = 0
    destination = "北京"

    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if 'progress' in line or 'step_result' in line:
                llm_count += 1
            if 'complete' in line:
                data = json.loads(line[6:])
                destinations = data.get('destinations', [])
                if destinations:
                    destination = destinations[0]['destination']
                break

    duration = time.time() - start

    print(f"完成: {duration:.2f}秒")
    print(f"推荐目的地: {destination}")

    return duration, llm_count, destination


def test_group_b(destination):
    """测试B组：获取风格方案"""
    print(f"\n[B组] 获取风格方案 (目的地: {destination})...")

    request = {
        "travel_scope": "domestic",
        "days": 3,
        "user_portrait": {
            "description": "文化旅游爱好者",
            "primary_interests": ["文化", "美食", "历史"],
            "budget": "medium"
        }
    }

    start = time.time()
    response = requests.post(
        f'http://localhost:8005/api/travel/staged/get-styles-stream?destination={destination}',
        json=request,
        stream=True,
        timeout=300
    )

    llm_count = 0
    style = "深度文化游"

    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if 'progress' in line or 'step_result' in line:
                llm_count += 1
            if 'complete' in line:
                data = json.loads(line[6:])
                styles = data.get('styles', [])
                if styles:
                    style = styles[0].get('style_name', '深度文化游')
                break

    duration = time.time() - start

    print(f"完成: {duration:.2f}秒")
    print(f"风格方案数: 4个")

    return duration, llm_count


def test_group_c(destination, style):
    """测试C组：生成详细攻略"""
    print(f"\n[C组] 生成详细攻略...")

    request = {
        "travel_scope": "domestic",
        "start_date": "2025-05-01",
        "days": 3,
        "user_portrait": {
            "description": "文化旅游爱好者",
            "primary_interests": ["文化", "美食", "历史"],
            "budget": "medium"
        }
    }

    start = time.time()

    # 直接调用完整流程API
    response = requests.post(
        f'http://localhost:8005/api/travel/staged/generate-guide-stream?destination={destination}&style_name={style}',
        json=request,
        stream=True,
        timeout=600
    )

    llm_count = 0
    line_count = 0

    for line in response.iter_lines():
        if line:
            line_count += 1
            line = line.decode('utf-8')
            if 'progress' in line:
                llm_count += 1
            if line_count > 200:  # 只读取前200行
                break

    duration = time.time() - start

    print(f"完成: {duration:.2f}秒 (读取前200行)")

    return duration, llm_count


# 主测试
if __name__ == "__main__":
    print("="*70)
    print("旅行规划完整流程性能测试")
    print("="*70)

    try:
        # 测试A组
        duration_a, calls_a, dest = test_group_a()

        # 测试B组
        duration_b, calls_b = test_group_b(dest)

        # 测试C组（部分）
        duration_c, calls_c = test_group_c(dest, "深度文化游")

        # 汇总
        print("\n" + "="*70)
        print("性能测试汇总")
        print("="*70)
        print(f"A组 (目的地推荐): {duration_a:.2f}秒")
        print(f"B组 (风格方案): {duration_b:.2f}秒")
        print(f"C组 (详细攻略): {duration_c:.2f}秒 (部分)")
        print("-"*70)
        print(f"A+B: {duration_a + duration_b:.2f}秒")
        print(f"总计: {duration_a + duration_b + duration_c:.2f}秒")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
