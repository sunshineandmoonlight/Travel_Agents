"""
快速测试脚本 - 验证修复效果
"""
import requests
import json

API_BASE = "http://localhost:8005"

def test_image_api():
    """测试图片API修复"""
    print("\n" + "="*50)
    print("测试1: 图片API修复")
    print("="*50)

    cities = ["北京", "上海", "成都", "西安"]
    for city in cities:
        url = f"{API_BASE}/api/travel/images/destination/{city}"
        try:
            response = requests.get(url, params={"width": 800, "height": 600}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"  [OK] {city}: {data.get('source', 'N/A')} - {data.get('url', '')[:50]}...")
            else:
                print(f"  [FAIL] {city}: HTTP {response.status_code}")
        except Exception as e:
            print(f"  [ERROR] {city}: {e}")

def test_destination_scores():
    """测试目的地评分修复"""
    print("\n" + "="*50)
    print("测试2: 目的地评分区分度")
    print("="*50)

    requirements = {
        "travel_scope": "domestic",
        "days": 5,
        "adults": 2,
        "children": 0,
        "budget": "medium",
        "interests": ["历史文化", "美食"],
        "start_date": "2024-05-01"
    }

    url = f"{API_BASE}/api/travel/staged/get-destinations"
    try:
        response = requests.post(url, json=requirements, timeout=30)
        if response.status_code == 200:
            data = response.json()
            destinations = data.get("destinations", [])

            print(f"\n  返回 {len(destinations)} 个目的地:")
            scores = []
            for dest in destinations:
                score = dest.get("match_score", 0)
                name = dest.get("destination", "N/A")
                scores.append(score)
                print(f"    - {name}: {score}分")

            # 检查区分度
            if len(scores) > 1:
                score_range = max(scores) - min(scores)
                avg_score = sum(scores) / len(scores)

                print(f"\n  评分分析:")
                print(f"    - 分数范围: {min(scores)} - {max(scores)} (差距: {score_range}分)")
                print(f"    - 平均分: {avg_score:.1f}")

                if score_range > 5:
                    print(f"    - [OK] 分数有区分度 (差距 > 5分)")
                else:
                    print(f"    - [WARN] 分数区分度较小")

                if min(scores) > 50:
                    print(f"    - [OK] 最低分 > 50分 (已修复)")
                else:
                    print(f"    - [WARN] 仍然存在50分")
        else:
            print(f"  [FAIL] HTTP {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] {e}")

def test_llm_status():
    """检查LLM配置状态"""
    print("\n" + "="*50)
    print("测试3: LLM配置状态")
    print("="*50)

    # 检查.env文件
    import os
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()

        llm_providers = {
            "LLM_PROVIDER": None,
            "SILICONFLOW_API_KEY": None,
            "DEEPSEEK_API_KEY": None,
            "DASHSCOPE_API_KEY": None,
            "OPENAI_API_KEY": None,
            "GOOGLE_API_KEY": None
        }

        for key in llm_providers:
            for line in content.split('\n'):
                if line.startswith(key + '='):
                    value = line.split('=', 1)[1].strip()
                    llm_providers[key] = value

        provider = llm_providers["LLM_PROVIDER"]
        print(f"\n  当前LLM提供商: {provider or '未配置'}")

        if provider:
            key_name = f"{provider.upper()}_API_KEY"
            key_value = llm_providers.get(key_name, "")

            if key_value and "your_" not in key_value and "_here" not in key_value:
                print(f"  [OK] {key_name}: 已配置 (len={len(key_value)})")
                print(f"  [INFO] LLM评分已启用，将获得更精准的匹配度")
            else:
                print(f"  [WARN] {key_name}: 未配置或使用占位符")
                print(f"  [INFO] 当前使用规则引擎评分（已改进）")
        else:
            print(f"  [WARN] LLM未配置，使用规则引擎")
            print(f"  [INFO] 参考 .env.example.llm 配置LLM")
    else:
        print("  [WARN] .env文件不存在")

def main():
    print("\n" + "="*60)
    print("  TravelAgents-CN 修复验证测试")
    print("="*60)
    print(f"  后端地址: {API_BASE}")
    print(f"  测试时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 测试1: 图片API
    test_image_api()

    # 测试2: 目的地评分
    test_destination_scores()

    # 测试3: LLM状态
    test_llm_status()

    print("\n" + "="*60)
    print("  测试完成")
    print("="*60)
    print("\n建议:")
    print("  1. 刷新前端页面验证图片加载")
    print("  2. 重新规划旅行查看评分区分度")
    print("  3. (可选) 配置LLM获得更精准评分")
    print()

if __name__ == "__main__":
    main()
