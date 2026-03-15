"""
高德地图 API 客户端

用于国内旅游数据获取
- 景点搜索 (POI)
- 天气查询
- 路径规划
"""

import os
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


class AmapClient:
    """高德地图API客户端"""

    # API endpoints
    BASE_URL = "https://restapi.amap.com/v3"

    # POI类型代码
    POI_TYPES = {
        "scenic": "风景名胜",      # 景点
        "restaurant": "餐饮服务",  # 餐厅
        "hotel": "住宿服务",       # 酒店
        "shopping": "购物服务",    # 购物
        "transport": "交通设施服务", # 交通
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化客户端

        Args:
            api_key: 高德地图API Key，如不传则从环境变量AMAP_API_KEY读取
        """
        # 默认API密钥（Web服务API Key - 出行类型）
        DEFAULT_API_KEY = "0f52326f698fc89f3bc0941c3bb113ec"
        self.api_key = api_key or os.getenv("AMAP_API_KEY", DEFAULT_API_KEY)

    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """
        发起API请求

        Args:
            endpoint: API端点路径
            params: 请求参数

        Returns:
            API响应数据
        """
        url = f"{self.BASE_URL}/{endpoint}"
        params["key"] = self.api_key

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "1":
                return {"success": True, "data": data}
            else:
                return {
                    "success": False,
                    "error": data.get("info", "Unknown error"),
                    "error_code": data.get("infocode", "unknown")
                }

        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timeout"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_attractions(
        self,
        city: str,
        keyword: str = "景点",
        limit: int = 20
    ) -> Dict:
        """
        搜索景点

        Args:
            city: 城市名称
            keyword: 搜索关键词
            limit: 返回数量限制

        Returns:
            {
                "success": bool,
                "city": str,
                "attractions": List[Dict],
                "count": int
            }
        """
        result = self._make_request("place/text", {
            "keywords": keyword,
            "city": city,
            "types": self.POI_TYPES["scenic"],
            "offset": limit,
            "page": 1
        })

        if not result.get("success"):
            return {
                "success": False,
                "error": result.get("error", "Search failed"),
                "city": city
            }

        data = result["data"]
        pois = data.get("pois", [])

        attractions = []
        for poi in pois:
            # 解析位置（经纬度）
            location = poi.get("location", "")
            if location:
                lon, lat = location.split(",")
                coordinates = {"longitude": float(lon), "latitude": float(lat)}
            else:
                coordinates = {}

            attractions.append({
                "name": poi.get("name", ""),
                "address": poi.get("address", ""),
                "location": coordinates,
                "tel": poi.get("tel", ""),
                "type": poi.get("type", ""),
                "poi_id": poi.get("id", ""),
                "business_area": poi.get("business_area", ""),
            })

        return {
            "success": True,
            "city": city,
            "attractions": attractions,
            "count": len(attractions)
        }

    def get_attraction_detail(self, poi_id: str) -> Dict:
        """
        获取景点详情

        Args:
            poi_id: POI ID

        Returns:
            景点详细信息
        """
        result = self._make_request("place/detail", {
            "id": poi_id
        })

        if not result.get("success"):
            return {
                "success": False,
                "error": result.get("error", "Get detail failed")
            }

        pois = result["data"].get("pois", [])
        if not pois:
            return {"success": False, "error": "POI not found"}

        poi = pois[0]
        return {
            "success": True,
            "name": poi.get("name", ""),
            "address": poi.get("address", ""),
            "tel": poi.get("tel", ""),
            "business_area": poi.get("business_area", ""),
            "type": poi.get("type", ""),
            # 更多字段...
        }

    def get_weather(self, city: str, days: int = 7) -> Dict:
        """
        获取天气预报

        Args:
            city: 城市名称或adcode
            days: 查询天数（1-7天）

        Returns:
            {
                "success": bool,
                "city": str,
                "weather": List[Dict]
            }
        """
        result = self._make_request("weather/weatherInfo", {
            "city": city,
            "extensions": "all"  # 获取预报天气
        })

        if not result.get("success"):
            return {
                "success": False,
                "error": result.get("error", "Weather query failed"),
                "city": city
            }

        data = result["data"]
        forecasts = data.get("forecasts", [])
        if not forecasts:
            return {"success": False, "error": "No weather data", "city": city}

        forecast = forecasts[0]
        casts = forecast.get("casts", [])[:days]

        weather_info = []
        for cast in casts:
            weather_info.append({
                "date": cast.get("date", ""),
                "weather": cast.get("dayweather", ""),
                "night_weather": cast.get("nightweather", ""),
                "temperature": f"{cast.get('nighttemp')}°C-{cast.get('daytemp')}°C",
                "wind": cast.get("daywind", ""),
                "wind_power": cast.get("daypower", ""),
                "week": cast.get("week", "")
            })

        return {
            "success": True,
            "city": city,
            "province": forecast.get("province", ""),
            "city_name": forecast.get("city", ""),
            "weather": weather_info,
            "report_time": data.get("time", "")
        }

    def plan_route(
        self,
        origin: str,
        destination: str,
        strategy: str = "1"
    ) -> Dict:
        """
        路径规划

        Args:
            origin: 起点坐标或地址
            destination: 终点坐标或地址
            strategy: 路径规划策略
                0: 速度优先
                1: 费用优先
                2: 距离优先

        Returns:
            路径规划结果
        """
        # 注意：这需要使用路径规划API，可能需要不同的endpoint
        # 这里提供一个简化版本
        result = self._make_request("dir/walking", {  # 示例：步行路径
            "origin": origin,
            "destination": destination,
            "strategy": strategy
        })

        # 实际应用中可能需要集成驾车、公交、骑行等不同模式的路径规划
        return result

    def search_restaurants(
        self,
        city: str,
        keyword: str = "美食",
        limit: int = 20
    ) -> Dict:
        """
        搜索餐厅

        Args:
            city: 城市名称
            keyword: 搜索关键词
            limit: 返回数量限制

        Returns:
            餐厅列表
        """
        result = self._make_request("place/text", {
            "keywords": keyword,
            "city": city,
            "types": self.POI_TYPES["restaurant"],
            "offset": limit
        })

        if not result.get("success"):
            return {"success": False, "error": result.get("error")}

        pois = result["data"].get("pois", [])
        restaurants = []
        for poi in pois:
            location = poi.get("location", "")
            if location:
                lon, lat = location.split(",")
                coordinates = {"longitude": float(lon), "latitude": float(lat)}
            else:
                coordinates = {}

            restaurants.append({
                "name": poi.get("name", ""),
                "address": poi.get("address", ""),
                "location": coordinates,
                "type": poi.get("type", ""),
                "rating": poi.get("rating", 0),
            })

        return {
            "success": True,
            "restaurants": restaurants,
            "count": len(restaurants)
        }

    def get_distance(
        self,
        origins: str,
        destination: str,
        type: str = "1"
    ) -> Dict:
        """
        获取距离矩阵

        Args:
            origins: 起点坐标（经度,纬度）
            destination: 终点坐标
            type: 距离测量类型
                0: 直线距离
                1: 驾车距离
                3: 步行距离

        Returns:
            距离信息
        """
        result = self._make_request("distance", {
            "origins": origins,
            "destination": destination,
            "type": type
        })

        if not result.get("success"):
            return {"success": False, "error": result.get("error")}

        results = result["data"].get("results", [])
        if not results:
            return {"success": False, "error": "No distance data"}

        return {
            "success": True,
            "distance": results[0].get("distance", ""),  # 米
            "duration": results[0].get("duration", ""),  # 秒
        }

    def estimate_transport_cost(
        self,
        origin: str,
        destination: str,
        transport_type: str = "high_speed_rail"
    ) -> Dict:
        """
        估算交通费用（基于距离的估算）

        Args:
            origin: 出发城市
            destination: 目的地城市
            transport_type: 交通类型

        Returns:
            费用估算
        """
        # 这里使用城市间距离数据库进行估算
        # 实际应用中可以集成真实的高铁/机票API

        # 常见城市距离（公里）
        distance_map = {
            ("北京", "上海"): 1200,
            ("北京", "西安"): 1000,
            ("北京", "成都"): 1800,
            ("北京", "广州"): 1900,
            ("北京", "深圳"): 1950,
            ("北京", "杭州"): 1100,
            ("北京", "南京"): 900,
            ("上海", "杭州"): 180,
            ("上海", "南京"): 300,
            ("上海", "苏州"): 80,
            ("广州", "深圳"): 140,
            ("广州", "珠海"): 120,
            ("成都", "重庆"): 300,
            ("成都", "西安"): 700,
            # 更多城市距离...
        }

        # 尝试获取距离
        distance = distance_map.get((origin, destination))
        if not distance:
            # 如果不在表中，估算一个平均距离
            distance = 800  # 默认800公里

        # 价格估算（每公里单价）
        price_rates = {
            "high_speed_rail": {
                "second_class": 0.4,  # 二等座：约0.4元/公里
                "first_class": 0.65,   # 一等座：约0.65元/公里
                "business": 1.2        # 商务座：约1.2元/公里
            },
            "train": {
                "hard_seat": 0.18,     # 硬座：约0.18元/公里
                "hard_sleeper": 0.35,  # 硬卧：约0.35元/公里
                "soft_sleeper": 0.55   # 软卧：约0.55元/公里
            },
            "flight": {
                "economy": 1.5,        # 经济舱：约1.5元/公里 + 起飞费
                "business": 3.0,       # 商务舱
                "first": 5.0           # 头等舱
            }
        }

        if transport_type not in price_rates:
            return {
                "success": False,
                "error": f"Unknown transport type: {transport_type}"
            }

        rates = price_rates[transport_type]
        price_estimate = {}

        for seat_class, rate in rates.items():
            base_price = distance * rate
            # 添加起步价和机场建设费等
            if transport_type == "flight":
                base_price += 200  # 机场建设费 + 燃油附加费
            # 向下取整到10的倍数
            price_estimate[seat_class] = int(base_price // 10 * 10)

        return {
            "success": True,
            "type": transport_type,
            "distance": distance,
            "origin": origin,
            "destination": destination,
            "price_estimate": price_estimate
        }


# 使用示例
if __name__ == "__main__":
    client = AmapClient()

    # 测试景点搜索
    print("=== 搜索北京景点 ===")
    attractions = client.search_attractions("北京", "故宫", 5)
    if attractions["success"]:
        for attr in attractions["attractions"][:3]:
            print(f"  - {attr['name']}: {attr['address']}")
    else:
        print(f"  Error: {attractions['error']}")

    # 测试天气查询
    print("\n=== 查询北京天气 ===")
    weather = client.get_weather("北京", 3)
    if weather["success"]:
        for day in weather["weather"][:3]:
            print(f"  {day['date']}: {day['weather']} {day['temperature']}")
    else:
        print(f"  Error: {weather['error']}")

    # 测试交通费用估算
    print("\n=== 估算北京到上海的高铁费用 ===")
    cost = client.estimate_transport_cost("北京", "上海", "high_speed_rail")
    if cost["success"]:
        print(f"  距离: {cost['distance']}公里")
        print(f"  二等座: {cost['price_estimate']['second_class']}元")
        print(f"  一等座: {cost['price_estimate']['first_class']}元")
