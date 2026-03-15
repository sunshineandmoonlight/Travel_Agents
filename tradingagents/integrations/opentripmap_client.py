"""
OpenTripMap API 客户端

获取国际旅游景点数据（完全免费，无需API Key）
文档: https://opentripmap.io
"""

import os
import requests
from typing import Dict, List, Optional


class OpenTripMapClient:
    """OpenTripMap API客户端 - 国际景点数据"""

    BASE_URL = "https://api.opentripmap.com/0.1"

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化客户端

        Args:
            api_key: OpenTripMap API Key（可免费获取）
        """
        # OpenTripMap需要API Key，但可以免费获取
        # 使用用户可能配置的Key或默认测试Key
        self.api_key = api_key or os.getenv("OPENTRIPMAP_API_KEY", "5ae2e3f221c38a28845f05b65ccfb5edab62132003e6277f17873df9")

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        发起API请求

        Args:
            endpoint: API端点
            params: 请求参数

        Returns:
            API响应数据
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        if params is None:
            params = {}

        # 添加API Key
        params["apikey"] = self.api_key

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            # 检查错误
            if isinstance(data, dict) and data.get("status") == "error":
                return {
                    "success": False,
                    "error": data.get("message", "API Error")
                }

            return {"success": True, "data": data}

        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timeout"}
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {"success": False, "error": "Not found"}
            return {"success": False, "error": str(e)}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_attractions_by_radius(
        self,
        lat: float,
        lon: float,
        radius: int = 1000,
        limit: int = 20,
        lang: str = "en"
    ) -> Dict:
        """
        按半径搜索景点（需要经纬度）

        Args:
            lat: 纬度
            lon: 经度
            radius: 搜索半径（米）
            limit: 返回数量限制
            lang: 语言代码

        Returns:
            景点列表
        """
        endpoint = f"/{lang}/places/radius"
        params = {
            "radius": radius,
            "lon": lon,
            "lat": lat,
            "limit": limit,
            "format": "json"
        }

        result = self._make_request(endpoint, params)

        if not result.get("success"):
            return {
                "success": False,
                "error": result.get("error", "Search failed")
            }

        features = result.get("data", [])
        attractions = []

        # 检查响应格式
        if not features:
            logger.warning(f"[OpenTripMap] 无景点数据返回，API响应: {result.get('data', {})}")
            return {
                "success": False,
                "error": "No attractions found in API response",
                "api_response": result.get("data", {})
            }

        for feature in features:
            if not isinstance(feature, dict):
                logger.warning(f"[OpenTripMap] 跳过非字典元素: {type(feature)}")
                continue

            properties = feature.get("properties", {})
            geometry = feature.get("geometry", {})

            # 确保name字段存在
            name = properties.get("name", "")
            if not name:
                # 尝试从其他字段获取名称
                name = properties.get("name_en", "") or properties.get("local_name", "")
                if not name:
                    logger.debug(f"[OpenTripMap] 跳过无名称的景点: {properties.keys()}")
                    continue

            attractions.append({
                "xid": properties.get("xid", ""),
                "name": name,
                "kind": properties.get("kinds", ""),
                "otm": properties.get("otm", ""),
                "wikipedia": properties.get("wikipedia", ""),
                "wikidata": properties.get("wikidata", ""),
                "address": self._extract_address(properties),
                "description": self._extract_description(properties),
                "image": properties.get("image", ""),
                "preview": properties.get("preview", {}),
                "rate": properties.get("rate", ""),
                "distance": properties.get("dist", 0),
                "coordinates": geometry.get("coordinates", [])
            })

        return {
            "success": True,
            "attractions": attractions,
            "count": len(attractions),
            "search_center": {"lat": lat, "lon": lon, "radius": radius}
        }

    def get_attraction_details(self, xid: str, lang: str = "en") -> Dict:
        """
        获取景点详细信息

        Args:
            xid: OpenTripMap景点ID
            lang: 语言代码

        Returns:
            景点详细信息
        """
        endpoint = f"/{lang}/places/xid/{xid}"

        result = self._make_request(endpoint)

        if not result.get("success"):
            return {
                "success": False,
                "error": result.get("error", "Failed to get details")
            }

        data = result.get("data", {})
        properties = data.get("properties", {})
        geometry = data.get("geometry", {})

        return {
            "success": True,
            "xid": xid,
            "name": properties.get("name", ""),
            "kind": properties.get("kinds", ""),
            "otm": properties.get("otm", ""),
            "wikipedia": properties.get("wikipedia", ""),
            "wikidata": properties.get("wikidata", ""),
            "address": self._extract_address(properties),
            "description": properties.get("wikipedia_extracts", {}).get("text", ""),
            "image": properties.get("image", ""),
            "preview": properties.get("preview", {}),
            "rate": properties.get("rate", ""),
            "url": properties.get("url", ""),
            "phone": properties.get("contact", {}).get("phone", ""),
            "email": properties.get("contact", {}).get("email", ""),
            "website": properties.get("contact", {}).get("website", ""),
            "opening_hours": properties.get("opening_hours", ""),
            "reviews": properties.get("reviews", {}),
            "coordinates": geometry.get("coordinates", []),
            "geometry": geometry
        }

    def search_attractions_by_name(
        self,
        city_name: str,
        limit: int = 20,
        lang: str = "en"
    ) -> Dict:
        """
        按城市名称搜索景点

        Args:
            city_name: 城市名称
            limit: 返回数量限制
            lang: 语言代码

        Returns:
            景点列表
        """
        # 首先获取城市的经纬度
        geo_result = self.get_city_coordinates(city_name)

        if not geo_result.get("success"):
            return {
                "success": False,
                "error": f"City not found: {city_name}"
            }

        lat = geo_result.get("lat")
        lon = geo_result.get("lon")

        # 然后按半径搜索景点
        return self.search_attractions_by_radius(lat, lon, radius=10000, limit=limit, lang=lang)

    def get_city_coordinates(self, city_name: str) -> Dict:
        """
        获取城市经纬度

        Args:
            city_name: 城市名称

        Returns:
            经纬度信息
        """
        # 使用城市名称映射（主要城市）
        city_coords = {
            # 亚洲
            "Tokyo": (35.6762, 139.6503),
            "Osaka": (34.6937, 135.5023),
            "Kyoto": (35.0116, 135.7681),
            "Seoul": (37.5665, 126.9780),
            "Busan": (35.1796, 129.0756),
            "Beijing": (39.9042, 116.4074),
            "Shanghai": (31.2304, 121.4737),
            "Hong Kong": (22.3193, 114.1694),
            "Taipei": (25.0330, 121.5654),
            "Bangkok": (13.7563, 100.5018),
            "Phuket": (7.8804, 98.3925),
            "Singapore": (1.3521, 103.8198),
            "Kuala Lumpur": (3.1390, 101.6869),
            "Jakarta": (-6.2088, 106.8456),
            "Bali": (-8.3405, 115.0920),
            "Manila": (14.5995, 120.9842),
            "Ho Chi Minh City": (10.8231, 106.6297),
            "Hanoi": (21.0285, 105.8542),
            "Vientiane": (17.9757, 102.6331),
            "Phnom Penh": (11.5564, 104.9282),
            "Yangon": (16.8661, 96.1951),
            "Delhi": (28.6139, 77.2090),
            "Mumbai": (19.0760, 72.8777),
            "Kathmandu": (27.7172, 85.3239),
            # 欧洲
            "London": (51.5074, -0.1278),
            "Paris": (48.8566, 2.3522),
            "Rome": (41.9028, 12.4964),
            "Barcelona": (41.3851, 2.1734),
            "Amsterdam": (52.3676, 4.9041),
            "Berlin": (52.5200, 13.4050),
            "Vienna": (48.2082, 16.3738),
            "Prague": (50.0755, 14.4378),
            "Budapest": (47.4979, 19.0402),
            "Athens": (37.9838, 23.7275),
            "Lisbon": (38.7223, -9.1393),
            "Madrid": (40.4168, -3.7038),
            # 北美
            "New York": (40.7128, -74.0060),
            "Los Angeles": (34.0522, -118.2437),
            "Chicago": (41.8781, -87.6298),
            "San Francisco": (37.7749, -122.4194),
            "Toronto": (43.6532, -79.3832),
            "Vancouver": (49.2827, -123.1207),
            "Miami": (25.7617, -80.1918),
            "Las Vegas": (36.1699, -115.1398),
            # 大洋洲
            "Sydney": (-33.8688, 151.2093),
            "Melbourne": (-37.8136, 144.9631),
            "Brisbane": (-27.4698, 153.0251),
            "Auckland": (-36.8485, 174.7633),
            "Queenstown": (-45.0312, 168.6626),
            # 中东
            "Dubai": (25.2048, 55.2708),
            "Abu Dhabi": (24.4539, 54.3773),
            "Doha": (25.2854, 51.5310),
            # 非洲
            "Cairo": (30.0444, 31.2357),
            "Cape Town": (-33.9249, 18.4241),
            "Marrakech": (31.6295, -7.9811),
        }

        # 标准化城市名称
        coords = city_coords.get(city_name)
        if coords:
            return {
                "success": True,
                "city": city_name,
                "lat": coords[0],
                "lon": coords[1]
            }

        # 如果没有预置，尝试使用geonames API（如果有）
        # 这里简化处理，返回错误
        return {
            "success": False,
            "error": f"City coordinates not found for: {city_name}"
        }

    def search_by_type(
        self,
        city_name: str,
        attraction_type: str,
        limit: int = 10,
        lang: str = "en"
    ) -> Dict:
        """
        按类型搜索景点

        Args:
            city_name: 城市名称
            attraction_type: 景点类型（如 'historic', 'museums', 'religious', 'natural'）
            limit: 返回数量限制
            lang: 语言代码

        Returns:
            景点列表
        """
        # 首先获取城市坐标
        geo_result = self.get_city_coordinates(city_name)

        if not geo_result.get("success"):
            return {
                "success": False,
                "error": f"City not found: {city_name}"
            }

        lat = geo_result.get("lat")
        lon = geo_result.get("lon")

        # 按类型筛选
        endpoint = f"/{lang}/places/radius"
        params = {
            "radius": 10000,
            "lon": lon,
            "lat": lat,
            "limit": limit * 2,  # 获取更多然后筛选
            "format": "json",
            "kinds": attraction_type
        }

        result = self._make_request(endpoint, params)

        if not result.get("success"):
            return result

        features = result.get("data", [])
        attractions = []

        for feature in features[:limit]:
            properties = feature.get("properties", {})
            geometry = feature.get("geometry", {})

            attractions.append({
                "xid": properties.get("xid", ""),
                "name": properties.get("name", ""),
                "kind": properties.get("kinds", ""),
                "address": self._extract_address(properties),
                "description": self._extract_description(properties),
                "image": properties.get("image", ""),
                "distance": properties.get("dist", 0),
                "coordinates": geometry.get("coordinates", [])
            })

        return {
            "success": True,
            "city": city_name,
            "type": attraction_type,
            "attractions": attractions,
            "count": len(attractions)
        }

    def get_attraction_types(self) -> Dict:
        """
        获取支持的景点类型

        Returns:
            类型列表和说明
        """
        attraction_types = {
            "historic": "历史古迹",
            "museums": "博物馆",
            "religious": "宗教场所",
            "natural": "自然景观",
            "amusements": "娱乐场所",
            "sport": "体育设施",
            "shopping": "购物中心",
            "architecture": "建筑",
            "other": "其他"
        }

        return {
            "success": True,
            "types": attraction_types,
            "count": len(attraction_types)
        }

    def _extract_address(self, properties: Dict) -> str:
        """提取地址信息"""
        parts = []
        if properties.get("postcode"):
            parts.append(properties["postcode"])
        if properties.get("city"):
            parts.append(properties["city"])
        if properties.get("country"):
            parts.append(properties["country"])
        return ", ".join(parts) if parts else properties.get("address", "")

    def _extract_description(self, properties: Dict) -> str:
        """提取描述信息"""
        # 优先使用Wikipedia摘要
        wiki = properties.get("wikipedia_extracts", {})
        if wiki and wiki.get("text"):
            return wiki["text"]

        # 其次使用preview
        preview = properties.get("preview", {})
        if preview and preview.get("text"):
            return preview["text"]

        return ""


# 城市到经纬度的映射（扩展版）
CITY_COORDINATES = {
    # 亚洲 - 日本
    "Tokyo": (35.6762, 139.6503),
    "Osaka": (34.6937, 135.5023),
    "Kyoto": (35.0116, 135.7681),
    "Nara": (34.6851, 135.8048),
    "Hiroshima": (34.3853, 132.4553),
    "Fukuoka": (33.5904, 130.4017),
    "Sapporo": (43.0642, 141.3469),
    # 亚洲 - 韩国
    "Seoul": (37.5665, 126.9780),
    "Busan": (35.1796, 129.0756),
    "Jeju": (33.4996, 126.5312),
    # 亚洲 - 泰国
    "Bangkok": (13.7563, 100.5018),
    "Phuket": (7.8804, 98.3925),
    "Chiang Mai": (18.7883, 98.9853),
    "Pattaya": (12.9236, 100.8825),
    # 亚洲 - 新加坡/马来西亚
    "Singapore": (1.3521, 103.8198),
    "Kuala Lumpur": (3.1390, 101.6869),
    "Penang": (5.4141, 100.3288),
    "Malacca": (2.1896, 102.2501),
    # 亚洲 - 越南/柬埔寨/老挝
    "Ho Chi Minh City": (10.8231, 106.6297),
    "Hanoi": (21.0285, 105.8542),
    "Da Nang": (16.0544, 108.2022),
    "Siem Reap": (13.3618, 103.8606),
    "Phnom Penh": (11.5564, 104.9282),
    "Vientiane": (17.9757, 102.6331),
    "Luang Prabang": (19.8563, 102.1350),
    # 亚洲 - 印尼/菲律宾
    "Jakarta": (-6.2088, 106.8456),
    "Bali": (-8.3405, 115.0920),
    "Yogyakarta": (-7.7956, 110.3695),
    "Manila": (14.5995, 120.9842),
    "Cebu": (10.3157, 123.8854),
    # 亚洲 - 印度/尼泊尔
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Agra": (27.1751, 78.0421),
    "Jaipur": (26.9124, 75.7873),
    "Kathmandu": (27.7172, 85.3239),
    "Pokhara": (28.2096, 83.9856),
    # 欧洲 - 英国
    "London": (51.5074, -0.1278),
    "Edinburgh": (55.9533, -3.1883),
    "Manchester": (53.4808, -2.2426),
    # 欧洲 - 法国
    "Paris": (48.8566, 2.3522),
    "Nice": (43.7102, 7.2620),
    "Lyon": (45.7640, 4.8357),
    # 欧洲 - 意大利
    "Rome": (41.9028, 12.4964),
    "Venice": (45.4408, 12.3155),
    "Florence": (43.7696, 11.2558),
    "Milan": (45.4642, 9.1900),
    "Naples": (40.8518, 14.2681),
    # 欧洲 - 西班牙
    "Madrid": (40.4168, -3.7038),
    "Barcelona": (41.3851, 2.1734),
    "Seville": (37.3891, -5.9845),
    "Valencia": (39.4699, -0.3763),
    # 欧洲 - 德国
    "Berlin": (52.5200, 13.4050),
    "Munich": (48.1351, 11.5820),
    "Frankfurt": (50.1109, 8.6821),
    "Hamburg": (53.5511, 9.9937),
    # 欧洲 - 其他
    "Amsterdam": (52.3676, 4.9041),
    "Vienna": (48.2082, 16.3738),
    "Prague": (50.0755, 14.4378),
    "Budapest": (47.4979, 19.0402),
    "Athens": (37.9838, 23.7275),
    "Lisbon": (38.7223, -9.1393),
    "Zurich": (47.3769, 8.5417),
    "Geneva": (46.2044, 6.1432),
    # 北美
    "New York": (40.7128, -74.0060),
    "Los Angeles": (34.0522, -118.2437),
    "Chicago": (41.8781, -87.6298),
    "San Francisco": (37.7749, -122.4194),
    "Washington": (38.9072, -77.0369),
    "Boston": (42.3601, -71.0589),
    "Miami": (25.7617, -80.1918),
    "Las Vegas": (36.1699, -115.1398),
    "Toronto": (43.6532, -79.3832),
    "Vancouver": (49.2827, -123.1207),
    "Montreal": (45.5017, -73.5673),
    # 大洋洲
    "Sydney": (-33.8688, 151.2093),
    "Melbourne": (-37.8136, 144.9631),
    "Brisbane": (-27.4698, 153.0251),
    "Gold Coast": (-28.0023, 153.4318),
    "Auckland": (-36.8485, 174.7633),
    "Queenstown": (-45.0312, 168.6626),
    "Wellington": (-41.2924, 174.7787),
    # 中东
    "Dubai": (25.2048, 55.2708),
    "Abu Dhabi": (24.4539, 54.3773),
    "Doha": (25.2854, 51.5310),
    # 非洲
    "Cairo": (30.0444, 31.2357),
    "Cape Town": (-33.9249, 18.4241),
    "Marrakech": (31.6295, -7.9811),
    # 中国
    "Beijing": (39.9042, 116.4074),
    "Shanghai": (31.2304, 121.4737),
    "Hong Kong": (22.3193, 114.1694),
    "Taipei": (25.0330, 121.5654),
}


def get_city_coordinates(city_name: str) -> tuple:
    """获取城市经纬度"""
    return CITY_COORDINATES.get(city_name)


# 使用示例
if __name__ == "__main__":
    client = OpenTripMapClient()

    print("=== 按城市搜索景点 ===")
    result = client.search_attractions_by_name("Paris", limit=5)
    if result.get("success"):
        print(f"找到 {result['count']} 个景点:")
        for attr in result["attractions"][:5]:
            print(f"  - {attr['name']}")
            print(f"    类型: {attr['kind']}")
            print(f"    距离中心: {attr['distance']}米")

    print("\n=== 按类型搜索景点 ===")
    result = client.search_by_type("Rome", "historic", limit=3)
    if result.get("success"):
        print(f"找到 {result['count']} 个历史景点:")
        for attr in result["attractions"]:
            print(f"  - {attr['name']}")
