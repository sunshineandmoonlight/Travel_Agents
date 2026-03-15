"""
旅行数据增强服务

整合高德地图API、天气API等真实数据源，为Group C智能体提供详细数据
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger('travel_agents')


class TravelDataEnrichmentService:
    """旅行数据增强服务"""

    def __init__(self):
        """初始化服务"""
        # 延迟导入，避免循环依赖
        from tradingagents.integrations.amap_client import AmapClient
        from tradingagents.integrations.openmeteo_client import OpenMeteoClient
        from tradingagents.utils.destination_classifier import DestinationClassifier

        self.amap_client = AmapClient()
        self.meteo_client = OpenMeteoClient()
        self.destination_classifier = DestinationClassifier

    def enrich_restaurant_data(
        self,
        city: str,
        cuisine_type: str = "美食",
        budget_level: str = "medium",
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        增强餐厅数据 - 使用高德地图API获取真实餐厅信息

        Args:
            city: 城市名称
            cuisine_type: 菜系类型 (美食、火锅、烤鸭等)
            budget_level: 预算等级
            limit: 返回数量

        Returns:
            {
                "success": bool,
                "restaurants": List[Dict],
                "count": int,
                "source": str
            }
        """
        logger.info(f"[数据增强] 获取{city}的餐厅数据: {cuisine_type}")

        # 先检查是否为国内目的地
        classification = self.destination_classifier.classify(city)
        if classification.get("type") != "domestic":
            return {
                "success": False,
                "restaurants": [],
                "count": 0,
                "source": "not_domestic",
                "message": "国际目的地暂不支持实时餐厅数据"
            }

        # 构建搜索关键词
        search_keywords = self._get_restaurant_keywords(cuisine_type, budget_level)

        # 搜索餐厅
        result = self.amap_client.search_restaurants(
            city=city,
            keyword=search_keywords,
            limit=limit
        )

        if result.get("success"):
            restaurants = result.get("restaurants", [])

            # 增强餐厅信息
            enriched_restaurants = []
            for restaurant in restaurants:
                enriched = self._enrich_single_restaurant(restaurant, budget_level)
                enriched_restaurants.append(enriched)

            logger.info(f"[数据增强] 成功获取{len(enriched_restaurants)}家餐厅信息")

            return {
                "success": True,
                "restaurants": enriched_restaurants,
                "count": len(enriched_restaurants),
                "source": "amap"
            }
        else:
            logger.warning(f"[数据增强] 高德API查询失败: {result.get('error')}")
            return {
                "success": False,
                "restaurants": [],
                "count": 0,
                "source": "amap_error",
                "error": result.get("error")
            }

    def enrich_attraction_data(
        self,
        city: str,
        attraction_type: str = "景点",
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        增强景点数据 - 使用高德地图API获取真实景点信息

        Args:
            city: 城市名称
            attraction_type: 景点类型
            limit: 返回数量

        Returns:
            增强后的景点数据
        """
        logger.info(f"[数据增强] 获取{city}的景点数据")

        classification = self.destination_classifier.classify(city)
        if classification.get("type") != "domestic":
            return {
                "success": False,
                "attractions": [],
                "count": 0,
                "source": "not_domestic"
            }

        # 搜索景点
        result = self.amap_client.search_attractions(
            city=city,
            keyword=attraction_type,
            limit=limit
        )

        if result.get("success"):
            attractions = result.get("attractions", [])

            # 增强景点信息
            enriched_attractions = []
            for attraction in attractions:
                enriched = self._enrich_single_attraction(attraction)
                enriched_attractions.append(enriched)

            logger.info(f"[数据增强] 成功获取{len(enriched_attractions)}个景点信息")

            return {
                "success": True,
                "attractions": enriched_attractions,
                "count": len(enriched_attractions),
                "source": "amap"
            }
        else:
            return {
                "success": False,
                "attractions": [],
                "count": 0,
                "error": result.get("error")
            }

    def get_detailed_weather(
        self,
        city: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        获取详细天气预报

        Args:
            city: 城市名称
            days: 天数

        Returns:
            天气预报数据
        """
        logger.info(f"[数据增强] 获取{city}的{days}天天气预报")

        # 优先使用高德天气（国内）
        classification = self.destination_classifier.classify(city)

        if classification.get("type") == "domestic":
            result = self.amap_client.get_weather(city, days)
            if result.get("success"):
                # 添加来源标识
                result["source"] = "amap"
                return result

        # 备用：使用Open-Meteo（国际或高德失败时）
        result = self.meteo_client.get_weather_forecast(city, days)
        result["source"] = "openmeteo"
        return result

    def get_attraction_image(
        self,
        attraction_name: str,
        city: str
    ) -> str:
        """
        获取景点图片URL

        Args:
            attraction_name: 景点名称
            city: 城市名称

        Returns:
            图片URL
        """
        # 使用新的图片服务（支持多种可靠的图片来源）
        try:
            from tradingagents.services.attraction_image_service import get_attraction_image as get_img
            return get_img(attraction_name, city)
        except Exception as e:
            logger.warning(f"[数据增强] 图片服务调用失败: {e}")
            # 降级方案：使用占位图
            from urllib.parse import quote
            text = quote(f"{attraction_name}")
            return f"https://via.placeholder.com/800x600/0EA5E9/FFFFFF?text={text}"

    def search_nearby_restaurants(
        self,
        attraction_name: str,
        city: str,
        meal_type: str = "午餐",
        budget_level: str = "medium"
    ) -> List[Dict[str, Any]]:
        """
        搜索景点附近的餐厅

        Args:
            attraction_name: 景点名称
            city: 城市
            meal_type: 用餐类型
            budget_level: 预算等级

        Returns:
            附近餐厅列表
        """
        logger.info(f"[数据增强] 搜索{attraction_name}附近的餐厅")

        # 构建搜索关键词
        keywords = f"{attraction_name}附近 美食"

        result = self.amap_client.search_restaurants(
            city=city,
            keyword=keywords,
            limit=5
        )

        if result.get("success"):
            restaurants = result.get("restaurants", [])
            enriched = [self._enrich_single_restaurant(r, budget_level) for r in restaurants]
            return enriched

        return []

    def get_route_info(
        self,
        origin: str,
        destination: str,
        city: str
    ) -> Dict[str, Any]:
        """
        获取路线信息

        Args:
            origin: 起点
            destination: 终点
            city: 城市

        Returns:
            路线信息（距离、时间、费用）
        """
        # 使用高德距离矩阵API
        # 这里简化处理，返回估算数据

        distance_map = {
            ("故宫", "王府井"): {"distance": 2000, "duration": "步行10分钟"},
            ("故宫", "天安门"): {"distance": 500, "duration": "步行5分钟"},
            ("天坛", "故宫"): {"distance": 8000, "duration": "地铁30分钟"},
        }

        key = (origin, destination)
        if key in distance_map:
            return distance_map[key]

        return {
            "distance": 3000,
            "duration": "打车15分钟/地铁25分钟",
            "cost": 25
        }

    # ==================== 私有辅助方法 ====================

    def _get_restaurant_keywords(self, cuisine_type: str, budget_level: str) -> str:
        """获取餐厅搜索关键词"""
        keyword_map = {
            "火锅": "火锅",
            "烤鸭": "烤鸭",
            "小吃": "小吃",
            "美食": "美食",
            "中餐": "中餐",
            "西餐": "西餐",
            "日料": "日料",
            "韩料": "韩料"
        }
        keyword = keyword_map.get(cuisine_type, "美食")

        # 添加价格相关的关键词
        if budget_level == "economy":
            keyword += " 便宜 实惠"
        elif budget_level == "luxury":
            keyword += " 高端 精致"

        return keyword

    def _enrich_single_restaurant(
        self,
        restaurant: Dict,
        budget_level: str
    ) -> Dict[str, Any]:
        """增强单个餐厅信息"""
        name = restaurant.get("name", "")

        # 估算人均消费
        estimated_cost = self._estimate_restaurant_cost(name, budget_level)

        return {
            "name": name,
            "address": restaurant.get("address", ""),
            "phone": restaurant.get("tel", ""),
            "location": restaurant.get("location", {}),
            "type": restaurant.get("type", ""),
            "business_area": restaurant.get("business_area", ""),
            "rating": restaurant.get("rating", 0),
            "estimated_cost": estimated_cost,
            "cost_range": f"{int(estimated_cost * 0.8)}-{int(estimated_cost * 1.2)}元/人",
            "specialties": self._guess_restaurant_specialties(name, restaurant.get("type", "")),
            "opening_hours": "待确认",  # 高德API可能不包含营业时间
            "recommendation_score": self._calculate_restaurant_score(restaurant, budget_level)
        }

    def _enrich_single_attraction(self, attraction: Dict) -> Dict[str, Any]:
        """增强单个景点信息"""
        name = attraction.get("name", "")
        city = attraction.get("city", "")

        return {
            "name": name,
            "address": attraction.get("address", ""),
            "phone": attraction.get("tel", ""),
            "location": attraction.get("location", {}),
            "type": attraction.get("type", ""),
            "poi_id": attraction.get("poi_id", ""),
            "business_area": attraction.get("business_area", ""),
            "image_url": self.get_attraction_image(name, city),
            "ticket_price": self._estimate_ticket_price(name),
            "recommended_duration": self._estimate_visit_duration(name),
            "best_time_to_visit": "上午9-11点，下午2-4点",
            "highlights": self._get_attraction_highlights(name),
            "tips": self._get_attraction_tips(name)
        }

    def _estimate_restaurant_cost(self, name: str, budget_level: str) -> int:
        """估算餐厅人均消费"""
        # 基于餐厅名称的特征识别
        luxury_keywords = ["大酒店", "饭店", "酒楼", "会所", "轩", "府"]
        economy_keywords = ["小吃", "快餐", "面馆", "粥", "店"]

        name_lower = name.lower()

        if any(kw in name for kw in luxury_keywords):
            base_cost = 200
        elif any(kw in name for kw in economy_keywords):
            base_cost = 40
        else:
            base_cost = 100

        # 根据预算等级调整
        multiplier = {"economy": 0.7, "medium": 1.0, "luxury": 1.5}
        return int(base_cost * multiplier.get(budget_level, 1.0))

    def _guess_restaurant_specialties(self, name: str, type_str: str) -> List[str]:
        """猜测餐厅特色菜"""
        specialty_map = {
            "烤鸭": ["北京烤鸭", "鸭卷", "鸭汤"],
            "火锅": ["毛肚", "肥牛", "鸭肠", "虾滑"],
            "涮肉": ["手切羊肉", "糖蒜", "芝麻酱"],
            "炸酱面": ["炸酱面", "拌菜", "腊八蒜"],
            "小吃": ["驴打滚", "艾窝窝", "豌豆黄"],
            "火锅": ["麻辣锅底", "毛肚", "黄喉"],
            "烤鱼": ["烤鱼", "配菜"],
            "小龙虾": ["麻辣小龙虾", "蒜蓉小龙虾"],
        }

        for key, specialties in specialty_map.items():
            if key in name or key in type_str:
                return specialties

        return ["招牌菜"]

    def _calculate_restaurant_score(self, restaurant: Dict, budget_level: str) -> float:
        """计算餐厅推荐分数"""
        score = 0.5  # 基础分数

        # 有评分则使用
        if restaurant.get("rating"):
            score = min(restaurant["rating"] / 5, 1.0)
        else:
            # 没有评分则基于其他因素
            if restaurant.get("tel"):
                score += 0.1  # 有电话信息
            if restaurant.get("address"):
                score += 0.1  # 有详细地址
            if restaurant.get("business_area"):
                score += 0.1  # 在商圈内

        return min(score, 1.0)

    def _estimate_ticket_price(self, attraction_name: str) -> Dict[str, int]:
        """估算门票价格"""
        price_map = {
            "故宫": {"adult": 60, "student": 20},
            "长城": {"adult": 45, "student": 25},
            "颐和园": {"adult": 30, "student": 15},
            "天坛": {"adult": 34, "student": 17},
            "西湖": {"adult": 0, "student": 0},
            "外滩": {"adult": 0, "student": 0},
        }

        for name, prices in price_map.items():
            if name in attraction_name:
                return prices

        return {"adult": 0, "student": 0}  # 默认免费

    def _estimate_visit_duration(self, attraction_name: str) -> str:
        """估算游览时长"""
        duration_map = {
            "故宫": "3-4小时",
            "长城": "4-5小时",
            "颐和园": "3-4小时",
            "天坛": "2-3小时",
            "西湖": "半天",
            "博物馆": "2-3小时",
        }

        for name, duration in duration_map.items():
            if name in attraction_name:
                return duration

        return "2-3小时"

    def _get_attraction_highlights(self, attraction_name: str) -> List[str]:
        """获取景点亮点"""
        highlights_map = {
            "故宫": ["太和殿", "乾清宫", "御花园", "珍宝馆"],
            "长城": ["烽火台", "敌楼", "壮丽景色", "历史文化"],
            "颐和园": ["昆明湖", "万寿山", "佛香阁", "长廊"],
            "天坛": ["祈年殿", "回音壁", "圜丘坛"],
            "西湖": ["断桥残雪", "苏堤春晓", "雷峰塔", "三潭印月"],
        }

        for name, highlights in highlights_map.items():
            if name in attraction_name:
                return highlights

        return ["历史悠久", "风景优美", "值得一游"]

    def _get_attraction_tips(self, attraction_name: str) -> List[str]:
        """获取景点游玩建议"""
        tips_map = {
            "故宫": ["提前网上预约", "穿舒适鞋子", "从午门进入", "周一闭馆"],
            "长城": ["穿运动鞋", "带足够水", "建议坐缆车", "注意安全"],
            "颐和园": ["建议租讲解器", "坐船游湖", "春天最美", "预留半天"],
            "天坛": ["回音壁体验", "早晚人少", "建议联票"],
        }

        for name, tips in tips_map.items():
            if name in attraction_name:
                return tips

        return ["建议提前预约", "注意开放时间", "保管好随身物品"]


# 全局单例
_enrichment_service = None


def get_enrichment_service() -> TravelDataEnrichmentService:
    """获取数据增强服务单例"""
    global _enrichment_service
    if _enrichment_service is None:
        _enrichment_service = TravelDataEnrichmentService()
    return _enrichment_service
