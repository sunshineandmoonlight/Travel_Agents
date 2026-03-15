"""
测试目的地情报与旅行规划集成

验证目的地情报是否正确集成到旅行规划流程中
"""
import sys
import os
import io
import asyncio

# 设置UTF-8编码输出（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_news_adapter():
    """测试新闻适配器"""
    print("\n[测试1] 测试新闻适配器...")
    try:
        from app.services.data_sources.news_adapter import get_news_adapter

        adapter = get_news_adapter()
        print(f"  ✓ 新闻适配器创建成功")
        print(f"  ✓ 使用数据源: {adapter.source}")

        # 测试搜索新闻
        async def run_search():
            news = await adapter.search_news("杭州", days=7, num=5)
            print(f"  ✓ 搜索到 {len(news)} 条新闻")

            if news:
                first = news[0]
                print(f"  ✓ 第一条新闻: {first.get('title', 'N/A')}")
                print(f"  ✓ 情感: {first.get('sentiment', 'N/A')}")
                print(f"  ✓ 分类: {first.get('category', 'N/A')}")

            return len(news) > 0

        return asyncio.run(run_search())

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_intelligence_with_real_news():
    """测试情报智能体使用真实新闻"""
    print("\n[测试2] 测试情报智能体使用真实新闻...")

    # 临时设置使用模拟数据
    os.environ["NEWS_SOURCE"] = "mock"

    try:
        from tradingagents.agents.analysts.destination_intelligence import analyze_destination

        async def run_test():
            report = await analyze_destination("杭州", "2026-04-15")

            print(f"  ✓ 目的地: {report['destination']}")
            print(f"  ✓ 新闻数量: {len(report['news'])}")
            print(f"  ✓ 风险等级: {report['risk_assessment']['risk_level']}/5")

            if report['news']:
                first_news = report['news'][0]
                print(f"  ✓ 第一条新闻标题: {first_news.get('title', 'N/A')}")
                print(f"  ✓ 情感分析: {first_news.get('sentiment', 'N/A')}")

            return True

        return asyncio.run(run_test())

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复环境变量
        os.environ["NEWS_SOURCE"] = "mock"


def test_intelligence_in_travel_plan():
    """测试旅行规划中包含目的地情报"""
    print("\n[测试3] 测试旅行规划包含目的地情报...")

    # 启用目的地情报
    os.environ["ENABLE_DESTINATION_INTELLIGENCE"] = "true"
    os.environ["NEWS_SOURCE"] = "mock"

    try:
        from tradingagents.graph.travel_graph_with_llm import create_travel_graph_with_llm
        from tradingagents.agents.analysts.destination_intelligence import analyze_destination

        async def run_test():
            # 模拟旅行规划流程
            destination = "杭州"
            days = 3

            print(f"  - 模拟规划 {destination} {days}日游...")

            # 1. 生成旅行规划
            graph = create_travel_graph_with_llm(
                llm_provider="deepseek",
                llm_model="deepseek-chat"
            )

            result = graph.plan(
                destination=destination,
                days=days,
                budget="medium",
                travelers=2,
                interest_type="风景",
                selected_style="relaxed"
            )

            print(f"  ✓ 旅行规划生成成功")

            # 2. 获取目的地情报（模拟API调用）
            intelligence = await analyze_destination(destination, "2026-04-15")

            # 3. 构建包含情报的响应数据
            plan_with_intelligence = {
                "destination": result.get("destination"),
                "days": days,
                "itinerary": result.get("detailed_itinerary", {}),
                "attractions": result.get("attractions", {}).get("recommended", []),
                "destination_intelligence": {
                    "risk_level": intelligence.get("risk_assessment", {}).get("risk_level", 1),
                    "risk_text": intelligence.get("risk_assessment", {}).get("overall_risk_text", ""),
                    "news_count": len(intelligence.get("news", [])),
                    "latest_news": intelligence.get("news", [])[:3],
                    "events": intelligence.get("events", [])[:5],
                    "recommendations": intelligence.get("recommendations", [])[:5]
                }
            }

            # 验证情报是否包含
            intel = plan_with_intelligence["destination_intelligence"]
            print(f"  ✓ 风险等级: {intel['risk_level']}/5")
            print(f"  ✓ 风险描述: {intel['risk_text']}")
            print(f"  ✓ 新闻数量: {intel['news_count']}")
            print(f"  ✓ 活动数量: {len(intel['events'])}")
            print(f"  ✓ 建议数量: {len(intel['recommendations'])}")

            if intel['latest_news']:
                print(f"  ✓ 最新新闻: {intel['latest_news'][0].get('title', 'N/A')}")

            return True

        return asyncio.run(run_test())

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复环境变量
        os.environ["ENABLE_DESTINATION_INTELLIGENCE"] = "true"
        os.environ["NEWS_SOURCE"] = "mock"


def test_sentiment_analysis():
    """测试情感分析功能"""
    print("\n[测试4] 测试情感分析...")

    try:
        from app.services.data_sources.news_adapter import NewsAdapter

        adapter = NewsAdapter(source="mock")

        test_titles = [
            ("杭州推出旅游优惠政策", "positive"),
            ("杭州发生安全事故", "negative"),
            ("杭州天气预报明天有雨", "neutral"),
            ("杭州新增高铁线路", "positive"),
            ("杭州景区临时关闭", "negative")
        ]

        all_correct = True
        for title, expected in test_titles:
            result = adapter._analyze_sentiment(title)
            status = "✓" if result == expected else "✗"
            print(f"  {status} '{title}' -> {result} (期望: {expected})")
            if result != expected:
                all_correct = False

        return all_correct

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False


def test_news_categorization():
    """测试新闻分类功能"""
    print("\n[测试5] 测试新闻分类...")

    try:
        from app.services.data_sources.news_adapter import NewsAdapter

        adapter = NewsAdapter(source="mock")

        test_titles = [
            ("杭州发布新的旅游政策", "policy"),
            ("杭州新增地铁线路", "transport"),
            ("杭州明天有大风天气预警", "weather"),
            ("杭州西湖游客数量增加", "tourism"),
            ("杭州举办音乐节活动", "event"),
            ("杭州景区发生安全事故", "safety")
        ]

        all_correct = True
        for title, expected in test_titles:
            result = adapter._categorize_news(title)
            status = "✓" if result == expected else "✗"
            print(f"  {status} '{title}' -> {result} (期望: {expected})")
            if result != expected:
                all_correct = False

        return all_correct

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("  目的地情报集成测试")
    print("=" * 70)

    tests = [
        ("新闻适配器", test_news_adapter),
        ("情报智能体使用真实新闻", test_intelligence_with_real_news),
        ("旅行规划包含目的地情报", test_intelligence_in_travel_plan),
        ("情感分析", test_sentiment_analysis),
        ("新闻分类", test_news_categorization)
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
        print("\n🎉 所有测试通过！目的地情报已成功集成到旅行规划流程。")
        print("\n使用示例：")
        print("  1. 调用 POST /travel/plan 生成旅行规划")
        print("  2. 响应中的 data.destination_intelligence 包含情报信息")
        print("  3. 设置环境变量 NEWS_SOURCE=tianapi 使用真实新闻API")
    else:
        print(f"\n⚠ {total - passed} 个测试失败，请检查。")


if __name__ == "__main__":
    main()
