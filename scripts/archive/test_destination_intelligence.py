"""
测试目的地情报智能体

验证目的地情报分析功能是否正常工作
"""
import sys
import os
import io
import asyncio
from datetime import datetime, timedelta

# 设置UTF-8编码输出（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_intelligence_agent_import():
    """测试智能体导入"""
    print("\n[测试1] 测试智能体导入...")
    try:
        from tradingagents.agents.analysts.destination_intelligence import (
            DestinationIntelligenceAgent,
            get_destination_intelligence_agent,
            analyze_destination
        )
        print("  ✓ 智能体导入成功")
        return True
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        return False


def test_analyze_hangzhou():
    """测试分析杭州"""
    print("\n[测试2] 测试分析杭州情报...")
    try:
        from tradingagents.agents.analysts.destination_intelligence import analyze_destination

        async def run_test():
            report = await analyze_destination("杭州", "2026-04-15")

            print(f"  ✓ 目的地: {report['destination']}")
            print(f"  ✓ 分析时间: {report['generated_at']}")
            print(f"  ✓ 新闻数量: {len(report['news'])}")
            print(f"  ✓ 风险评估: {report['risk_assessment']['overall_risk_text']}")
            print(f"  ✓ 风险等级: {report['risk_assessment']['risk_level']}/5")
            print(f"  ✓ 活动数量: {len(report['events'])}")
            print(f"  ✓ 推荐数量: {len(report['recommendations'])}")
            print(f"  ✓ 活动示例: {report['events'][0]['name'] if report['events'] else '无'}")

            return True

        return asyncio.run(run_test())
    except Exception as e:
        print(f"  ✗ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_other_destinations():
    """测试其他目的地"""
    print("\n[测试3] 测试其他目的地...")
    try:
        from tradingagents.agents.analysts.destination_intelligence import analyze_destination

        async def run_test():
            destinations = ["北京", "成都", "三亚", "西安"]
            results = []

            for dest in destinations:
                report = await analyze_destination(dest)
                risk_text = report['risk_assessment']['overall_risk_text']
                event_count = len(report['events'])
                print(f"  ✓ {dest}: {risk_text}, {event_count}个活动")
                results.append(dest)

            print(f"  ✓ 共测试了 {len(results)} 个目的地")
            return True

        return asyncio.run(run_test())
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False


def test_markdown_report():
    """测试Markdown报告生成"""
    print("\n[测试4] 测试Markdown报告生成...")
    try:
        from tradingagents.agents.analysts.destination_intelligence import get_destination_intelligence_agent

        agent = get_destination_intelligence_agent()

        # 创建模拟报告（完整数据）
        mock_report = {
            "destination": "杭州",
            "travel_date": "2026-04-15",
            "generated_at": datetime.now().isoformat(),
            "news": [
                {
                    "title": "杭州推出新一轮旅游优惠政策",
                    "source": "杭州日报",
                    "published_at": "2026-03-10T10:00:00",
                    "summary": "杭州推出新一轮旅游优惠政策，部分景点门票减免，吸引更多游客前来观光",
                    "sentiment": "positive",
                    "category": "policy"
                },
                {
                    "title": "西湖春季赏花季正式开启",
                    "source": "浙江旅游网",
                    "published_at": "2026-03-08T14:30:00",
                    "summary": "西湖景区春季花卉进入最佳观赏期，樱花、桃花、郁金香竞相开放",
                    "sentiment": "positive",
                    "category": "tourism"
                },
                {
                    "title": "杭州地铁新线开通，直达多个热门景点",
                    "source": "杭州发布",
                    "published_at": "2026-03-05T09:00:00",
                    "summary": "杭州地铁新线路正式开通，游客可乘坐地铁直达西湖、灵隐寺等多个热门景点",
                    "sentiment": "positive",
                    "category": "transport"
                }
            ],
            "risk_assessment": {
                "overall_risk": "low",
                "overall_risk_text": "🟢 低风险 - 可以放心前往",
                "risk_level": 1,
                "recommendation": "目的地安全，可以放心前往",
                "risk_categories": {
                    "political": {"status": "安全", "description": "社会稳定，无政治风险"},
                    "safety": {"status": "安全", "description": "治安良好，犯罪率低"},
                    "health": {"status": "安全", "description": "无疫情或健康风险"},
                    "natural_disaster": {"status": "注意", "description": "春季雨水较多，注意携带雨具"},
                    "social": {"status": "正常", "description": "社会秩序良好"}
                },
                "risk_factors": []
            },
            "events": [
                {
                    "name": "杭州西湖龙井茶文化节",
                    "type": "festival",
                    "start_date": "2026-04-01",
                    "end_date": "2026-04-15",
                    "location": "杭州西湖龙井村",
                    "description": "春季龙井茶文化节，体验采茶、制茶、品茶的乐趣，感受茶文化魅力",
                    "recommendation": "推荐！茶文化爱好者不容错过",
                    "tickets": "现场购票或预约"
                },
                {
                    "name": "杭州春季花卉展",
                    "type": "cultural",
                    "start_date": "2026-03-20",
                    "end_date": "2026-04-20",
                    "location": "杭州植物园",
                    "description": "春季花卉展览，展示樱花、郁金香、牡丹等多种花卉",
                    "recommendation": "推荐！摄影爱好者必去",
                    "tickets": "需提前预约"
                }
            ],
            "cultural_experiences": {
                "museums": [
                    {"name": "浙江省博物馆", "description": "了解浙江历史文化", "duration": "2-3小时", "tips": "周一闭馆"},
                    {"name": "中国丝绸博物馆", "description": "丝绸文化体验", "duration": "1-2小时", "tips": "可预约讲解"},
                    {"name": "中国茶叶博物馆", "description": "茶文化专题博物馆", "duration": "1-2小时", "tips": "免费开放"}
                ],
                "performances": [
                    {"name": "印象西湖", "description": "大型室外实景演出，张艺谋导演"},
                    {"name": "宋城千古情", "description": "大型歌舞演出，展现杭州历史文化"}
                ],
                "food_experiences": [
                    {
                        "name": "杭帮菜",
                        "description": "杭州传统菜系，口味清淡",
                        "dishes": ["西湖醋鱼", "东坡肉", "龙井虾仁", "叫花鸡"],
                        "restaurants": ["楼外楼", "知味观", "外婆家", "新白鹿"]
                    },
                    {
                        "name": "茶文化体验",
                        "description": "龙井茶品鉴与茶艺学习",
                        "dishes": ["龙井茶", "茶点"],
                        "restaurants": ["龙井村茶室", "湖畔居茶楼"]
                    }
                ],
                "local_specialties": [
                    {"name": "西湖龙井", "description": "中国十大名茶之一"},
                    {"name": "西湖绸伞", "description": "杭州传统工艺品"},
                    {"name": "王星记扇子", "description": "中华老字号，杭扇代表"},
                    {"name": "张小泉剪刀", "description": "中华老字号"}
                ],
                "cultural_tips": [
                    "杭州人说话温柔，交流时请保持礼貌",
                    "在寺庙参观时请保持安静，不要随意拍照",
                    "品茶时主人会先敬茶，接茶时应双手接过",
                    "杭州气候湿润，春季雨水较多，记得携带雨具"
                ]
            },
            "recommendations": [
                "建议提前预订热门景点门票和酒店",
                "春季雨水较多，请携带雨具",
                "西湖景区建议公共交通，避免拥堵",
                "龙井村可以体验采茶制茶，适合亲子游",
                "尝试杭帮菜，品尝正宗西湖醋鱼",
                "晚上可以看印象西湖演出"
            ]
        }

        markdown = agent.format_intelligence_report(mock_report)

        if len(markdown) > 1000:
            print(f"  ✓ Markdown报告生成成功 ({len(markdown)} 字符)")
            print(f"  ✓ 包含标题: {'杭州' in markdown}")
            print(f"  ✓ 包含风险评估: {'风险评估' in markdown}")
            return True
        else:
            print(f"  ✗ Markdown报告过短: {len(markdown)} 字符")
            return False

    except Exception as e:
        print(f"  ✗ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoints():
    """测试API端点"""
    print("\n[测试5] 测试API端点...")
    try:
        from app.routers.travel_intelligence import router

        endpoints = []
        for route in router.routes:
            if hasattr(route, 'path'):
                methods = list(route.methods) if hasattr(route, 'methods') else []
                endpoints.append(f"{methods} {route.path if hasattr(route, 'path') else ''}")

        print(f"  ✓ 注册了 {len(endpoints)} 个端点:")
        for endpoint in endpoints:
            print(f"     - {endpoint}")
        return True
    except Exception as e:
        print(f"  ✗ 检查失败: {e}")
        return False


def test_seasonal_risks():
    """测试季节性风险评估"""
    print("\n[测试6] 测试季节性风险...")
    try:
        from tradingagents.agents.analysts.destination_intelligence import get_destination_intelligence_agent

        agent = get_destination_intelligence_agent()

        # 测试夏季风险（台风季节）
        async def run_test():
            # 模拟夏季
            test_results = []
            destinations = ["杭州", "三亚"]
            for dest in destinations:
                # 夏季风险测试 - 7月是台风季节
                risks = await agent._assess_risks(dest, "2026-07-15")
                summer_risk = risks["risk_level"]
                print(f"  ✓ {dest} 夏季风险等级: {summer_risk}/5")

                test_results.append((dest, summer_risk))

            return True

        return asyncio.run(run_test())
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_culture_recommendations():
    """测试文化推荐"""
    print("\n[测试7] 测试文化推荐...")
    try:
        from tradingagents.agents.analysts.destination_intelligence import get_destination_intelligence_agent

        agent = get_destination_intelligence_agent()

        # 测试几个主要旅游城市的文化推荐
        test_destinations = ["杭州", "北京", "成都"]

        async def run_test():
            for dest in test_destinations:
                culture = await agent._recommend_culture(dest)

                museums = culture.get("museums", [])
                performances = culture.get("performances", [])
                food = culture.get("food_experiences", [])

                print(f"\n  📍 {dest}:")
                print(f"     - 博物馆: {len(museums)}个")
                print(f"     - 表演: {len(performances)}个")
                print(f"     - 美食: {len(food)}个")

                if museums:
                    print(f"     示例: {museums[0]['name']}")

            return True

        return asyncio.run(run_test())
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("  目的地情报智能体测试")
    print("=" * 70)

    tests = [
        ("智能体导入", test_intelligence_agent_import),
        ("杭州情报分析", test_analyze_hangzhou),
        ("其他目的地", test_other_destinations),
        ("Markdown报告", test_markdown_report),
        ("API端点", test_api_endpoints),
        ("季节性风险", test_seasonal_risks),
        ("文化推荐", test_culture_recommendations)
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
        print("\n🎉 所有测试通过！目的地情报智能体已就绪。")
        print("\n使用示例：")
        print("  analyze_destination('杭州', '2026-04-15')")
    else:
        print(f"\n⚠ {total - passed} 个测试失败，请检查。")


if __name__ == "__main__":
    main()
