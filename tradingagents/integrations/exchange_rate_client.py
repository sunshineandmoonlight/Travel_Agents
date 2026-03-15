"""
ExchangeRate-API 客户端

用于实时汇率转换
免费额度: 1500次/月
文档: https://www.exchangerate-api.com/docs/overview
"""

import os
import requests
from typing import Dict, Optional, List


class ExchangeRateClient:
    """ExchangeRate-API客户端 - 实时汇率"""

    BASE_URL = "https://v6.exchangerate-api.com/v6"

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化客户端

        Args:
            api_key: ExchangeRate-API Key，如不传则从环境变量EXCHANGERATE_API_KEY读取
        """
        # 用户提供的API密钥
        self.api_key = api_key or os.getenv("EXCHANGERATE_API_KEY", "86894aac3ce5084f3afc7068")

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        发起API请求

        Args:
            endpoint: API端点
            params: 请求参数

        Returns:
            API响应数据
        """
        url = f"{self.BASE_URL}/{self.api_key}/{endpoint.lstrip('/')}"

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if data.get("result") == "error":
                return {
                    "success": False,
                    "error": data.get("error-type", "Unknown error")
                }

            return {"success": True, "data": data}

        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timeout"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_latest_rates(self, base_currency: str = "USD") -> Dict:
        """
        获取最新汇率

        Args:
            base_currency: 基础货币代码（如 USD, EUR, CNY）

        Returns:
            汇率数据
        """
        endpoint = f"latest/{base_currency}"

        result = self._make_request(endpoint)

        if not result.get("success"):
            return {
                "success": False,
                "error": result.get("error", "Failed to get rates")
            }

        data = result["data"]
        return {
            "success": True,
            "base": data.get("base_code", base_currency),
            "rates": data.get("conversion_rates", {}),
            "timestamp": data.get("time_last_update_unix", 0),
            "date": data.get("date", "")
        }

    def convert_currency(
        self,
        amount: float,
        from_currency: str,
        to_currency: str
    ) -> Dict:
        """
        货币转换

        Args:
            amount: 金额
            from_currency: 源货币代码
            to_currency: 目标货币代码

        Returns:
            转换结果
        """
        endpoint = f"pair/{from_currency}/{to_currency}/{amount}"

        result = self._make_request(endpoint)

        if not result.get("success"):
            return {
                "success": False,
                "error": result.get("error", "Conversion failed")
            }

        data = result["data"]
        return {
            "success": True,
            "from_currency": data.get("base_code", from_currency),
            "to_currency": data.get("target_code", to_currency),
            "amount": amount,
            "converted_amount": data.get("conversion_result", 0),
            "rate": data.get("conversion_rate", 0),
            "timestamp": data.get("time_last_update_unix", 0)
        }

    def get_supported_currencies(self) -> Dict:
        """
        获取支持的货币列表

        Returns:
            货币代码列表
        """
        # 使用固定列表（API不直接提供此端点）
        currencies = [
            # 主要货币
            "USD", "EUR", "GBP", "JPY", "CNY", "CHF", "CAD", "AUD",
            "NZD", "SEK", "NOK", "DKK", "SGD", "HKD", "KRW", "INR",
            # 亚洲货币
            "THB", "MYR", "IDR", "VND", "PHP", "TWD", "BND", "LKR",
            "NPR", "PKR", "BDT", "LAK", "KHR", "MMK", "MVR",
            # 欧洲货币
            "PLN", "CZK", "HUF", "RON", "BGN", "HRK", "RUB", "UAH",
            # 中东货币
            "AED", "SAR", "QAR", "KWD", "BHD", "OMR", "JOD", "ILS",
            "TRY", "EGP", "MAD",
            # 非洲货币
            "ZAR", "EGP", "NGN", "KES", "GHS", "XOF", "XAF",
            # 美洲货币
            "MXN", "BRL", "ARS", "CLP", "COP", "PEN", "COP", "CRC",
            # 大洋洲货币
            "FJD", "PGK", "VUV", "WST", "TOP", "SBD",
        ]

        return {
            "success": True,
            "currencies": currencies,
            "count": len(currencies)
        }

    def get_historical_rates(
        self,
        date: str,
        base_currency: str = "USD"
    ) -> Dict:
        """
        获取历史汇率

        Args:
            date: 日期（YYYY-MM-DD格式）
            base_currency: 基础货币代码

        Returns:
            历史汇率数据
        """
        endpoint = f"historical/{date}/{base_currency}"

        result = self._make_request(endpoint)

        if not result.get("success"):
            return {
                "success": False,
                "error": result.get("error", "Failed to get historical rates")
            }

        data = result["data"]
        return {
            "success": True,
            "base": data.get("base_code", base_currency),
            "rates": data.get("conversion_rates", {}),
            "date": data.get("date", date)
        }

    def convert_to_multiple(
        self,
        amount: float,
        from_currency: str,
        to_currencies: List[str]
    ) -> Dict:
        """
        转换为多种货币

        Args:
            amount: 金额
            from_currency: 源货币代码
            to_currencies: 目标货币代码列表

        Returns:
            多种货币的转换结果
        """
        # 首先获取所有汇率
        rates_result = self.get_latest_rates(from_currency)

        if not rates_result.get("success"):
            return {
                "success": False,
                "error": rates_result.get("error", "Failed to get rates")
            }

        rates = rates_result.get("rates", {})
        results = {}

        for to_curr in to_currencies:
            if to_curr in rates:
                converted = amount * rates[to_curr]
                results[to_curr] = {
                    "amount": converted,
                    "rate": rates[to_curr]
                }
            else:
                results[to_curr] = {
                    "error": "Currency not supported"
                }

        return {
            "success": True,
            "from_currency": from_currency,
            "original_amount": amount,
            "conversions": results
        }


# 常用货币代码映射（国家/地区 -> 货币代码）
COUNTRY_TO_CURRENCY = {
    # 亚洲
    "China": "CNY", "Japan": "JPY", "South Korea": "KRW",
    "Thailand": "THB", "Singapore": "SGD", "Malaysia": "MYR",
    "Indonesia": "IDR", "Vietnam": "VND", "Philippines": "PHP",
    "Cambodia": "KHR", "Laos": "LAK", "Myanmar": "MMK",
    "India": "INR", "Nepal": "NPR", "Sri Lanka": "LKR",
    "Bangladesh": "BDT", "Pakistan": "PKR",
    "Taiwan": "TWD", "Hong Kong": "HKD", "Macau": "MOP",
    # 欧洲
    "United Kingdom": "GBP", "France": "EUR", "Germany": "EUR",
    "Italy": "EUR", "Spain": "EUR", "Netherlands": "EUR",
    "Switzerland": "CHF", "Sweden": "SEK", "Norway": "NOK",
    "Denmark": "DKK", "Poland": "PLN", "Czech Republic": "CZK",
    "Hungary": "HUF", "Romania": "RON", "Russia": "RUB",
    # 中东
    "United Arab Emirates": "AED", "Saudi Arabia": "SAR",
    "Qatar": "QAR", "Kuwait": "KWD", "Bahrain": "BHD",
    "Oman": "OMR", "Jordan": "JOD", "Israel": "ILS",
    "Turkey": "TRY", "Egypt": "EGP", "Morocco": "MAD",
    # 美洲
    "United States": "USD", "Canada": "CAD", "Mexico": "MXN",
    "Brazil": "BRL", "Argentina": "ARS", "Chile": "CLP",
    "Peru": "PEN", "Colombia": "COP", "Costa Rica": "CRC",
    # 大洋洲
    "Australia": "AUD", "New Zealand": "NZD",
    "Fiji": "FJD", "Papua New Guinea": "PGK",
    # 非洲
    "South Africa": "ZAR", "Kenya": "KES", "Ghana": "GHS",
    "Nigeria": "NGN",
}


def get_currency_for_country(country_name: str) -> str:
    """根据国家名称获取货币代码"""
    return COUNTRY_TO_CURRENCY.get(country_name, "USD")


# 使用示例
if __name__ == "__main__":
    client = ExchangeRateClient()

    print("=== 获取最新汇率 ===")
    rates = client.get_latest_rates("USD")
    if rates["success"]:
        print(f"基础货币: {rates['base']}")
        print(f"CNY汇率: {rates['rates'].get('CNY', 'N/A')}")
        print(f"EUR汇率: {rates['rates'].get('EUR', 'N/A')}")
        print(f"JPY汇率: {rates['rates'].get('JPY', 'N/A')}")

    print("\n=== 货币转换 ===")
    conversion = client.convert_currency(100, "USD", "CNY")
    if conversion["success"]:
        print(f"100 USD = {conversion['converted_amount']:.2f} CNY")
        print(f"汇率: {conversion['rate']}")
