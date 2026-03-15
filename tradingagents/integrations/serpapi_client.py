"""
SerpAPI 客户端

用于国际旅游数据获取
- Google Places 景点搜索
- 酒店搜索
- 餐厅搜索
"""

import os
import requests
from typing import Dict, List, Optional, Any


class SerpAPIClient:
    """SerpAPI客户端 - Google搜索结果API"""

    BASE_URL = "https://serpapi.com/search"

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化客户端

        Args:
            api_key: SerpAPI Key，如不传则从环境变量SERPAPI_KEY读取
        """
        # 默认API密钥
        DEFAULT_API_KEY = "dd5682943bc32a9ac9a83ef9772ec819b8aa1f3f74e418f960a4715ae18b2d6e"
        self.api_key = api_key or os.getenv("SERPAPI_KEY", DEFAULT_API_KEY)

    def _make_request(self, engine: str, params: Dict) -> Dict:
        """
        发起API请求

        Args:
            engine: 搜索引擎类型
            params: 请求参数

        Returns:
            API响应数据
        """
        params["engine"] = engine
        params["api_key"] = self.api_key
        params["hl"] = "en"  # 语言

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if data.get("error"):
                return {
                    "success": False,
                    "error": data.get("error", "Unknown error")
                }

            return {"success": True, "data": data}

        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timeout"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_attractions(
        self,
        query: str,
        location: str = "",
        limit: int = 20
    ) -> Dict:
        """
        搜索景点

        Args:
            query: 搜索关键词（如 "tourist attractions in Tokyo"）
            location: 地理位置（如 "Tokyo, Japan"）
            limit: 返回数量限制

        Returns:
            景点列表
        """
        params = {
            "q": query,
            "location": location,
            "google_domain": "google.com",
            "gl": "us",  # 地区
            "num": limit
        }

        result = self._make_request("google", params)

        if not result.get("success"):
            return {
                "success": False,
                "error": result.get("error", "Search failed"),
                "query": query
            }

        data = result["data"]
        places_results = data.get("places_results", [])
        local_results = data.get("local_results", [])
        organic_results = data.get("organic_results", [])

        # 确保是列表类型
        if not isinstance(places_results, list):
            places_results = []
        if not isinstance(local_results, list):
            local_results = []
        if not isinstance(organic_results, list):
            organic_results = []

        # 优先使用places_results
        attractions = []

        # 处理places_results
        for place in places_results[:limit]:
            attractions.append({
                "name": place.get("title", ""),
                "address": place.get("address", ""),
                "description": place.get("description", ""),
                "rating": place.get("rating", 0),
                "reviews": place.get("reviews", 0),
                "phone": place.get("phone", ""),
                "website": place.get("website", ""),
                "type": "place_result",
                "thumbnail": place.get("thumbnail", ""),
            })

        # 如果places_results不够，补充local_results
        if len(attractions) < limit and local_results:
            for item in local_results[:limit - len(attractions)]:
                attractions.append({
                    "name": item.get("title", ""),
                    "address": item.get("address", ""),
                    "description": "",
                    "rating": item.get("rating", 0),
                    "reviews": item.get("reviews", 0),
                    "phone": "",
                    "website": item.get("links", {}).get("website", ""),
                    "type": "local_result"
                })

        return {
            "success": True,
            "query": query,
            "location": location,
            "attractions": attractions,
            "count": len(attractions)
        }

    def search_hotels(
        self,
        query: str,
        location: str = "",
        limit: int = 20
    ) -> Dict:
        """
        搜索酒店

        Args:
            query: 搜索关键词
            location: 地理位置或坐标
            limit: 返回数量限制

        Returns:
            酒店列表
        """
        params = {
            "q": query,
            "location": location,
            "google_domain": "google.com",
            "num": limit
        }

        result = self._make_request("google_hotels", params)

        if not result.get("success"):
            return {"success": False, "error": result.get("error")}

        data = result["data"]
        properties = data.get("properties", [])

        # 确保是列表类型
        if not isinstance(properties, list):
            properties = []

        hotels = []
        for prop in properties[:limit]:
            # 获取价格信息
            price_info = prop.get("rate", {})
            price = price_info.get("price", "") if isinstance(price_info, dict) else ""

            hotels.append({
                "name": prop.get("name", ""),
                "description": prop.get("description", ""),
                "address": prop.get("address", ""),
                "price": price,
                "rating": prop.get("rating", 0),
                "reviews": prop.get("reviews", 0),
                "stars": prop.get("stars", 0),
                "amenities": prop.get("amenities", []) or [],
                "thumbnail": prop.get("images", [{}])[0].get("thumbnail", "") if prop.get("images") else ""
            })

        return {
            "success": True,
            "hotels": hotels,
            "count": len(hotels)
        }

    def search_restaurants(
        self,
        query: str,
        location: str = "",
        limit: int = 20
    ) -> Dict:
        """
        搜索餐厅

        Args:
            query: 搜索关键词
            location: 地理位置或坐标
            limit: 返回数量限制

        Returns:
            餐厅列表
        """
        params = {
            "q": query,
            "location": location,
            "google_domain": "google.com",
            "num": limit
        }

        result = self._make_request("google", params)

        if not result.get("success"):
            return {"success": False, "error": result.get("error")}

        data = result["data"]
        local_results = data.get("local_results", [])
        places_results = data.get("places_results", [])

        # 确保是列表类型
        if not isinstance(local_results, list):
            local_results = []
        if not isinstance(places_results, list):
            places_results = []

        restaurants = []

        # 处理local_results
        for item in local_results[:limit]:
            restaurants.append({
                "name": item.get("title", ""),
                "address": item.get("address", ""),
                "rating": item.get("rating", 0),
                "reviews": item.get("reviews", 0),
                "phone": item.get("phone", ""),
                "type": "restaurant",
            })

        # 处理places_results
        if len(restaurants) < limit:
            for place in places_results[:limit - len(restaurants)]:
                restaurants.append({
                    "name": place.get("title", ""),
                    "address": place.get("address", ""),
                    "rating": place.get("rating", 0),
                    "reviews": place.get("reviews", 0),
                    "phone": place.get("phone", ""),
                    "type": "restaurant",
                })

        return {
            "success": True,
            "restaurants": restaurants,
            "count": len(restaurants)
        }

    def search_flights(
        self,
        origin: str,
        destination: str,
        date: str,
        return_date: Optional[str] = None
    ) -> Dict:
        """
        搜索航班（使用Google Flights）

        Args:
            origin: 出发地IATA代码（如 NRT, HND）
            destination: 目的地IATA代码
            date: 出发日期（YYYY-MM-DD）
            return_date: 返程日期（可选）

        Returns:
            航班列表
        """
        params = {
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": date,
            "type": "1"  # 往返或单程
        }

        if return_date:
            params["return_date"] = return_date
        else:
            params["type"] = "2"  # 单程

        result = self._make_request("google_flights", params)

        if not result.get("success"):
            return {"success": False, "error": result.get("error")}

        data = result["data"]
        best_flights = data.get("best_flights", [])
        other_flights = data.get("other_flights", [])

        flights = []
        all_flights = best_flights + other_flights

        for flight in all_flights[:20]:
            # 获取价格
            price = 0
            if isinstance(flight, dict) and "price" in flight:
                price = flight["price"]

            # 获取航班信息
            if "flights" in flight and flight["flights"]:
                flight_info = flight["flights"][0]
                airline = flight_info.get("airline", "")
                flight_number = flight_info.get("flight_number", "")
                departure_airport = flight_info.get("departure_airport", {}).get("name", "")
                arrival_airport = flight_info.get("arrival_airport", {}).get("name", "")
                departure_time = flight_info.get("departure_airport", {}).get("time", "")
                arrival_time = flight_info.get("arrival_airport", {}).get("time", "")
                duration = flight_info.get("duration", "")

                flights.append({
                    "airline": airline,
                    "flight_number": flight_number,
                    "departure_airport": departure_airport,
                    "arrival_airport": arrival_airport,
                    "departure_time": departure_time,
                    "arrival_time": arrival_time,
                    "duration": duration,
                    "price": price
                })

        return {
            "success": True,
            "flights": flights,
            "count": len(flights)
        }

    def get_place_details(
        self,
        place_id: str,
        fields: Optional[List[str]] = None
    ) -> Dict:
        """
        获取地点详情

        Args:
            place_id: Google Place ID
            fields: 需要返回的字段列表

        Returns:
            地点详细信息
        """
        # SerpAPI 可能不支持直接获取place_id详情
        # 这里提供一个搜索替代方案
        params = {
            "q": place_id,
            "google_domain": "google.com",
            "num": 1
        }

        result = self._make_request("google", params)
        return result

    def estimate_flight_cost(
        self,
        origin: str,
        destination: str
    ) -> Dict:
        """
        估算国际机票价格（基于历史数据）

        Args:
            origin: 出发国家/城市
            destination: 目的地国家/城市

        Returns:
            价格估算
        """
        # 常见航线价格估算（人民币）
        flight_price_map = {
            ("中国", "日本"): 2500,
            ("中国", "韩国"): 2200,
            ("中国", "泰国"): 3000,
            ("中国", "新加坡"): 3500,
            ("中国", "马来西亚"): 3200,
            ("中国", "越南"): 2800,
            ("中国", "法国"): 6000,
            ("中国", "英国"): 6500,
            ("中国", "意大利"): 5800,
            ("中国", "美国"): 8000,
            ("中国", "澳大利亚"): 7000,
            ("中国", "新西兰"): 8500,
        }

        price = flight_price_map.get((origin, destination))

        if not price:
            # 默认估算
            if destination in ["日本", "韩国", "泰国", "新加坡", "马来西亚", "越南"]:
                price = 3000  # 亚洲
            elif destination in ["法国", "英国", "意大利", "德国"]:
                price = 6000  # 欧洲
            elif destination in ["美国", "加拿大"]:
                price = 8000  # 北美
            elif destination in ["澳大利亚", "新西兰"]:
                price = 7500  # 大洋洲
            else:
                price = 5000  # 其他

        # 价格范围（淡季/旺季）
        price_estimate = {
            "economy_low": int(price * 0.7),   # 淡季
            "economy_avg": price,               # 平均
            "economy_high": int(price * 1.3),   # 旺季
            "business_avg": int(price * 2.5),   # 商务舱
            "first_avg": int(price * 4.5),      # 头等舱
        }

        return {
            "success": True,
            "type": "flight",
            "origin": origin,
            "destination": destination,
            "price_estimate": price_estimate
        }


# 使用示例
if __name__ == "__main__":
    client = SerpAPIClient()

    # 测试景点搜索
    print("=== 搜索东京景点 ===")
    attractions = client.search_attractions(
        "tourist attractions in Tokyo",
        "Tokyo, Japan",
        5
    )
    if attractions["success"]:
        for attr in attractions["attractions"][:3]:
            print(f"  - {attr['name']}: {attr.get('rating', 0)} stars")
    else:
        print(f"  Error: {attractions['error']}")

    # 测试机票费用估算
    print("\n=== 估算中国到日本的机票费用 ===")
    cost = client.estimate_flight_cost("中国", "日本")
    if cost["success"]:
        print(f"  经济舱平均: {cost['price_estimate']['economy_avg']}元")
        print(f"  经济舱淡季: {cost['price_estimate']['economy_low']}元")
        print(f"  经济舱旺季: {cost['price_estimate']['economy_high']}元")
