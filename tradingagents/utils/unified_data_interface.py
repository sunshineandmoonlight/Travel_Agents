"""
统一数据接口 - 自动切换国内/国际数据源
"""

from typing import Dict, List
from abc import ABC, abstractmethod

from tradingagents.integrations.amap_client import AmapClient
from tradingagents.integrations.serpapi_client import SerpAPIClient
from tradingagents.integrations.openmeteo_client import OpenMeteoClient
from tradingagents.integrations.restcountries_client import RestCountriesClient, normalize_country_name
from tradingagents.integrations.exchange_rate_client import ExchangeRateClient, get_currency_for_country
from tradingagents.integrations.opentripmap_client import OpenTripMapClient


class BaseTravelDataProvider(ABC):
    """旅行数据提供者基类"""

    @abstractmethod
    def search_attractions(self, location: str, interest_type: str = "") -> Dict:
        """搜索景点"""
        pass

    @abstractmethod
    def get_weather(self, location: str, days: int = 7) -> Dict:
        """获取天气"""
        pass

    @abstractmethod
    def estimate_transport_cost(self, origin: str, destination: str) -> Dict:
        """估算交通费用"""
        pass

    @abstractmethod
    def get_location_info(self, location: str) -> Dict:
        """获取地点信息"""
        pass


class DomesticDataProvider(BaseTravelDataProvider):
    """国内数据提供者（使用高德地图API + Open-Meteo）"""

    def __init__(self):
        self.amap_client = AmapClient()
        self.weather_client = OpenMeteoClient()

    def search_attractions(self, location: str, interest_type: str = "") -> Dict:
        """搜索国内景点"""
        # 兴趣类型映射
        keyword_map = {
            "自然": "风景区",
            "寺庙": "寺庙",
            "古镇": "古镇",
            "博物馆": "博物馆",
            "公园": "公园",
            "历史": "历史景点",
            "": "风景名胜"  # 默认
        }
        keyword = keyword_map.get(interest_type, "风景名胜")

        result = self.amap_client.search_attractions(location, keyword, 20)

        # 添加国内标识
        if result.get("success"):
            result["destination_type"] = "domestic"
        else:
            result["destination_type"] = "domestic"

        return result

    def get_weather(self, location: str, days: int = 7) -> Dict:
        """获取国内天气"""
        result = self.amap_client.get_weather(location, days)

        if result.get("success"):
            result["destination_type"] = "domestic"
        else:
            result["destination_type"] = "domestic"

        return result

    def estimate_transport_cost(self, origin: str, destination: str) -> Dict:
        """估算国内交通费用（高铁）"""
        return self.amap_client.estimate_transport_cost(origin, destination, "high_speed_rail")

    def get_location_info(self, location: str) -> Dict:
        """获取国内城市信息"""
        # 从城市数据库获取信息
        from .destination_classifier import DestinationClassifier

        classification = DestinationClassifier.classify(location)

        return {
            "name": classification.get("normalized_name", location),
            "type": "domestic",
            "currency": "CNY",
            "timezone": "Asia/Shanghai",
            "language": "zh",
            "confidence": classification.get("confidence", 0)
        }


class InternationalDataProvider(BaseTravelDataProvider):
    """国际数据提供者（使用OpenTripMap + RestCountries + ExchangeRate + Open-Meteo）"""

    def __init__(self):
        self.tripmap_client = OpenTripMapClient()
        self.countries_client = RestCountriesClient()
        self.exchange_client = ExchangeRateClient()
        self.weather_client = OpenMeteoClient()
        # SerpAPI作为备用
        self.serp_client = SerpAPIClient()

    def search_attractions(self, location: str, interest_type: str = "") -> Dict:
        """搜索国际景点（使用OpenTripMap API）"""
        # 兴趣类型映射
        type_map = {
            "": "",
            "自然": "natural",
            "历史": "historic",
            "博物馆": "museums",
            "购物": "shopping",
            "美食": "other",
            "宗教": "religious",
            "建筑": "architecture"
        }

        tripmap_type = type_map.get(interest_type, "")

        try:
            # 使用OpenTripMap搜索
            if tripmap_type:
                result = self.tripmap_client.search_by_type(
                    location, tripmap_type, limit=20
                )
            else:
                result = self.tripmap_client.search_attractions_by_name(
                    location, limit=20
                )

            if result.get("success") and result.get("count", 0) > 0:
                # 转换为统一格式
                attractions = []
                for attr in result.get("attractions", []):
                    attractions.append({
                        "name": attr.get("name", ""),
                        "address": attr.get("address", ""),
                        "description": attr.get("description", ""),
                        "rating": 0,  # OpenTripMap没有评分
                        "reviews": 0,
                        "type": attr.get("kind", ""),
                        "xid": attr.get("xid", ""),
                        "distance": attr.get("distance", 0),
                        "image": attr.get("image", ""),
                        "coordinates": attr.get("coordinates", []),
                        "source": "opentripmap"
                    })

                return {
                    "success": True,
                    "attractions": attractions,
                    "count": len(attractions),
                    "destination": location,
                    "destination_type": "international",
                    "source": "OpenTripMap"
                }

        except Exception as e:
            import logging
            logging.warning(f"[OpenTripMap] 搜索失败: {e}，尝试使用备用方案")

        # 降级：使用SerpAPI
        query_map = {
            "": "tourist attractions",
            "自然": "nature attractions",
            "历史": "historical sites",
            "博物馆": "museums",
            "购物": "shopping",
            "美食": "food",
        }

        query = query_map.get(interest_type, "tourist attractions")
        search_query = f"{query} in {location}"

        result = self.serp_client.search_attractions(search_query, location, 20)

        if result.get("success") and result.get("attractions"):
            for attr in result["attractions"]:
                attr["source"] = "serpapi"
            result["destination_type"] = "international"
            result["source"] = "SerpAPI"
            return result

        # 如果都失败，返回空结果
        return {
            "success": False,
            "error": "No attractions found",
            "destination_type": "international",
            "destination": location
        }

    def get_weather(self, location: str, days: int = 7) -> Dict:
        """获取国际天气"""
        result = self.weather_client.get_weather_forecast(location, days)

        if result.get("success"):
            result["destination_type"] = "international"
        else:
            result["destination_type"] = "international"

        return result

    def estimate_transport_cost(self, origin: str, destination: str) -> Dict:
        """估算国际交通费用（机票）"""
        return self.serp_client.estimate_flight_cost(origin, destination)

    def get_location_info(self, location: str) -> Dict:
        """获取国际国家信息（使用RestCountries API）"""
        # 规范化国家名称
        country_name = normalize_country_name(location)

        # 尝试从RestCountries获取详细信息
        try:
            result = self.countries_client.get_country_info_for_travel(country_name)

            if result.get("success"):
                country = result
                return {
                    "name": country.get("country_name", location),
                    "code": country.get("country_code", ""),
                    "type": "international",
                    "currency": country.get("currency", {}).get("code", "USD"),
                    "currency_name": country.get("currency", {}).get("name", "US Dollar"),
                    "currency_symbol": country.get("currency", {}).get("symbol", "$"),
                    "capital": country.get("capital", ""),
                    "region": country.get("region", ""),
                    "subregion": country.get("subregion", ""),
                    "languages": country.get("languages", []),
                    "flag": country.get("flag", ""),
                    "timezones": country.get("timezones", []),
                    "calling_code": country.get("calling_code", ""),
                    "population": country.get("population", 0),
                    "timezone": country.get("timezones", ["UTC"])[0] if country.get("timezones") else "UTC",
                    "language": country.get("languages", ["en"])[0] if country.get("languages") else "en",
                    "travel_info": country.get("travel_info", {}),
                    "confidence": 1.0
                }
        except Exception as e:
            pass  # 降级到基础信息

        # 降级：返回基础信息
        return {
            "name": location,
            "type": "international",
            "currency": get_currency_for_country(location),
            "timezone": "auto",
            "language": "en",
            "confidence": 0.5
        }

    def search_restaurants(self, location: str, area: str = "", limit: int = 10) -> Dict:
        """搜索国际餐厅"""
        query = f"restaurants in {location}"
        if area:
            query = f"best restaurants in {area}, {location}"

        result = self.serp_client.search_restaurants(query, location, limit)

        if result.get("success"):
            # 添加国际特色信息
            for restaurant in result.get("restaurants", []):
                restaurant["cuisine_type"] = self._guess_cuisine_type(location, restaurant.get("name", ""))
                # 估算当地货币价格
                restaurant["local_currency"] = self._get_local_currency(location)

        result["destination_type"] = "international"
        return result

    def search_hotels(self, location: str, area: str = "", limit: int = 10) -> Dict:
        """搜索国际酒店"""
        query = f"hotels in {location}"
        if area:
            query = f"hotels in {area}, {location}"

        result = self.serp_client.search_hotels(query, location, limit)

        if result.get("success"):
            # 添加货币信息
            currency = self._get_local_currency(location)
            for hotel in result.get("hotels", []):
                hotel["local_currency"] = currency
                # 转换价格为美元（简化处理）
                price_str = hotel.get("price", "")
                if price_str:
                    hotel["price_usd_estimate"] = self._estimate_price_usd(price_str, currency)

        result["destination_type"] = "international"
        return result

    def search_destinations(self, keywords: str, scope: str = "international") -> Dict:
        """搜索国际目的地"""
        from tradingagents.tools.travel_tools import DestinationSearchTool

        search_tool = DestinationSearchTool()
        destinations = search_tool.search_destinations(keywords, scope)

        return {
            "success": True,
            "destinations": destinations,
            "count": len(destinations),
            "destination_type": "international"
        }

    def plan_route(self, origin: str, destination: str, city: str = "") -> Dict:
        """规划国际路线（使用Google Directions API的简化版本）"""
        # SerpAPI不直接支持路线规划，这里使用估算
        # 可以后续集成Google Maps Directions API

        # 距离估算（公里）
        distance_map = {
            ("Tokyo", "Kyoto"): 450,
            ("Tokyo", "Osaka"): 500,
            ("Bangkok", "Chiang Mai"): 700,
            ("Bangkok", "Phuket"): 860,
            ("Singapore", "Kuala Lumpur"): 320,
            ("Paris", "London"): 450,
            ("Paris", "Rome"): 1400,
            ("Rome", "Florence"): 280,
        }

        # 尝试获取距离
        distance = distance_map.get((origin, destination))
        if not distance:
            distance = distance_map.get((destination, origin))

        if not distance:
            distance = 500  # 默认估算

        # 交通方式选项
        transport_options = []

        # 飞行（远距离）
        if distance > 300:
            transport_options.append({
                "method": "飞机",
                "duration": f"{1 + distance // 800}小时",
                "cost": distance * 0.5 + 100,  # 简化估算
                "description": f"从{origin}飞往{destination}"
            })

        # 火车（某些国家有）
        if distance < 800:
            train_countries = ["Japan", "France", "Italy", "UK", "Germany", "Switzerland"]
            country = self._guess_country_from_city(origin)
            if country in train_countries:
                transport_options.append({
                    "method": "火车",
                    "duration": f"{distance // 100 + 1}小时",
                    "cost": distance * 0.3,
                    "description": f"乘坐火车从{origin}到{destination}"
                })

        # 大巴（预算选项）
        transport_options.append({
            "method": "大巴",
            "duration": f"{distance // 60 + 2}小时",
            "cost": distance * 0.1,
            "description": f"长途大巴从{origin}到{destination}"
        })

        return {
            "success": True,
            "origin": origin,
            "destination": destination,
            "distance_km": distance,
            "transport_options": transport_options,
            "recommended": transport_options[0] if transport_options else None,
            "destination_type": "international"
        }

    def _guess_cuisine_type(self, location: str, restaurant_name: str) -> str:
        """猜测餐厅菜系类型"""
        cuisine_map = {
            "Japan": "Japanese",
            "Tokyo": "Japanese",
            "Kyoto": "Japanese",
            "Thailand": "Thai",
            "Bangkok": "Thai",
            "Korea": "Korean",
            "Seoul": "Korean",
            "Italy": "Italian",
            "Rome": "Italian",
            "France": "French",
            "Paris": "French",
            "India": "Indian",
            "China": "Chinese",
            "USA": "American",
            "Mexico": "Mexican"
        }

        for key, cuisine in cuisine_map.items():
            if key in location or key in restaurant_name:
                return cuisine

        return "International"

    def _get_local_currency(self, location: str) -> str:
        """获取当地货币代码"""
        currency_map = {
            "Japan": "JPY", "Tokyo": "JPY", "Osaka": "JPY", "Kyoto": "JPY",
            "Thailand": "THB", "Bangkok": "THB", "Phuket": "THB",
            "Korea": "KRW", "Seoul": "KRW", "Busan": "KRW",
            "Singapore": "SGD",
            "Malaysia": "MYR", "Kuala Lumpur": "MYR",
            "Vietnam": "VND", "Hanoi": "VND",
            "Indonesia": "IDR", "Bali": "IDR",
            "USA": "USD", "New York": "USD", "Los Angeles": "USD",
            "UK": "GBP", "London": "GBP",
            "Europe": "EUR", "France": "EUR", "Paris": "EUR",
            "Italy": "EUR", "Rome": "EUR", "Venice": "EUR",
            "Australia": "AUD", "Sydney": "AUD",
            "China": "CNY"
        }

        for key, currency in currency_map.items():
            if key in location:
                return currency

        return "USD"

    def _estimate_price_usd(self, price_str: str, currency: str) -> float:
        """估算美元价格"""
        # 简化处理：移除货币符号和数字
        import re
        numbers = re.findall(r'\d+', price_str)
        if numbers:
            price = float(numbers[0])
            # 简化汇率（实际应该调用汇率API）
            exchange_rates = {
                "JPY": 0.007,   # 1 JPY ≈ 0.007 USD
                "THB": 0.028,   # 1 THB ≈ 0.028 USD
                "KRW": 0.00075, # 1 KRW ≈ 0.00075 USD
                "SGD": 0.74,    # 1 SGD ≈ 0.74 USD
                "MYR": 0.22,    # 1 MYR ≈ 0.22 USD
                "EUR": 1.08,    # 1 EUR ≈ 1.08 USD
                "GBP": 1.27,    # 1 GBP ≈ 1.27 USD
                "AUD": 0.65,    # 1 AUD ≈ 0.65 USD
                "CNY": 0.14     # 1 CNY ≈ 0.14 USD
            }
            rate = exchange_rates.get(currency, 1)
            return price * rate
        return 0

    def _guess_country_from_city(self, city: str) -> str:
        """根据城市猜测国家"""
        city_to_country = {
            "Tokyo": "Japan", "Osaka": "Japan", "Kyoto": "Japan",
            "Seoul": "South Korea", "Busan": "South Korea",
            "Bangkok": "Thailand", "Phuket": "Thailand", "Chiang Mai": "Thailand",
            "Singapore": "Singapore",
            "Kuala Lumpur": "Malaysia", "Penang": "Malaysia",
            "Hanoi": "Vietnam", "Ho Chi Minh": "Vietnam",
            "Paris": "France", "Nice": "France",
            "London": "UK", "Edinburgh": "UK",
            "Rome": "Italy", "Venice": "Italy", "Florence": "Italy",
            "Barcelona": "Spain", "Madrid": "Spain",
            "Berlin": "Germany", "Munich": "Germany",
            "Amsterdam": "Netherlands",
            "Zurich": "Switzerland", "Geneva": "Switzerland",
            "Athens": "Greece",
            "New York": "USA", "Los Angeles": "USA", "Las Vegas": "USA",
            "Sydney": "Australia", "Melbourne": "Australia"
        }

        return city_to_country.get(city, "Unknown")

    def convert_currency(
        self,
        amount: float,
        from_currency: str,
        to_currency: str = "CNY"
    ) -> Dict:
        """
        货币转换（使用ExchangeRate-API）

        Args:
            amount: 金额
            from_currency: 源货币代码
            to_currency: 目标货币代码（默认人民币）

        Returns:
            转换结果
        """
        try:
            result = self.exchange_client.convert_currency(
                amount, from_currency, to_currency
            )

            if result.get("success"):
                return {
                    "success": True,
                    "original_amount": amount,
                    "from_currency": from_currency,
                    "to_currency": to_currency,
                    "converted_amount": result.get("converted_amount", 0),
                    "rate": result.get("rate", 0),
                    "timestamp": result.get("timestamp", 0)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Conversion failed")
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_exchange_rates(self, base_currency: str = "USD") -> Dict:
        """
        获取汇率表

        Args:
            base_currency: 基础货币代码

        Returns:
            汇率表
        """
        try:
            result = self.exchange_client.get_latest_rates(base_currency)

            if result.get("success"):
                return {
                    "success": True,
                    "base": result.get("base", base_currency),
                    "rates": result.get("rates", {}),
                    "timestamp": result.get("timestamp", 0)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Failed to get rates")
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_country_details(self, country_name: str) -> Dict:
        """
        获取国家详细信息（使用RestCountries API）

        Args:
            country_name: 国家名称

        Returns:
            国家详细信息
        """
        try:
            result = self.countries_client.get_country_info_for_travel(country_name)

            if result.get("success"):
                return result
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Country not found")
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class UnifiedDataProvider:
    """统一数据提供者（自动切换国内/国际）"""

    def __init__(self):
        self.domestic = DomesticDataProvider()
        self.international = InternationalDataProvider()

    def get_provider(self, destination: str) -> BaseTravelDataProvider:
        """根据目的地类型返回对应的数据提供者"""
        from .destination_classifier import DestinationClassifier

        classification = DestinationClassifier.classify(destination)

        if classification["type"] == "domestic":
            return self.domestic
        elif classification["type"] == "international":
            return self.international
        else:
            # 无法判断时，默认使用国际
            return self.international

    def search_attractions(self, destination: str, interest_type: str = "") -> Dict:
        """统一景点搜索接口"""
        provider = self.get_provider(destination)
        result = provider.search_attractions(destination, interest_type)
        result["destination_type"] = "domestic" if isinstance(provider, DomesticDataProvider) else "international"
        return result

    def get_weather(self, destination: str, days: int = 7) -> Dict:
        """统一天气查询接口"""
        provider = self.get_provider(destination)
        result = provider.get_weather(destination, days)
        result["destination_type"] = "domestic" if isinstance(provider, DomesticDataProvider) else "international"
        return result

    def estimate_transport_cost(self, origin: str, destination: str) -> Dict:
        """统一交通费用估算接口"""
        provider = self.get_provider(destination)
        return provider.estimate_transport_cost(origin, destination)
