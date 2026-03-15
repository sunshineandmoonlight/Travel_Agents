"""
测试RestCountries和ExchangeRate-API集成

验证免费国际旅游API功能
"""

import sys
import os
import io
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 修复Windows编码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from tradingagents.integrations.restcountries_client import RestCountriesClient, normalize_country_name
from tradingagents.integrations.exchange_rate_client import ExchangeRateClient, get_currency_for_country
from tradingagents.utils.unified_data_interface import InternationalDataProvider

print("=" * 70)
print(" 免费国际旅游API集成测试")
print("=" * 70)


def test_restcountries():
    """测试RestCountries API"""
    print("\n" + "=" * 70)
    print("1. RestCountries API - 国家信息查询")
    print("=" * 70)

    client = RestCountriesClient()

    test_countries = ["Japan", "Thailand", "France", "Australia"]

    for country in test_countries:
        print(f"\n🌍 查询: {country}")
        print("-" * 50)

        result = client.get_country_info_for_travel(country)

        if result.get("success"):
            print(f"  名称: {result.get('country_name')}")
            print(f"  首都: {result.get('capital')}")
            print(f"  地区: {result.get('region')} / {result.get('subregion')}")
            print(f"  人口: {result.get('population'):,}")
            print(f"  货币: {result.get('currency', {}).get('code')} - {result.get('currency', {}).get('name')}")
            print(f"  货币符号: {result.get('currency', {}).get('symbol')}")
            print(f"  语言: {', '.join(result.get('languages', [])[:3])}")
            print(f"  国际区号: +{result.get('calling_code')}")
            print(f"  时区: {result.get('timezones', [''])[0] if result.get('timezones') else 'N/A'}")
            print(f"  国旗: {result.get('flag', '')[:50]}...")

            travel = result.get('travel_info', {})
            print(f"  签证要求: {travel.get('visa_required')}")
            print(f"  安全等级: {travel.get('safety_level')}")
            print(f"  预算等级: {travel.get('budget_level')}")
        else:
            print(f"  ❌ 错误: {result.get('error')}")


def test_exchange_rate():
    """测试ExchangeRate API"""
    print("\n" + "=" * 70)
    print("2. ExchangeRate-API - 货币转换")
    print("=" * 70)

    client = ExchangeRateClient(api_key="86894aac3ce5084f3afc7068")

    # 测试货币转换
    print("\n💱 货币转换测试:")
    conversions = [
        (100, "USD", "CNY", "100美元转人民币"),
        (1000, "JPY", "CNY", "1000日元转人民币"),
        (100, "EUR", "CNY", "100欧元转人民币"),
        (100, "THB", "CNY", "100泰铢转人民币"),
    ]

    for amount, from_curr, to_curr, desc in conversions:
        result = client.convert_currency(amount, from_curr, to_curr)
        if result.get("success"):
            converted = result.get("converted_amount", 0)
            rate = result.get("rate", 0)
            print(f"  {desc}: {converted:.2f} {to_curr} (汇率: {rate})")
        else:
            print(f"  {desc}: ❌ {result.get('error')}")

    # 测试获取所有汇率
    print("\n📊 主要货币汇率 (基准: USD):")
    rates_result = client.get_latest_rates("USD")
    if rates_result.get("success"):
        rates = rates_result.get("rates", {})
        major_currencies = ["CNY", "JPY", "EUR", "GBP", "KRW", "THB", "SGD", "AUD"]
        for currency in major_currencies:
            if currency in rates:
                print(f"  1 USD = {rates[currency]:.4f} {currency}")


def test_international_provider():
    """测试InternationalDataProvider集成"""
    print("\n" + "=" * 70)
    print("3. InternationalDataProvider - 统一接口")
    print("=" * 70)

    provider = InternationalDataProvider()

    # 测试获取位置信息
    print("\n📍 获取位置信息测试:")
    locations = ["Tokyo", "Paris", "Bangkok", "Sydney"]

    for location in locations:
        result = provider.get_location_info(location)
        if result.get("confidence", 0) > 0.5:
            print(f"\n  {location}:")
            print(f"    国家: {result.get('name')}")
            print(f"    货币: {result.get('currency')} ({result.get('currency_name')})")
            print(f"    首都: {result.get('capital')}")
            print(f"    语言: {result.get('language')}")

            travel = result.get('travel_info', {})
            if travel:
                print(f"    签证: {travel.get('visa_required')}")

    # 测试货币转换
    print("\n💱 货币转换测试:")
    conversion = provider.convert_currency(100, "JPY", "CNY")
    if conversion.get("success"):
        print(f"  100 JPY = {conversion['converted_amount']:.2f} CNY")
        print(f"  汇率: {conversion['rate']:.6f}")

    # 测试获取国家详情
    print("\n🌍 获取国家详情测试:")
    details = provider.get_country_details("Thailand")
    if details.get("success"):
        print(f"  国家: {details.get('country_name')}")
        print(f"  首都: {details.get('capital')}")
        print(f"  签证: {details.get('travel_info', {}).get('visa_required')}")


def test_country_normalization():
    """测试国家名称规范化"""
    print("\n" + "=" * 70)
    print("4. 国家名称规范化测试")
    print("=" * 70)

    test_names = [
        "日本", "东京", "Japan",
        "泰国", "曼谷", "Thailand",
        "韩国", "南韩", "South Korea",
        "阿联酋", "迪拜", "UAE"
    ]

    print("\n🔄 名称规范化:")
    for name in test_names:
        normalized = normalize_country_name(name)
        if normalized != name:
            print(f"  {name} -> {normalized}")


def main():
    """主测试函数"""
    try:
        test_restcountries()
        test_exchange_rate()
        test_international_provider()
        test_country_normalization()

        print("\n" + "=" * 70)
        print("✅ 所有测试完成!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
