"""
RestCountries API 客户端

获取国家基础信息（货币、语言、首都等）
完全免费，无需API Key
文档: https://restcountries.com/v3.1
"""

import requests
from typing import Dict, List, Optional


class RestCountriesClient:
    """RestCountries API客户端 - 国家信息"""

    BASE_URL = "https://restcountries.com/v3.1"

    def __init__(self):
        """初始化客户端（无需API Key）"""
        pass

    def _make_request(self, endpoint: str) -> Dict:
        """
        发起API请求

        Args:
            endpoint: API端点

        Returns:
            API响应数据
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()

            # RestCountries返回404时不是标准JSON
            if isinstance(data, dict) and data.get("status") == 404:
                return {
                    "success": False,
                    "error": data.get("message", "Not found")
                }

            return {"success": True, "data": data}

        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timeout"}
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {"success": False, "error": "Country not found"}
            return {"success": False, "error": str(e)}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_country_by_name(self, name: str, full_text: bool = False) -> Dict:
        """
        按名称获取国家信息

        Args:
            name: 国家名称
            full_text: 是否完整匹配

        Returns:
            国家详细信息
        """
        endpoint = f"/name/{name}"
        if full_text:
            endpoint += "?fullText=true"

        result = self._make_request(endpoint)

        if not result.get("success"):
            return result

        data = result["data"]
        # API返回数组
        countries = data if isinstance(data, list) else [data]

        if not countries:
            return {"success": False, "error": "No country found"}

        country = countries[0]
        return {
            "success": True,
            "country": self._parse_country_data(country)
        }

    def get_country_by_code(self, code: str) -> Dict:
        """
        按国家代码获取信息

        Args:
            code: 国家代码（如 JP, US, CN）

        Returns:
            国家详细信息
        """
        endpoint = f"/alpha/{code}"

        result = self._make_request(endpoint)

        if not result.get("success"):
            return result

        data = result["data"]
        country = data if isinstance(data, dict) else data[0]

        return {
            "success": True,
            "country": self._parse_country_data(country)
        }

    def get_all_countries(self, fields: Optional[List[str]] = None) -> Dict:
        """
        获取所有国家列表

        Args:
            fields: 需要返回的字段列表

        Returns:
            所有国家的简要信息
        """
        endpoint = "/all"
        if fields:
            endpoint += f"?fields={','.join(fields)}"

        result = self._make_request(endpoint)

        if not result.get("success"):
            return result

        countries = result["data"] if isinstance(result["data"], list) else []

        return {
            "success": True,
            "countries": [
                self._parse_country_data(c) for c in countries
            ],
            "count": len(countries)
        }

    def get_countries_by_region(self, region: str) -> Dict:
        """
        按地区获取国家

        Args:
            region: 地区名称（Africa, Americas, Asia, Europe, Oceania）

        Returns:
            该地区的国家列表
        """
        endpoint = f"/region/{region}"

        result = self._make_request(endpoint)

        if not result.get("success"):
            return result

        countries = result["data"] if isinstance(result["data"], list) else []

        return {
            "success": True,
            "region": region,
            "countries": [
                self._parse_country_data(c) for c in countries
            ],
            "count": len(countries)
        }

    def get_countries_by_currency(self, currency: str) -> Dict:
        """
        按货币获取国家

        Args:
            currency: 货币代码（如 USD, EUR, JPY）

        Returns:
            使用该货币的国家列表
        """
        endpoint = f"/currency/{currency}"

        result = self._make_request(endpoint)

        if not result.get("success"):
            return result

        countries = result["data"] if isinstance(result["data"], list) else []

        return {
            "success": True,
            "currency": currency,
            "countries": [
                self._parse_country_data(c) for c in countries
            ],
            "count": len(countries)
        }

    def search_countries(self, query: str) -> Dict:
        """
        搜索国家

        Args:
            query: 搜索关键词

        Returns:
            匹配的国家列表
        """
        endpoint = f"/translation/{query}"

        result = self._make_request(endpoint)

        if not result.get("success"):
            return result

        countries = result["data"] if isinstance(result["data"], list) else []

        return {
            "success": True,
            "query": query,
            "countries": [
                self._parse_country_data(c) for c in countries
            ],
            "count": len(countries)
        }

    def get_country_info_for_travel(self, country_name: str) -> Dict:
        """
        获取国家旅游相关信息

        Args:
            country_name: 国家名称

        Returns:
            旅游所需的信息
        """
        result = self.get_country_by_name(country_name)

        if not result.get("success"):
            return result

        country = result["country"]

        return {
            "success": True,
            "country_name": country.get("name", ""),
            "country_code": country.get("code", ""),
            "capital": country.get("capital", ""),
            "region": country.get("region", ""),
            "subregion": country.get("subregion", ""),
            "population": country.get("population", 0),
            "area": country.get("area", 0),
            "languages": country.get("languages", []),
            "currency": country.get("currency", {}),
            "flag": country.get("flag", ""),
            "timezones": country.get("timezones", []),
            "calling_code": country.get("calling_code", ""),
            "travel_info": {
                "visa_required": self._check_visa_requirement(country_name),
                "best_season": self._get_best_season(country.get("season", "")),
                "safety_level": self._get_safety_level(country_name),
                "budget_level": self._get_budget_level(country.get("currency", {}).get("code", ""))
            }
        }

    def _parse_country_data(self, country: Dict) -> Dict:
        """解析国家数据"""
        return {
            "name": country.get("name", {}).get("common", country.get("name", "")),
            "code": country.get("cca2", ""),
            "ccn3": country.get("ccn3", ""),
            "capital": country.get("capital", [""])[0] if country.get("capital") else "",
            "region": country.get("region", ""),
            "subregion": country.get("subregion", ""),
            "population": country.get("population", 0),
            "area": country.get("area", 0),
            "languages": list(country.get("languages", {}).values()),
            "currency": self._parse_currency(country.get("currencies", {})),
            "flag": country.get("flags", {}).get("png", ""),
            "coat_of_arms": country.get("coatOfArms", {}).get("png", ""),
            "timezones": country.get("timezones", []),
            "calling_code": country.get("idd", {}).get("root", ""),
            "independent": country.get("independent", True),
            "un_member": country.get("unMember", False)
        }

    def _parse_currency(self, currencies: Dict) -> Dict:
        """解析货币信息"""
        if not currencies:
            return {"code": "USD", "name": "US Dollar", "symbol": "$"}

        for code, info in currencies.items():
            return {
                "code": code,
                "name": info.get("name", ""),
                "symbol": info.get("symbol", "")
            }

        return {"code": "USD", "name": "US Dollar", "symbol": "$"}

    def _check_visa_requirement(self, country: str) -> str:
        """检查签证要求（简化版本）"""
        # 中国公民免签/落地签国家（部分）
        visa_free = [
            "Thailand", "Singapore", "Malaysia", "Indonesia", "Vietnam",
            "Cambodia", "Laos", "Myanmar", "Philippines", "South Korea",
            "Japan", "UAE", "Qatar", "Bahrain", "Morocco", "Egypt",
            "Serbia", "Bosnia", "Albania", "North Macedonia"
        ]

        if country in visa_free:
            return "免签或落地签"
        elif country in ["United States", "United Kingdom", "Canada", "Australia"]:
            return "需要签证"
        else:
            return "请查询最新要求"

    def _get_best_season(self, season_info: str) -> str:
        """获取最佳旅游季节"""
        # 这里可以扩展为更详细的季节数据
        return "全年皆宜"

    def _get_safety_level(self, country: str) -> str:
        """获取安全等级（简化版本）"""
        safe_countries = [
            "Singapore", "Japan", "Switzerland", "Denmark", "Iceland",
            "New Zealand", "Canada", "Norway", "Finland", "Sweden"
        ]

        if country in safe_countries:
            return "非常安全"
        else:
            return "注意安全"

    def _get_budget_level(self, currency_code: str) -> str:
        """根据货币获取预算等级"""
        # 这是一个粗略的估算
        expensive = ["CHF", "NOK", "SEK", "GBP", "EUR", "AUD", "CAD"]
        moderate = ["USD", "JPY", "KRW", "SGD", "HKD", "MYR"]
        budget = ["THB", "VND", "IDR", "PHP", "INR", "LKR"]

        if currency_code in expensive:
            return "高消费"
        elif currency_code in moderate:
            return "中等消费"
        elif currency_code in budget:
            return "低消费"
        else:
            return "中等"


# 常用国家名称映射（别名 -> 标准名称）
COUNTRY_ALIASES = {
    # 亚洲
    "日本": "Japan", "东京": "Japan",
    "韩国": "South Korea", "南韩": "South Korea", "首尔": "South Korea",
    "泰国": "Thailand", "曼谷": "Thailand",
    "新加坡": "Singapore",
    "马来西亚": "Malaysia", "吉隆坡": "Malaysia",
    "印尼": "Indonesia", "印度尼西亚": "Indonesia", "巴厘岛": "Indonesia",
    "越南": "Vietnam",
    "菲律宾": "Philippines",
    "柬埔寨": "Cambodia",
    "老挝": "Laos",
    "缅甸": "Myanmar",
    "印度": "India",
    "尼泊尔": "Nepal",
    "斯里兰卡": "Sri Lanka",
    # 欧洲
    "英国": "United Kingdom", "伦敦": "United Kingdom",
    "法国": "France", "巴黎": "France",
    "德国": "Germany", "柏林": "Germany",
    "意大利": "Italy", "罗马": "Italy",
    "西班牙": "Spain",
    "瑞士": "Switzerland",
    "荷兰": "Netherlands",
    "希腊": "Greece",
    # 北美
    "美国": "United States", "USA": "United States",
    "加拿大": "Canada",
    "墨西哥": "Mexico",
    # 大洋洲
    "澳大利亚": "Australia",
    "新西兰": "New Zealand",
    # 中东
    "阿联酋": "United Arab Emirates", "迪拜": "United Arab Emirates",
    # 非洲
    "南非": "South Africa",
    "埃及": "Egypt",
    "摩洛哥": "Morocco",
}


def normalize_country_name(name: str) -> str:
    """规范化国家名称"""
    return COUNTRY_ALIASES.get(name, name)


# 使用示例
if __name__ == "__main__":
    client = RestCountriesClient()

    print("=== 按名称查询 ===")
    result = client.get_country_by_name("Japan")
    if result["success"]:
        country = result["country"]
        print(f"国家: {country['name']}")
        print(f"首都: {country['capital']}")
        print(f"货币: {country['currency']}")
        print(f"语言: {country['languages']}")

    print("\n=== 获取旅游信息 ===")
    travel = client.get_country_info_for_travel("Thailand")
    if travel["success"]:
        print(f"国家: {travel['country_name']}")
        print(f"签证: {travel['travel_info']['visa_required']}")
        print(f"货币: {travel['currency']['code']}")
        print(f"预算: {travel['travel_info']['budget_level']}")
