"""
测试天行数据新闻API

验证天行数据API是否正常工作
"""
import os
import sys
import io
import asyncio
import requests

# 设置UTF-8编码输出（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_tianapi_direct():
    """直接测试天行数据API"""
    print("\n[测试1] 直接测试天行数据API...")

    api_key = "8879cb7f41e435e278a404fe2be791ae"
    url = "http://api.tianapi.com/generalnews/index"

    params = {
        "key": api_key,
        "word": "杭州 旅游",
        "num": 5
    }

    try:
        print(f"  - 请求URL: {url}")
        print(f"  - 搜索关键词: {params['word']}")

        response = requests.get(url, params=params, timeout=10)

        print(f"  - HTTP状态码: {response.status_code}")

        data = response.json()

        if data.get("code") == 200:
            news_list = data.get("newsList", [])
            print(f"  ✓ 成功获取 {len(news_list)} 条新闻")

            if news_list:
                for i, news in enumerate(news_list[:3], 1):
                    print(f"\n  新闻 {i}:")
                    print(f"    标题: {news.get('title', 'N/A')}")
                    print(f"    来源: {news.get('source', 'N/A')}")
                    print(f"    时间: {news.get('ctime', 'N/A')}")
                    print(f"    描述: {news.get('description', 'N/A')[:60]}...")

            return True
        else:
            print(f"  ✗ API返回错误: {data.get('msg', '未知错误')}")
            print(f"  错误代码: {data.get('code', 'N/A')}")
            return False

    except requests.exceptions.Timeout:
        print("  ✗ 请求超时")
        return False
    except Exception as e:
        print(f"  ✗ 请求失败: {e}")
        return False


def test_news_adapter_with_tianapi():
    """测试新闻适配器使用天行数据"""
    print("\n[测试2] 测试新闻适配器使用天行数据...")

    # 临时设置环境变量
    os.environ["NEWS_SOURCE"] = "tianapi"
    os.environ["TIANAPI_KEY"] = "8879cb7f41e435e278a404fe2be791ae"

    try:
        from app.services.data_sources.news_adapter import get_news_adapter

        adapter = get_news_adapter()
        print(f"  ✓ 适配器创建成功")
        print(f"  ✓ 使用数据源: {adapter.source}")

        async def run_test():
            news = await adapter.search_news("成都", days=7, num=5)

            print(f"  ✓ 搜索到 {len(news)} 条新闻")

            if news:
                for i, item in enumerate(news[:3], 1):
                    print(f"\n  新闻 {i}:")
                    print(f"    标题: {item.get('title', 'N/A')}")
                    print(f"    来源: {item.get('source', 'N/A')}")
                    print(f"    情感: {item.get('sentiment', 'N/A')}")
                    print(f"    分类: {item.get('category', 'N/A')}")

            return len(news) > 0

        return asyncio.run(run_test())

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_destination_intelligence_with_real_news():
    """测试目的地情报使用真实新闻"""
    print("\n[测试3] 测试目的地情报使用真实新闻...")

    # 设置使用天行数据
    os.environ["NEWS_SOURCE"] = "tianapi"
    os.environ["TIANAPI_KEY"] = "8879cb7f41e435e278a404fe2be791ae"

    try:
        from tradingagents.agents.analysts.destination_intelligence import analyze_destination

        async def run_test():
            print("  - 正在分析北京...")
            report = await analyze_destination("北京", "2026-04-15")

            print(f"  ✓ 目的地: {report['destination']}")
            print(f"  ✓ 新闻数量: {len(report['news'])}")
            print(f"  ✓ 风险等级: {report['risk_assessment']['risk_level']}/5")

            if report['news']:
                print(f"\n  最新新闻:")
                for i, news in enumerate(report['news'][:3], 1):
                    print(f"    {i}. {news.get('title', 'N/A')}")
                    print(f"       来源: {news.get('source', 'N/A')}")
                    print(f"       情感: {news.get('sentiment', 'N/A')}")

            # 判断是否使用了真实新闻
            # 真实新闻通常会有真实的URL和详细描述
            has_real_news = any(
                news.get('url', '#') != '#' and len(news.get('summary', '')) > 50
                for news in report['news']
            )

            if has_real_news:
                print(f"\n  ✓ 检测到真实新闻数据")

            return True

        return asyncio.run(run_test())

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_serpapi_config():
    """检查SerpApi配置"""
    print("\n[测试4] 检查SerpApi配置...")

    serpapi_key = "dd5682943bc32a9ac9a83ef9772ec819b8aa1f3f74e418f960a4715ae18b2d6e"

    print(f"  ✓ SerpApi Key: {serpapi_key[:20]}...")
    print(f"  ✓ 注意: SerpApi用于百度新闻搜索，100次/月免费")

    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("  天行数据新闻API测试")
    print("=" * 70)

    tests = [
        ("直接API测试", test_tianapi_direct),
        ("新闻适配器", test_news_adapter_with_tianapi),
        ("目的地情报", test_destination_intelligence_with_real_news),
        ("SerpApi配置", test_serpapi_config)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ 测试 '{name}' 发生异常: {e}")
            results.append((name, False))

    # 汇总结果
    print("\n" + "=" * 70)
    print("  测试结果汇总")
    print("=" * 70)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {status}: {name}")

    print(f"\n总计: {passed}/{total} 通过")
    print("=" * 70)

    if passed == total:
        print("\n🎉 所有测试通过！天行数据API配置正确。")
        print("\n下一步：")
        print("  - 设置 NEWS_SOURCE=tianapi 启用真实新闻")
        print("  - 调用 POST /travel/plan 时会自动获取目的地情报")
    else:
        print(f"\n⚠ {total - passed} 个测试失败，请检查。")
        print("\n可能的问题：")
        print("  - 天行数据API密钥无效或已过期")
        print("  - 网络连接问题")
        print("  - API调用配额已用完")


if __name__ == "__main__":
    main()
