"""
旅行规划实时工具集

集成外部API，为智能体提供实时数据能力：
- 高德地图：景点搜索、餐厅推荐、路径规划
- Open-Meteo：天气预报
- Unsplash：景点图片
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger('travel_agents')


# ============================================================
# 工具1: 景点搜索工具
# ============================================================

class AttractionSearchTool:
    """景点实时搜索工具（使用高德地图API）"""

    def __init__(self, api_key: str = None):
        from tradingagents.integrations.amap_client import AmapClient
        # 默认API Key或从环境变量读取
        self.client = AmapClient(api_key or os.getenv("AMAP_API_KEY"))

    def search_attractions(
        self,
        city: str,
        keywords: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        搜索城市内的景点

        Args:
            city: 城市名称
            keywords: 搜索关键词（如"博物馆"、"公园"）
            limit: 返回数量限制

        Returns:
            景点列表，每个景点包含：
            - name: 景点名称
            - address: 地址
            - location: {lat, lon}
            - tel: 电话
            - type: 景点类型
        """
        logger.info(f"[景点搜索] 搜索 {city} 的景点...")

        result = self.client.search_attractions(
            city=city,
            keyword=keywords or "景点",
            limit=limit
        )

        if result.get("success") and result.get("attractions"):
            attractions = []
            for poi in result["attractions"][:limit]:
                attractions.append({
                    "name": poi.get("name", ""),
                    "address": poi.get("address", ""),
                    "location": poi.get("location", {}),
                    "tel": poi.get("tel", ""),
                    "type": poi.get("type", ""),
                    "rating": poi.get("rating", 0)
                })
            logger.info(f"[景点搜索] 找到 {len(attractions)} 个景点")
            return attractions
        else:
            logger.warning(f"[景点搜索] 搜索失败: {result.get('error')}")
            return []

    def get_attraction_details(
        self,
        city: str,
        attraction_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取单个景点的详细信息

        Args:
            city: 城市名称
            attraction_name: 景点名称

        Returns:
            景点详细信息
        """
        logger.info(f"[景点搜索] 获取 {attraction_name} 详情...")

        result = self.client.search_attractions(
            city=city,
            keyword=attraction_name,
            limit=1
        )

        if result.get("success") and result.get("attractions"):
            poi = result["attractions"][0]
            return {
                "name": poi.get("name", ""),
                "address": poi.get("address", ""),
                "location": poi.get("location", {}),
                "tel": poi.get("tel", ""),
                "business_area": poi.get("business_area", ""),
                "rating": poi.get("rating", 0),
                "cost": poi.get("cost", "")
            }
        return None


# ============================================================
# 工具2: 餐厅推荐工具
# ============================================================

class RestaurantSearchTool:
    """餐厅实时搜索工具（使用高德地图API）"""

    def __init__(self, api_key: str = None):
        from tradingagents.integrations.amap_client import AmapClient
        self.client = AmapClient(api_key or os.getenv("AMAP_API_KEY"))

    def search_restaurants(
        self,
        city: str,
        area: str = "",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        搜索餐厅

        Args:
            city: 城市名称
            area: 区域名称（如"王府井"、"西湖"）
            limit: 返回数量限制

        Returns:
            餐厅列表
        """
        logger.info(f"[餐厅搜索] 搜索 {city} {area} 的餐厅...")

        search_area = f"{city}{area}" if area else city
        result = self.client.search_restaurants(
            city=search_area,
            limit=limit
        )

        if result.get("success") and result.get("restaurants"):
            restaurants = []
            for poi in result["restaurants"][:limit]:
                restaurants.append({
                    "name": poi.get("name", ""),
                    "address": poi.get("address", ""),
                    "location": poi.get("location", {}),
                    "tel": poi.get("tel", ""),
                    "type": poi.get("type", "餐饮"),
                    "rating": poi.get("rating", 0),
                    "cost": poi.get("cost", "")
                })
            logger.info(f"[餐厅搜索] 找到 {len(restaurants)} 家餐厅")
            return restaurants
        else:
            logger.warning(f"[餐厅搜索] 搜索失败: {result.get('error')}")
            return []

    def get_restaurant_recommendation(
        self,
        city: str,
        meal_type: str = "午餐"
    ) -> Optional[Dict[str, Any]]:
        """
        获取餐厅推荐（根据用餐类型推荐）

        Args:
            city: 城市名称
            meal_type: 用餐类型（午餐、晚餐）

        Returns:
            推荐餐厅信息
        """
        restaurants = self.search_restaurants(city, limit=5)

        if restaurants:
            # 选择评分最高的餐厅
            best = max(restaurants, key=lambda x: x.get("rating", 0))

            # 估算人均消费
            cost_str = best.get("cost", "")
            estimated_cost = 80  # 默认值

            if "元" in cost_str:
                try:
                    estimated_cost = int(cost_str.replace("元", "").strip())
                except:
                    pass

            return {
                "restaurant": best["name"],
                "address": best["address"],
                "rating": best["rating"],
                "average_cost": estimated_cost,
                "meal_type": meal_type
            }

        return None


# ============================================================
# 工具3: 天气预报工具
# ============================================================

class WeatherForecastTool:
    """天气预报工具（使用Open-Meteo API）"""

    def __init__(self):
        from tradingagents.integrations.openmeteo_client import OpenMeteoClient
        self.client = OpenMeteoClient()

    def get_forecast(
        self,
        city: str,
        days: int = 7
    ) -> Optional[Dict[str, Any]]:
        """
        获取天气预报

        Args:
            city: 城市名称
            days: 预报天数

        Returns:
            天气预报数据
        """
        logger.info(f"[天气预报] 获取 {city} 未来{days}天天气...")

        result = self.client.get_weather_forecast(city, days)

        if result.get("success") and result.get("daily"):
            daily = result["daily"]
            forecasts = []

            for i in range(len(daily.get("time", []))):
                time = daily["time"][i] if "time" in daily else ""
                temp_max = daily.get("temperature_2m_max", [])[i] if "temperature_2m_max" in daily else 0
                temp_min = daily.get("temperature_2m_min", [])[i] if "temperature_2m_min" in daily else 0
                weather_code = daily.get("weathercode", [])[i] if "weathercode" in daily else 0
                precipitation = daily.get("precipitation_sum", [])[i] if "precipitation_sum" in daily else 0

                # 解析天气代码
                weather_desc = self._parse_weather_code(weather_code)

                forecasts.append({
                    "date": time,
                    "temp_max": temp_max,
                    "temp_min": temp_min,
                    "weather": weather_desc,
                    "precipitation": precipitation,
                    "temperature_range": f"{temp_min}°C - {temp_max}°C"
                })

            logger.info(f"[天气预报] 获取成功: {len(forecasts)} 天预报")

            return {
                "city": city,
                "forecasts": forecasts,
                "summary": self._generate_summary(forecasts)
            }

        return None

    def _parse_weather_code(self, code: int) -> str:
        """解析天气代码"""
        weather_map = {
            0: "晴朗",
            1: "多云",
            2: "阴天",
            3: "小雨",
            45: "雷雨",
            51: "中雨",
            61: "大雨",
            71: "小雪",
            77: "大雪"
        }
        return weather_map.get(code, "未知")

    def _generate_summary(self, forecasts: List[Dict]) -> str:
        """生成天气摘要"""
        if not forecasts:
            return "暂无天气数据"

        # 统计天气类型
        weather_counts = {}
        for f in forecasts[:3]:  # 前3天
            weather = f["weather"]
            weather_counts[weather] = weather_counts.get(weather, 0) + 1

        # 生成摘要
        parts = []
        if weather_counts.get("晴朗", 0) > 0:
            parts.append(f"晴天{weather_counts['晴朗']}天")
        if weather_counts.get("多云", 0) > 0:
            parts.append(f"多云{weather_counts['多云']}天")
        if "雨" in str(weather_counts):
            rain_days = sum(v for k, v in weather_counts.items() if "雨" in k)
            parts.append(f"雨天{rain_days}天")

        summary = "、".join(parts) if parts else "天气良好"

        avg_temp = sum(f["temp_max"] for f in forecasts[:3]) / 3
        summary += f"，平均气温约{int(avg_temp)}°C"

        return summary


# ============================================================
# 工具4: 图片搜索工具
# ============================================================

class ImageSearchTool:
    """图片搜索工具（使用Unsplash API）"""

    def __init__(self, access_key: str = None):
        from tradingagents.services.unsplash_search_service import UnsplashSearchService
        self.service = UnsplashSearchService(access_key)

    def search_attraction_image(
        self,
        attraction_name: str,
        city: str = ""
    ) -> Optional[str]:
        """
        搜索景点图片

        Args:
            attraction_name: 景点名称
            city: 城市名称（帮助提高准确性）

        Returns:
            图片URL
        """
        logger.info(f"[图片搜索] 搜索 {attraction_name} 的图片...")

        # 构建搜索关键词
        if city:
            query = f"{attraction_name} {city}"
        else:
            query = attraction_name

        result = self.service.search_photos(
            query=query,
            per_page=1,
            orientation="landscape"
        )

        if result and result.get("url"):
            logger.info(f"[图片搜索] 找到图片")
            return result["url"]

        logger.warning(f"[图片搜索] 未找到 {attraction_name} 的图片")
        return None


# ============================================================
# 工具5: 路径规划工具
# ============================================================

class RoutePlanningTool:
    """路径规划工具（使用高德地图API）"""

    def __init__(self, api_key: str = None):
        from tradingagents.integrations.amap_client import AmapClient
        self.client = AmapClient(api_key or os.getenv("AMAP_API_KEY"))

    def plan_route(
        self,
        origin: str,
        destination: str,
        city: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        规划路径

        Args:
            origin: 出发地
            destination: 目的地
            city: 城市（用于限定范围）

        Returns:
            路径规划结果
        """
        logger.info(f"[路径规划] 规划 {origin} -> {destination} 的路径...")

        result = self.client.plan_route(
            origin=origin,
            destination=destination,
            city=city
        )

        if result.get("success") and result.get("route"):
            route = result["route"]
            return {
                "distance": route.get("distance", 0),
                "duration": route.get("duration", 0),
                "distance_text": route.get("distance_text", ""),
                "duration_text": route.get("duration_text", ""),
                "steps": route.get("steps", []),
                "cost": self._estimate_cost(route.get("distance", 0))
            }

        return None

    def _estimate_cost(self, distance_meters: int) -> int:
        """估算交通费用（元）"""
        if distance_meters < 1000:
            return 10  # 步行
        elif distance_meters < 5000:
            return 5   # 公交
        elif distance_meters < 30000:
            return 20  # 地铁/公交
        else:
            return 50  # 出租车/打车


# ============================================================
# 工具6: 目的地搜索工具（实时）
# ============================================================

class DestinationSearchTool:
    """目的地实时搜索工具"""

    def __init__(self, api_key: str = None, serp_api_key: str = None):
        from tradingagents.integrations.amap_client import AmapClient
        from tradingagents.integrations.serpapi_client import SerpAPIClient
        from tradingagents.services.unsplash_search_service import UnsplashSearchService

        self.client = AmapClient(api_key or os.getenv("AMAP_API_KEY"))
        self.serp_client = SerpAPIClient(serp_api_key or os.getenv("SERPAPI_KEY"))
        self.unsplash_service = UnsplashSearchService()

    def search_destinations(
        self,
        keywords: str,
        scope: str = "domestic"
    ) -> List[Dict[str, Any]]:
        """
        实时搜索目的地

        Args:
            keywords: 搜索关键词（如"海滨城市"、"历史名城"）
            scope: 范围（domestic/international）

        Returns:
            目的地列表
        """
        logger.info(f"[目的地搜索] 搜索: {keywords} ({scope})")

        # 如果是国内，使用高德地图搜索
        if scope == "domestic":
            return self._search_domestic_destinations(keywords)
        else:
            # 国际目的地使用预置数据库（暂时）
            return self._get_international_destinations(keywords)

    def _search_domestic_destinations(self, keywords: str) -> List[Dict[str, Any]]:
        """搜索国内目的地"""
        # 基于关键词匹配热门城市
        city_keywords = {
            "海滨": ["三亚", "青岛", "大连", "厦门", "珠海"],
            "历史": ["北京", "西安", "南京", "洛阳", "开封"],
            "美食": ["成都", "广州", "重庆", "长沙", "顺德"],
            "自然": ["张家界", "九寨沟", "桂林", "黄山", "丽江"],
            "现代": ["上海", "深圳", "杭州", "苏州", "青岛"]
        }

        matched_cities = []
        for key, cities in city_keywords.items():
            if key in keywords:
                for city in cities:
                    # 搜索城市信息
                    result = self.client.search_attractions(city, "旅游景点", limit=1)

                    if result.get("success"):
                        matched_cities.append({
                            "destination": city,
                            "type": key,
                            "description": f"{key}特色城市",
                            "image_url": ""  # 可以后续添加图片搜索
                        })

        # 限制返回数量
        return matched_cities[:8] if matched_cities else self._get_default_cities()

    def _get_international_destinations(self, keywords: str) -> List[Dict[str, Any]]:
        """搜索国际目的地（使用SerpAPI实时搜索）"""
        # 国际目的地关键词映射
        keyword_to_search = {
            "海滨": "best beach destinations",
            "海滩": "tropical beach resorts",
            "历史": "historical cities to visit",
            "文化": "cultural heritage sites",
            "美食": "best food cities",
            "购物": "best shopping destinations",
            "自然": "natural wonders",
            "冒险": "adventure travel destinations",
            "浪漫": "romantic getaways",
            "家庭": "family friendly destinations",
            "都市": "best cities to visit",
            "古城": "ancient cities",
            "博物馆": "museum cities",
            "滑雪": "ski resorts",
            "海岛": "island paradises"
        }

        # 找到匹配的英文搜索词
        search_query = None
        for cn_key, en_query in keyword_to_search.items():
            if cn_key in keywords:
                search_query = en_query
                break

        # 如果没有匹配，使用通用搜索
        if not search_query:
            search_query = "top tourist destinations"

        # 构建搜索查询
        query = f"{search_query} in Asia Europe"  # 搜索热门目的地

        logger.info(f"[目的地搜索] SerpAPI搜索: {query}")

        # 使用SerpAPI搜索
        try:
            result = self.serp_client.search_attractions(query, "World", 10)

            if result.get("success") and result.get("attractions"):
                destinations = []

                # 从搜索结果中提取目的地
                for item in result["attractions"][:8]:
                    # 尝试从标题中提取目的地名称
                    title = item.get("name", "")
                    description = item.get("description", "")

                    # 解析目的地名称（简化处理）
                    destination_name = self._extract_destination_name(title, description)

                    if destination_name and len(destination_name) > 1:
                        # 搜索目的地图片
                        image_url = self._get_destination_image(destination_name)

                        destinations.append({
                            "destination": destination_name,
                            "type": self._categorize_destination(title, description),
                            "description": description[:100] if description else f"热门国际旅游目的地",
                            "image_url": image_url,
                            "rating": item.get("rating", 0)
                        })

                # 去重
                seen = set()
                unique_destinations = []
                for dest in destinations:
                    name_key = dest["destination"].lower()
                    if name_key not in seen:
                        seen.add(name_key)
                        unique_destinations.append(dest)

                logger.info(f"[目的地搜索] SerpAPI找到 {len(unique_destinations)} 个国际目的地")
                return unique_destinations[:8]

        except Exception as e:
            logger.warning(f"[目的地搜索] SerpAPI搜索失败: {e}")

        # 如果API失败，使用预置的国际目的地数据库
        return self._get_fallback_international_destinations(keywords)

    def _extract_destination_name(self, title: str, description: str) -> str:
        """从标题或描述中提取目的地名称"""
        # 常见目的地国家/城市列表
        destinations = [
            "Japan", "Tokyo", "Kyoto", "Osaka", "Mount Fuji",
            "Thailand", "Bangkok", "Phuket", "Chiang Mai", "Pattaya",
            "Singapore", "Malaysia", "Kuala Lumpur", "Penang", "Bali",
            "South Korea", "Seoul", "Busan", "Jeju",
            "Vietnam", "Hanoi", "Ho Chi Minh", "Da Nang", "Ha Long Bay",
            "Cambodia", "Angkor Wat", "Siem Reap", "Phnom Penh",
            "Indonesia", "Jakarta", "Bali", "Lombok",
            "Philippines", "Manila", "Cebu", "Boracay",
            "France", "Paris", "Nice", "Lyon", "Provence",
            "Italy", "Rome", "Venice", "Florence", "Milan", "Tuscany",
            "UK", "London", "Edinburgh", "Oxford", "Stonehenge",
            "Spain", "Barcelona", "Madrid", "Seville", "Valencia",
            "Germany", "Berlin", "Munich", "Frankfurt", "Hamburg",
            "Switzerland", "Zurich", "Geneva", "Lucerne", "Interlaken",
            "Greece", "Athens", "Santorini", "Mykonos", "Crete",
            "USA", "New York", "Los Angeles", "San Francisco", "Las Vegas",
            "Australia", "Sydney", "Melbourne", "Brisbane", "Gold Coast",
            "New Zealand", "Auckland", "Queenstown", "Wellington", "Rotorua",
            "India", "Delhi", "Mumbai", "Agra", "Jaipur", "Goa",
            "Nepal", "Kathmandu", "Pokhara",
            "Maldives", "Maldives Islands"
        ]

        text = f"{title} {description}".lower()

        # 查找匹配的目的地
        for dest in destinations:
            if dest.lower() in text:
                return dest

        # 如果没有匹配，尝试提取第一个大写单词
        words = title.split()
        for word in words:
            if word[0].isupper() and len(word) > 2:
                return word

        return title.split()[0] if title else ""

    def _categorize_destination(self, title: str, description: str) -> str:
        """根据标题和描述分类目的地类型"""
        text = f"{title} {description}".lower()

        categories = {
            "海滨": ["beach", "island", "coast", "sea", "ocean", "resort", "bali", "phuket", "maldives"],
            "历史": ["ancient", "historical", "temple", "monument", "heritage", "angkor", "rome", "athens"],
            "都市": ["city", "metropolitan", "urban", "tokyo", "seoul", "bangkok", "singapore", "new york"],
            "自然": ["nature", "mountain", "park", "forest", "waterfall", "mount fuji", "switzerland"],
            "文化": ["culture", "museum", "art", "kyoto", "florence", "paris"],
            "美食": ["food", "cuisine", "gastronomy", "street food"],
            "购物": ["shopping", "mall", "market"]
        }

        for category, keywords in categories.items():
            if any(kw in text for kw in keywords):
                return category

        return "综合"

    def _get_destination_image(self, destination_name: str) -> str:
        """获取目的地图片（使用Unsplash）"""
        try:
            # 常见目的地图片关键词映射
            image_keywords = {
                "tokyo": "tokyo city skyline",
                "paris": "paris eiffel tower",
                "bangkok": "bangkok temple",
                "bali": "bali beach",
                "sydney": "sydney opera house",
                "rome": "rome colosseum",
                "barcelona": "barcelona sagrada familia",
                "dubai": "dubai skyline",
                "singapore": "singapore marina bay",
                "kyoto": "kyoto temple"
            }

            query = image_keywords.get(destination_name.lower(), f"{destination_name} city")

            result = self.unsplash_service.search_photos(query, per_page=1, orientation="landscape")
            if result and result.get("url"):
                return result["url"]
        except Exception as e:
            logger.warning(f"[目的地搜索] 图片获取失败: {e}")

        return ""

    def _get_fallback_international_destinations(self, keywords: str) -> List[Dict[str, Any]]:
        """备用国际目的地数据库（当API失败时使用）"""
        # 根据关键词返回不同的目的地
        fallback_db = {
            "海滨": [
                {"destination": "Bali", "type": "海滨", "description": "印尼巴厘岛，热带天堂，海滩与寺庙", "image_url": ""},
                {"destination": "Phuket", "type": "海滨", "description": "泰国普吉岛，安达曼海明珠", "image_url": ""},
                {"destination": "Maldives", "type": "海滨", "description": "马尔代夫，蜜月胜地，水上屋", "image_url": ""},
                {"destination": "Gold Coast", "type": "海滨", "description": "澳大利亚黄金海岸，冲浪者天堂", "image_url": ""}
            ],
            "历史": [
                {"destination": "Rome", "type": "历史", "description": "意大利罗马，永恒之城，古罗马遗迹", "image_url": ""},
                {"destination": "Athens", "type": "历史", "description": "希腊雅典，西方文明摇篮", "image_url": ""},
                {"destination": "Kyoto", "type": "历史", "description": "日本京都，千年古都，寺庙之城", "image_url": ""},
                {"destination": "Siem Reap", "type": "历史", "description": "柬埔寨暹粒，吴哥窟奇迹", "image_url": ""}
            ],
            "美食": [
                {"destination": "Bangkok", "type": "美食", "description": "泰国曼谷，街头美食天堂", "image_url": ""},
                {"destination": "Osaka", "type": "美食", "description": "日本大阪，天下厨房", "image_url": ""},
                {"destination": "Singapore", "type": "美食", "description": "新加坡，多元美食融合", "image_url": ""},
                {"destination": "Penang", "type": "美食", "description": "马来西亚槟城，东南亚美食之都", "image_url": ""}
            ],
            "都市": [
                {"destination": "Tokyo", "type": "都市", "description": "日本东京，现代与传统交织", "image_url": ""},
                {"destination": "Seoul", "type": "都市", "description": "韩国首尔，韩流之都", "image_url": ""},
                {"destination": "Singapore", "type": "都市", "description": "新加坡，花园城市国家", "image_url": ""},
                {"destination": "Dubai", "type": "都市", "description": "阿联酋迪拜，奢华之都", "image_url": ""}
            ],
            "自然": [
                {"destination": "Switzerland", "type": "自然", "description": "瑞士，阿尔卑斯山脉风光", "image_url": ""},
                {"destination": "New Zealand", "type": "自然", "description": "新西兰，中土世界", "image_url": ""},
                {"destination": "Iceland", "type": "自然", "description": "冰岛，极光与火山之国", "image_url": ""},
                {"destination": "Norway", "type": "自然", "description": "挪威，峡湾国度", "image_url": ""}
            ]
        }

        # 查找匹配的关键词
        for key, destinations in fallback_db.items():
            if key in keywords:
                return destinations

        # 默认返回热门目的地
        return [
            {"destination": "Japan", "type": "综合", "description": "日本，樱花与古寺之国", "image_url": ""},
            {"destination": "Thailand", "type": "综合", "description": "泰国，微笑之国", "image_url": ""},
            {"destination": "Singapore", "type": "综合", "description": "新加坡，花园城市", "image_url": ""},
            {"destination": "France", "type": "综合", "description": "法国，浪漫之都", "image_url": ""}
        ]

    def _get_default_cities(self) -> List[Dict[str, Any]]:
        """获取默认推荐城市"""
        default_cities = ["北京", "上海", "成都", "杭州", "西安", "厦门", "三亚", "青岛"]
        return [
            {
                "destination": city,
                "type": "热门城市",
                "description": "中国热门旅游城市",
                "image_url": ""
            }
            for city in default_cities
        ]


# ============================================================
# 工具工厂函数
# ============================================================

def get_attraction_search_tool() -> AttractionSearchTool:
    """获取景点搜索工具实例"""
    return AttractionSearchTool()

def get_restaurant_search_tool() -> RestaurantSearchTool:
    """获取餐厅搜索工具实例"""
    return RestaurantSearchTool()

def get_weather_forecast_tool() -> WeatherForecastTool:
    """获取天气预报工具实例"""
    return WeatherForecastTool()

def get_image_search_tool() -> ImageSearchTool:
    """获取图片搜索工具实例"""
    return ImageSearchTool()

def get_route_planning_tool() -> RoutePlanningTool:
    """获取路径规划工具实例"""
    return RoutePlanningTool()

def get_transport_tool() -> RoutePlanningTool:
    """获取交通规划工具实例（别名，与路径规划工具相同）"""
    return RoutePlanningTool()

def get_destination_search_tool() -> DestinationSearchTool:
    """获取目的地搜索工具实例"""
    return DestinationSearchTool()


# ============================================================
# 导出所有工具
# ============================================================

__all__ = [
    "AttractionSearchTool",
    "RestaurantSearchTool",
    "WeatherForecastTool",
    "ImageSearchTool",
    "RoutePlanningTool",
    "DestinationSearchTool",
    "get_attraction_search_tool",
    "get_restaurant_search_tool",
    "get_weather_forecast_tool",
    "get_image_search_tool",
    "get_route_planning_tool",
    "get_destination_search_tool",
]
