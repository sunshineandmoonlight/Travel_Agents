"""
测试天行数据多个新闻接口

验证综合新闻、文旅新闻、地区新闻三个接口
"""
import os
import sys
import io
import requests

# 设置UTF-8编码输出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 天行数据配置
API_KEY = "8879cb7f41e435e278a404fe2be791ae"

# 天行数据API端点
ENDPOINTS = {
    "综合新闻": "http://api.tianapi.com/generalnews/index",
    "文旅新闻": "http://api.tianapi.com/travelnews/index",
    "地区新闻": "http://api.tianapi.com/areanews/index",
}


def test_endpoint(endpoint_name, url, keyword, num=5, destination=None):
    """测试单个接口"""
    print(f"\n{'='*60}")
    print(f"测试: {endpoint_name}")
    print(f"{'='*60}")

    params = {
        "key": API_KEY,
        "num": num
    }

    # 根据接口类型设置不同的参数
    if endpoint_name == "地区新闻":
        # 地区新闻使用 areaname 参数
        if destination:
            params["areaname"] = destination
        params["word"] = keyword
        print(f"  参数: areaname={destination}, word={keyword}")
    else:
        # 其他接口使用 word 参数
        params["word"] = keyword
        print(f"  参数: word={keyword}")

    try:
        print(f"  URL: {url}")
        print(f"  请求数量: {num}")

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        print(f"  HTTP状态: {response.status_code}")
        print(f"  响应代码: {data.get('code', 'N/A')}")
        print(f"  响应消息: {data.get('msg', 'N/A')}")

        if data.get("code") == 200:
            news_list = data.get("newsList", [])
            print(f"  ✓ 成功获取 {len(news_list)} 条新闻")

            if news_list:
                print(f"\n  新闻示例:")
                for i, news in enumerate(news_list[:3], 1):
                    print(f"    [{i}] {news.get('title', 'N/A')}")
                    print(f"        来源: {news.get('source', 'N/A')}")
                    print(f"        时间: {news.get('ctime', 'N/A')}")
                    desc = news.get('description', 'N/A')
                    if desc != 'N/A':
                        print(f"        摘要: {desc[:50]}...")
                    print()

            return True, len(news_list)
        else:
            print(f"  ✗ 失败: {data.get('msg', '未知错误')}")

            # 特殊错误代码说明
            code = data.get('code')
            if code == 160:
                print(f"  💡 提示: 需要在天行数据后台申请该接口")
            elif code == 170:
                print(f"  💡 提示: API Key错误或已过期")
            elif code == 110:
                print(f"  💡 提示: 查询参数错误")

            return False, 0

    except requests.exceptions.Timeout:
        print(f"  ✗ 请求超时")
        return False, 0
    except Exception as e:
        print(f"  ✗ 请求失败: {e}")
        return False, 0


def main():
    """运行所有测试"""
    print("\n" + "="*70)
    print("  天行数据多接口测试")
    print("="*70)
    print(f"  API Key: {API_KEY[:20]}...")
    print("="*70)

    results = {}
    total_news = 0

    # 测试不同的关键词
    test_cases = [
        ("杭州", "杭州"),
        ("杭州 旅游", "杭州 旅游"),
    ]

    for keyword, display_keyword in test_cases:
        print(f"\n\n{'#'*70}")
        print(f"# 测试关键词: {display_keyword}")
        print(f"{'#'*70}")

        keyword_results = {}

        for endpoint_name, url in ENDPOINTS.items():
            # 提取目的地名称（去掉"旅游"等后缀）
            destination = keyword.replace("旅游", "").replace("资讯", "").strip()
            success, count = test_endpoint(endpoint_name, url, keyword, destination=destination)
            keyword_results[endpoint_name] = (success, count)
            total_news += count

        results[display_keyword] = keyword_results

    # 汇总结果
    print("\n\n" + "="*70)
    print("  测试结果汇总")
    print("="*70)

    for keyword, endpoint_results in results.items():
        print(f"\n关键词: {keyword}")
        for endpoint, (success, count) in endpoint_results.items():
            status = "✓ 可用" if success else "✗ 不可用"
            print(f"  {endpoint:12} {status:10} (获取 {count} 条)")

    print(f"\n总计获取: {total_news} 条新闻")

    # 统计可用接口
    available = set()
    for endpoint_results in results.values():
        for endpoint, (success, _) in endpoint_results.items():
            if success:
                available.add(endpoint)

    print(f"\n可用接口 ({len(available)}/{len(ENDPOINTS)}):")
    for endpoint in available:
        print(f"  ✓ {endpoint}")

    unavailable = set(ENDPOINTS.keys()) - available
    if unavailable:
        print(f"\n不可用接口 ({len(unavailable)}):")
        for endpoint in unavailable:
            print(f"  ✗ {endpoint} - 需要在天行数据后台申请")

    print("\n" + "="*70)
    print("  建议")
    print("="*70)
    print("""
1. 如果接口显示"未申请"，请登录天行数据后台申请对应接口:
   https://www.tianapi.com/

2. 推荐申请顺序:
   - 文旅新闻 (最相关旅行信息)
   - 地区新闻 (特定地区新闻)
   - 综合新闻 (综合新闻资讯)

3. 系统会自动按优先级使用可用接口，无需手动配置
    """)

    if len(available) == len(ENDPOINTS):
        print("\n🎉 所有接口都已申请并可用！")
    elif len(available) > 0:
        print(f"\n⚠ {len(unavailable)} 个接口未申请，但系统仍可使用已申请的接口")
    else:
        print("\n⚠ 所有接口都未申请，系统将使用模拟数据")


if __name__ == "__main__":
    main()
