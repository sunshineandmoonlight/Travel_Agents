"""
SerpAPI工具

使用Google Local搜索API获取实时景点数据
"""

import os
import httpx
from typing import List, Dict, Any
import logging

from .base_api_tool import BaseAPITool, APIKeyMissingException, APICallException

logger = logging.getLogger('travel_agents')


class SerpAPITool(BaseAPITool):
    """SerpAPI景点搜索工具

    通过Google Local搜索获取实时景点数据，包括：
    - 景点名称和地址
    - 用户评分和评论数
    - 坐标位置
    - 联系方式
    - 开放时间
    """

    def __init__(self, api_key: str = None, cache_ttl: int = 3600):
        """
        初始化SerpAPI工具

        Args:
            api_key: SerpAPI密钥（默认从环境变量SERPAPI_KEY读取）
            cache_ttl: 缓存有效期（秒）
        """
        super().__init__(
            api_key or os.getenv("SERPAPI_KEY"),
            cache_ttl
        )
        self.base_url = "https://serpapi.com/search"
        self.timeout = 30.0

    async def search_attractions(
        self,
        destination: str,
        keywords: str,
        days: int,
        style: str
    ) -> List[Dict[str, Any]]:
        """
        使用SerpAPI搜索景点

        Args:
            destination: 目的地名称
            keywords: 搜索关键词
            days: 旅行天数
            style: 旅行风格

        Returns:
            景点列表
        """
        if not self._is_available():
            raise APIKeyMissingException("SerpAPI密钥未配置，请设置SERPAPI_KEY环境变量")

        # 根据风格调整搜索关键词
        style_keywords = self._get_style_keywords(style)
        search_query = f"{destination} {keywords} {style_keywords} 景点 旅游"

        cache_key = self._get_cache_key(
            "search",
            destination=destination,
            keywords=search_query
        )

        async def _search():
            params = {
                "engine": "google_local",
                "q": search_query,
                "type": "search",
                "api_key": self.api_key,
                "num": 20,  # 获取更多结果
                "hl": "zh-CN"  # 中文结果
            }

            logger.info(f"[SerpAPI] 搜索: {search_query}")

            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(self.base_url, params=params)
                    response.raise_for_status()
                    data = response.json()

                # 解析结果
                attractions = self._parse_search_results(data)

                logger.info(f"[SerpAPI] 搜索到 {len(attractions)} 个景点")
                return attractions

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise APICallException("SerpAPI密钥无效或已过期")
                elif e.response.status_code == 403:
                    raise APICallException("SerpAPI访问被拒绝，请检查配额")
                else:
                    raise APICallException(f"SerpAPI请求失败: {e}")
            except httpx.RequestError as e:
                raise APICallException(f"SerpAPI网络请求失败: {e}")
            except Exception as e:
                raise APICallException(f"SerpAPI调用异常: {e}")

        return await self._cached_call(cache_key, _search)

    async def get_attraction_details(self, attraction_id: str) -> Dict[str, Any]:
        """
        获取景点详情

        注意: SerpAPI的详细信息需要通过place_id获取，
        这里返回基本信息，实际使用中可能需要调用Google Places API

        Args:
            attraction_id: 景点ID

        Returns:
            景点详情（简化版）
        """
        # SerpAPI在搜索结果中已包含大部分信息
        # 这里返回占位符，实际使用时可以扩展
        return {
            "id": attraction_id,
            "source": "serpapi",
            "note": "详细信息已包含在搜索结果中"
        }

    def _parse_search_results(self, data: Dict) -> List[Dict[str, Any]]:
        """
        解析SerpAPI搜索结果

        Args:
            data: SerpAPI返回的JSON数据

        Returns:
            景点列表
        """
        attractions = []

        if "local_results" not in data:
            logger.warning("[SerpAPI] 响应中没有local_results字段")
            return attractions

        for place in data["local_results"][:15]:  # 取前15个
            try:
                # 提取坐标
                coords = place.get("gps_coordinates", {})
                latitude = coords.get("latitude") if isinstance(coords, dict) else None
                longitude = coords.get("longitude") if isinstance(coords, dict) else None

                # 提取图片
                photos = place.get("photos", [])
                image_url = photos[0] if photos else None

                attraction = {
                    "name": place.get("title", ""),
                    "address": place.get("address", ""),
                    "rating": place.get("rating", 0),
                    "reviews": place.get("reviews", 0),
                    "phone": place.get("phone", ""),
                    "website": place.get("website", ""),
                    "description": place.get("description", ""),
                    "coordinates": {
                        "lat": latitude,
                        "lng": longitude
                    } if latitude and longitude else None,
                    "image": image_url,
                    "types": place.get("type", "").split(", ") if place.get("type") else [],
                    "price_level": place.get("price_level", ""),
                    "hours": place.get("hours", {}),
                    "place_id": place.get("place_id", ""),  # Google Place ID
                    "source": "serpapi"
                }

                attractions.append(attraction)

            except Exception as e:
                logger.warning(f"[SerpAPI] 解析景点数据失败: {e}")
                continue

        return attractions

    def _get_style_keywords(self, style: str) -> str:
        """
        根据风格返回搜索关键词

        Args:
            style: 旅行风格

        Returns:
            搜索关键词字符串
        """
        style_map = {
            "immersive": "博物馆 文化 深度",
            "exploration": "打卡 热门 景点 必去",
            "relaxation": "公园 休闲 轻松 度假",
            "hidden_gem": "小众 冷门 私藏 冷门景点"
        }
        return style_map.get(style, "")

    async def search_restaurants(
        self,
        destination: str,
        area: str = "",
        budget_level: str = "medium",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        搜索餐厅

        Args:
            destination: 目的地
            area: 区域（可选）
            budget_level: 预算等级 (economy/medium/luxury)
            limit: 返回数量限制

        Returns:
            餐厅列表
        """
        if not self._is_available():
            raise APIKeyMissingException("SerpAPI密钥未配置")

        # 构建搜索查询
        area_query = f"{area}" if area else ""
        budget_query = self._get_budget_keywords(budget_level)
        search_query = f"{destination} {area_query} 餐厅 美食 {budget_query}"

        cache_key = self._get_cache_key(
            "restaurant",
            destination=destination,
            area=area,
            budget=budget_level
        )

        async def _search():
            params = {
                "engine": "google_local",
                "q": search_query,
                "type": "search",
                "api_key": self.api_key,
                "num": min(limit, 20),
                "hl": "zh-CN"
            }

            logger.info(f"[SerpAPI] 搜索餐厅: {search_query}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()

            restaurants = self._parse_restaurant_results(data)
            return restaurants

        return await self._cached_call(cache_key, _search)

    def _parse_restaurant_results(self, data: Dict) -> List[Dict[str, Any]]:
        """解析餐厅搜索结果"""
        restaurants = []

        if "local_results" not in data:
            return restaurants

        for place in data["local_results"]:
            restaurant = {
                "name": place.get("title", ""),
                "address": place.get("address", ""),
                "rating": place.get("rating", 0),
                "reviews": place.get("reviews", 0),
                "phone": place.get("phone", ""),
                "price_level": place.get("price_level", ""),
                "coordinates": {
                    "lat": place.get("gps_coordinates", {}).get("latitude"),
                    "lng": place.get("gps_coordinates", {}).get("longitude")
                },
                "source": "serpapi"
            }
            restaurants.append(restaurant)

        return restaurants

    def _get_budget_keywords(self, budget_level: str) -> str:
        """根据预算等级返回搜索关键词"""
        budget_map = {
            "economy": "便宜 实惠 人均50以下",
            "medium": "中档 人均50-150",
            "luxury": "高档 精致 人均150以上"
        }
        return budget_map.get(budget_level, "")
