"""
OpenTripMap工具

使用OpenTripMap API获取景点数据和详细信息
"""

import os
import httpx
from typing import List, Dict, Any, Optional
import logging

from .base_api_tool import BaseAPITool, APIKeyMissingException, APICallException

logger = logging.getLogger('travel_agents')


class OpenTripMapTool(BaseAPITool):
    """OpenTripMap景点工具

    通过OpenTripMap API获取：
    - 目的地坐标
    - 附近景点列表（按类型筛选）
    - 景点详细信息
    - 维基百科描述
    """

    def __init__(self, api_key: str = None, cache_ttl: int = 3600):
        """
        初始化OpenTripMap工具

        Args:
            api_key: OpenTripMap密钥（默认从环境变量OPENTRIPMAP_API_KEY读取）
            cache_ttl: 缓存有效期（秒）
        """
        super().__init__(
            api_key or os.getenv("OPENTRIPMAP_API_KEY"),
            cache_ttl
        )
        self.base_url = "https://api.opentripmap.com/0.1/en"
        self.timeout = 30.0

    async def search_attractions(
        self,
        destination: str,
        keywords: str,
        days: int,
        style: str
    ) -> List[Dict[str, Any]]:
        """
        搜索OpenTripMap景点

        Args:
            destination: 目的地名称
            keywords: 搜索关键词
            days: 旅行天数
            style: 旅行风格

        Returns:
            景点列表
        """
        if not self._is_available():
            logger.warning("[OpenTripMap] API密钥未配置，使用空结果")
            return []

        # 首先获取目的地的坐标
        coords = await self._get_destination_coords(destination)
        if not coords:
            logger.warning(f"[OpenTripMap] 无法获取 {destination} 的坐标")
            return []

        cache_key = self._get_cache_key(
            "search",
            destination=destination,
            keywords=keywords,
            style=style
        )

        async def _search():
            # 根据风格选择景点类型
            kinds = self._get_style_kinds(style)

            # 半径范围 (km)
            radius = min(50, days * 10)  # 根据天数调整搜索范围

            params = {
                "apikey": self.api_key,
                "lon": coords["lng"],
                "lat": coords["lat"],
                "radius": radius * 1000,  # 转换为米
                "kinds": kinds,
                "format": "json",
                "limit": 30
            }

            url = f"{self.base_url}/places/radius"
            logger.info(f"[OpenTripMap] 搜索 {destination} 附近景点，半径: {radius}km")

            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()

                # 解析结果
                attractions = self._parse_radius_results(data)

                logger.info(f"[OpenTripMap] 搜索到 {len(attractions)} 个景点")
                return attractions

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return []  # 没有找到景点
                else:
                    raise APICallException(f"OpenTripMap请求失败: {e}")
            except Exception as e:
                raise APICallException(f"OpenTripMap调用异常: {e}")

        return await self._cached_call(cache_key, _search)

    async def get_attraction_details(self, attraction_id: str) -> Dict[str, Any]:
        """
        获取景点详情

        Args:
            attraction_id: OpenTripMap的xid

        Returns:
            景点详细信息
        """
        if not self._is_available():
            return {}

        cache_key = self._get_cache_key("details", xid=attraction_id)

        async def _get_details():
            url = f"{self.base_url}/places/xid/{attraction_id}"
            params = {
                "apikey": self.api_key
            }

            logger.info(f"[OpenTripMap] 获取景点详情: {attraction_id}")

            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()

                details = {
                    "name": data.get("name", ""),
                    "address": self._extract_address(data),
                    "description": data.get("wikipedia_extracts", {}).get("text", ""),
                    "image": data.get("preview", {}).get("source", ""),
                    "rating": data.get("rate", 0),
                    "url": data.get("otm", ""),
                    "wikipedia": data.get("wikipedia", ""),
                    "source": "opentripmap"
                }

                return details

            except Exception as e:
                logger.warning(f"[OpenTripMap] 获取详情失败: {e}")
                return {}

        return await self._cached_call(cache_key, _get_details)

    async def _get_destination_coords(self, destination: str) -> Optional[Dict]:
        """
        获取目的地坐标

        Args:
            destination: 目的地名称

        Returns:
            {"lat": float, "lng": float} 或 None
        """
        cache_key = self._get_cache_key("geoname", name=destination)

        async def _get_coords():
            url = f"{self.base_url}/places/geoname"
            params = {
                "apikey": self.api_key,
                "name": destination
            }

            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()

                if data.get("features"):
                    coords = data["features"][0]["geometry"]["coordinates"]
                    return {"lat": coords[1], "lng": coords[0]}
            except Exception as e:
                logger.warning(f"[OpenTripMap] 获取坐标失败: {e}")

            return None

        return await self._cached_call(cache_key, _get_coords)

    def _parse_radius_results(self, data: Dict) -> List[Dict[str, Any]]:
        """
        解析半径搜索结果

        Args:
            data: OpenTripMap返回的JSON数据

        Returns:
            景点列表
        """
        attractions = []

        if "features" not in data:
            return attractions

        for place in data["features"][:20]:  # 取前20个
            try:
                properties = place.get("properties", {})
                geometry = place.get("geometry", {})
                coordinates = geometry.get("coordinates", [])

                attraction = {
                    "name": properties.get("name", ""),
                    "xid": properties.get("xid", ""),  # OpenTripMap ID
                    "kinds": properties.get("kinds", ""),
                    "address": self._extract_address_from_properties(properties),
                    "coordinates": {
                        "lat": coordinates[1] if len(coordinates) > 1 else None,
                        "lng": coordinates[0] if len(coordinates) > 0 else None
                    },
                    "wikidata": properties.get("wikidata", ""),
                    "wikipedia": properties.get("wikipedia", ""),
                    "source": "opentripmap"
                }
                attractions.append(attraction)

            except Exception as e:
                logger.warning(f"[OpenTripMap] 解析景点失败: {e}")
                continue

        return attractions

    def _extract_address(self, data: Dict) -> str:
        """从数据中提取地址"""
        # 尝试多种地址字段
        if "address" in data:
            addr = data["address"]
            if isinstance(addr, dict):
                parts = []
                if "road" in addr:
                    parts.append(addr["road"])
                if "city" in addr:
                    parts.append(addr["city"])
                if "country" in addr:
                    parts.append(addr["country"])
                return ", ".join(parts)
            return str(addr)
        return ""

    def _extract_address_from_properties(self, properties: Dict) -> str:
        """从properties中提取地址"""
        addr = properties.get("address", {})
        if isinstance(addr, dict):
            parts = []
            if "road" in addr:
                parts.append(addr["road"])
            if "city" in addr or "town" in addr:
                parts.append(addr.get("city") or addr.get("town", ""))
            if "country" in addr:
                parts.append(addr["country"])
            return ", ".join(parts)
        return str(addr) if addr else ""

    def _get_style_kinds(self, style: str) -> str:
        """
        根据风格返回景点类型

        OpenTripMap的kinds参数说明：
        https://opentripmap.github.io/opentripmap-v1/

        Args:
            style: 旅行风格

        Returns:
            景点类型字符串（逗号分隔）
        """
        kind_map = {
            "immersive": "museums,cultural,churches,historic,monuments",
            "exploration": "tourist_facilities,view_points,nature,amusements",
            "relaxation": "parks,beaches,gardens,natural",
            "hidden_gem": "other,interesting_places,architecture"
        }
        return kind_map.get(style, "")

    async def search_by_name(
        self,
        destination: str,
        attraction_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        按名称搜索景点

        Args:
            destination: 目的地
            attraction_name: 景点名称

        Returns:
            景点信息或None
        """
        if not self._is_available():
            return None

        cache_key = self._get_cache_key(
            "name_search",
            destination=destination,
            name=attraction_name
        )

        async def _search():
            url = f"{self.base_url}/places/geoname"
            params = {
                "apikey": self.api_key,
                "name": f"{destination} {attraction_name}"
            }

            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()

                if data.get("features"):
                    feature = data["features"][0]
                    coords = feature["geometry"]["coordinates"]
                    return {
                        "name": attraction_name,
                        "coordinates": {
                            "lat": coords[1],
                            "lng": coords[0]
                        },
                        "source": "opentripmap"
                    }
            except Exception as e:
                logger.warning(f"[OpenTripMap] 名称搜索失败: {e}")

            return None

        return await self._cached_call(cache_key, _search)
