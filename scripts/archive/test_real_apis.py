"""
测试目的地情报真实API

验证以下API是否正常工作：
- 天行数据: 文旅新闻
- 高德天气: 天气预报
- ExchangeRate-API: 汇率转换
- SerpAPI: 景点搜索
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.services.destination_intelligence_service import get_intelligence_service


async def test_all_apis():
    """测试所有API"""

    service = get_intelligence_service()

    print("=" * 60)
    print("目的地情报真实API测试")
    print("=" * 60)

    # 测试目的地
    destination = "杭州"

    # 1. 测试新闻API
    print("\n[1/4] Testing News API...")
    print("-" * 40)
    news = await service._get_news(destination)
    if news:
        print(f"[OK] Got {len(news)} news")
        for i, item in enumerate(news[:2]):
            print(f"  {i+1}. {item['title'][:40]}...")
            print(f"     Source: {item['source']} | Sentiment: {item['sentiment']}")
    else:
        print("[FAIL] No news retrieved")

    # 2. 测试天气API
    print("\n[2/4] Testing Weather API...")
    print("-" * 40)
    weather = await service._get_weather(destination)
    if weather and weather.get("current"):
        current = weather["current"]
        print(f"[OK] Current: {current['weather']}")
        print(f"  Temp: {current['temperature']}")
        print(f"  Wind: {current['wind']}")
        if weather.get("forecast"):
            print(f"  Tomorrow: {weather['forecast'][0]['day_temp']} {weather['forecast'][0]['weather']}")
    else:
        print("[FAIL] No weather data")

    # 3. 测试汇率API
    print("\n[3/4] Testing Exchange Rate API...")
    print("-" * 40)
    # 杭州用人民币，测试日元
    exchange = await service._get_exchange_rate("日本")
    if exchange.get("available"):
        print(f"[OK] Rate: 1 CNY = {exchange['rate']:.2f} {exchange['to']}")
        print(f"  Inverse: 1 {exchange['to']} = {exchange['inverse']:.4f} CNY")
    else:
        print(f"[FAIL] Exchange: {exchange.get('reason', 'Unknown error')}")

    # 4. 测试景点API
    print("\n[4/4] Testing Attractions API...")
    print("-" * 40)
    attractions = await service._get_attractions(destination)
    if attractions:
        print(f"[OK] Got {len(attractions)} attractions")
        for i, attr in enumerate(attractions[:3]):
            print(f"  {i+1}. {attr['name']}")
            print(f"     Rating: {attr['rating']} | Reviews: {attr['reviews']}")
    else:
        print("[FAIL] No attractions data")

    # 5. 测试完整情报
    print("\n[5/5] Testing Full Intelligence...")
    print("-" * 40)
    try:
        intelligence = await service.get_intelligence(destination)
        print(f"[OK] Intelligence generated")
        print(f"  News: {len(intelligence.get('news', []))} items")
        print(f"  Recommendations: {len(intelligence.get('recommendations', []))} items")
        print(f"  Risk Level: {intelligence.get('risk_assessment', {}).get('risk_level', 'N/A')}")
    except Exception as e:
        print(f"[FAIL] Intelligence failed: {e}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


async def test_specific_api():
    """测试特定API"""
    import sys

    if len(sys.argv) > 1:
        api_type = sys.argv[1]
        destination = sys.argv[2] if len(sys.argv) > 2 else "杭州"
    else:
        api_type = "all"
        destination = "杭州"

    service = get_intelligence_service()

    if api_type == "news":
        print(f"测试 {destination} 新闻API...")
        news = await service._get_news(destination)
        print(f"获取到 {len(news)} 条新闻")

    elif api_type == "weather":
        print(f"测试 {destination} 天气API...")
        weather = await service._get_weather(destination)
        print(f"天气: {weather}")

    elif api_type == "exchange":
        print("测试汇率API...")
        exchange = await service._get_exchange_rate("日本")
        print(f"汇率: {exchange}")

    elif api_type == "attractions":
        print(f"测试 {destination} 景点API...")
        attractions = await service._get_attractions(destination)
        print(f"景点: {attractions}")

    else:
        await test_all_apis()


if __name__ == "__main__":
    asyncio.run(test_specific_api())
