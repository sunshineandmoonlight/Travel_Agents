"""
详细旅行攻略生成器

采用多智能体逐天、逐项生成详细攻略的策略
"""

from typing import Dict, Any, List
import logging
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DetailedGuideGenerator:
    """详细攻略生成器"""

    def __init__(self, llm=None):
        self.llm = llm

    def generate_detailed_guide(self, basic_guide: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于基础攻略，生成详细的旅行攻略

        策略：逐天、逐项生成详细内容
        """
        destination = basic_guide.get("destination", "")
        days = basic_guide.get("total_days", 5)
        daily_itinerary = basic_guide.get("daily_itinerary", [])

        detailed_guide = {
            "destination": destination,
            "total_days": days,
            "detailed_days": []
        }

        logger.info(f"[详细攻略生成器] 开始为 {destination} 生成 {days} 天详细攻略")

        # 逐天生成详细攻略
        for day_info in daily_itinerary:
            day_number = day_info.get("day", 1)
            logger.info(f"[详细攻略生成器] 正在生成第 {day_number} 天详细攻略...")

            detailed_day = self._generate_detailed_day(
                destination,
                day_number,
                day_info
            )

            detailed_guide["detailed_days"].append(detailed_day)

        # 添加整体建议
        detailed_guide["overall_tips"] = self._generate_overall_tips(
            destination,
            days,
            detailed_guide
        )

        logger.info(f"[详细攻略生成器] 详细攻略生成完成！")

        return detailed_guide

    def _generate_detailed_day(self, destination: str, day_number: int, day_info: Dict) -> Dict[str, Any]:
        """生成单天的详细攻略"""

        # 提取基本信息
        date = day_info.get("date", "")
        theme = day_info.get("theme", f"第{day_number}天精彩旅程")
        pace = day_info.get("pace", "适中")
        estimated_cost = day_info.get("estimated_cost", 300)

        detailed_day = {
            "day": day_number,
            "date": date,
            "theme": theme,
            "pace": pace,
            "estimated_cost": estimated_cost,
            "schedule": []
        }

        # 获取当天的行程安排
        schedule_items = day_info.get("schedule", [])

        # 如果schedule为空，检查morning/afternoon等字段
        if not schedule_items:
            schedule_items = self._extract_schedule_from_old_format(day_info)

        # 逐个活动生成详细信息
        for item in schedule_items:
            detailed_item = self._generate_detailed_item(
                destination,
                day_number,
                item
            )
            detailed_day["schedule"].append(detailed_item)

        # 添加当天的实用信息
        detailed_day["day_tips"] = self._generate_day_tips(destination, day_number)

        return detailed_day

    def _generate_detailed_item(self, destination: str, day: int, item: Dict) -> Dict[str, Any]:
        """生成单个活动的详细信息"""

        time_range = item.get("time_range", "")
        period = item.get("period", "")
        activity = item.get("activity", "")
        location = item.get("location", activity)

        detailed_item = {
            "time_range": time_range,
            "period": period,
            "activity": activity,
            "location": location
        }

        # 根据活动类型生成不同的详细信息
        if period in ["lunch", "dinner"]:
            # 用餐活动 - 生成餐厅详情
            detailed_item.update(self._generate_dining_details(destination, day, item))
        elif period in ["morning", "afternoon", "evening"]:
            # 游览活动 - 生成景点详情
            detailed_item.update(self._generate_attraction_details(destination, day, item))

        return detailed_item

    def _generate_dining_details(self, destination: str, day: int, item: Dict) -> Dict:
        """生成用餐详细信息"""

        meal_type = item.get("period", "lunch")
        time_range = item.get("time_range", "")
        location = item.get("location", "")

        # 基础信息
        dining_details = {
            "type": "dining",
            "time_range": time_range,
            "location": location,
            "recommendations": {}
        }

        # 如果LLM可用，使用LLM生成详细推荐
        if self.llm:
            try:
                from tradingagents.agents.specialists import create_restaurant_recommendation_agent
                agent = create_restaurant_recommendation_agent(self.llm)

                state = {
                    "city": destination,
                    "meal_type": meal_type,
                    "meal_time": time_range,
                    "area": location,
                    "day": day
                }

                result = agent(state)
                restaurant_key = f"restaurant_{day}_{meal_type}"

                if restaurant_key in result:
                    dining_details["recommendations"] = result[restaurant_key]
                    dining_details["has_details"] = True
                    logger.info(f"[详细攻略] 第{day}天{meal_type}餐厅推荐已生成")
                    return dining_details
            except Exception as e:
                logger.warning(f"[详细攻略] LLM生成餐厅推荐失败: {e}，使用默认推荐")

        # 默认推荐（LLM不可用或失败时）
        dining_details["recommendations"] = self._get_default_restaurant(
            destination,
            location,
            meal_type
        )
        dining_details["has_details"] = False

        return dining_details

    def _generate_attraction_details(self, destination: str, day: int, item: Dict) -> Dict:
        """生成景点详细信息"""

        activity = item.get("activity", "")
        location = item.get("location", activity)
        time_range = item.get("time_range", "")

        attraction_details = {
            "type": "attraction",
            "time_range": time_range,
            "activity": activity,
            "location": location,
            "description": "",
            "highlights": [],
            "tips": {}
        }

        # 生成详细描述
        if self.llm:
            try:
                from tradingagents.agents.specialists import create_attraction_detail_agent
                agent = create_attraction_detail_agent(self.llm)

                state = {
                    "attraction_name": location,
                    "city": destination,
                    "day": day,
                    "time_slot": item.get("period", "morning")
                }

                result = agent(state)
                detail_key = f"attraction_detail_{day}_{item.get('period', 'morning')}"

                if detail_key in result:
                    detail = result[detail_key]
                    attraction_details["description"] = detail.get("description", "")
                    attraction_details["highlights"] = detail.get("highlights", [])
                    attraction_details["suggested_route"] = detail.get("suggested_route", "")
                    attraction_details["photography_spots"] = detail.get("photography_spots", [])

                    # 门票信息
                    if "tickets" in detail:
                        attraction_details["tickets"] = detail["tickets"]

                    # 贴士
                    if "tips" in detail:
                        attraction_details["tips"]["notes"] = detail["tips"]

                    logger.info(f"[详细攻略] 第{day}天{location}详情已生成")
                    attraction_details["has_details"] = True
            except Exception as e:
                logger.warning(f"[详细攻略] LLM生成景点详情失败: {e}，使用默认描述")
                attraction_details["description"] = self._get_default_description(destination, location)
                attraction_details["has_details"] = False
        else:
            attraction_details["description"] = self._get_default_description(destination, location)
            attraction_details["has_details"] = False

        # 交通信息（总是尝试生成）
        transport_info = self._get_transport_info(destination, item)
        if transport_info:
            attraction_details["transport"] = transport_info

        return attraction_details

    def _get_transport_info(self, destination: str, item: Dict) -> Dict:
        """获取交通信息"""

        # 如果item中已有transport信息，使用它
        if "transport" in item and item["transport"]:
            return item["transport"]

        # 否则返回默认交通信息
        return {
            "method": "地铁/打车结合",
            "duration": "约40分钟",
            "cost": 30,
            "tips": f"使用导航APP查看从上一地点的最佳路线"
        }

    def _get_default_restaurant(self, destination: str, area: str, meal_type: str) -> Dict:
        """获取默认餐厅推荐"""

        restaurant_names = {
            "lunch": ["特色小吃店", "当地菜馆", "美食广场"],
            "dinner": ["特色餐厅", "口碑饭店", "老字号"]
        }

        names = restaurant_names.get(meal_type, ["当地餐厅"])
        name = names[0] if names else "当地特色餐厅"

        return {
            "restaurant": f"{area}附近的{name}",
            "address": f"{destination}{area}周边",
            "signature_dishes": [
                {"name": f"{destination}特色菜", "price": 68, "description": "当地特色"},
                {"name": "时令蔬菜", "price": 38, "description": "新鲜时蔬"}
            ],
            "average_cost": 80,
            "tips": "建议提前到达或预约"
        }

    def _get_default_description(self, destination: str, location: str) -> str:
        """获取默认景点描述"""

        descriptions = {
            "西湖": "西湖是杭州的标志性景点，以其秀丽的湖光山色和丰富的历史文化闻名于世。苏堤春晓、断桥残雪等西湖十景各具特色。建议沿苏堤漫步，欣赏湖光山色，感受'人间天堂'的美誉。",
            "故宫": "故宫是明清两代的皇家宫殿，是世界上现存规模最大、保存最为完整的木质结构古建筑群。太和殿、乾清宫、御花园等建筑群展现了中国古代皇家建筑的恢弘气势。",
            "颐和园": "颐和园是中国清朝时期的皇家行宫，以昆明湖、万寿山为基址，按照江南园林的风格建造。长廊、佛香阁、石舫等景点各有特色，是皇家园林的杰作。",
            "灵隐寺": "灵隐寺是杭州最早的古刹，距今已有1600多年历史。寺内飞来峰石窟造像精美，天王殿、大雄宝殿庄严肃穆，是佛教文化的重要场所。",
            "宋城": "宋城是杭州的大型文化旅游主题公园，以'给我一天，还你千年'为理念。景区内有宋河东街、宋城千古情表演等，可以体验宋代市井生活。"
        }

        return descriptions.get(location, f"{location}是{destination}的热门景点，拥有独特的历史文化和迷人的自然风光，值得深入游览。建议预留足够时间，慢慢欣赏其魅力。")

    def _generate_day_tips(self, destination: str, day: int) -> Dict:
        """生成当天实用贴士"""

        return {
            "clothing": "建议穿着舒适的步行鞋，根据天气准备合适的衣物",
            "photography": [
                "最佳拍摄时间：上午9-11点，下午3-5点",
                "建议携带充电宝，拍照耗电",
                "注意保护设备，避免碰撞跌落"
            ],
            "notes": [
                "提前查看天气预报，做好相应准备",
                "携带身份证件，部分景点需要登记",
                "保持手机电量，便于导航和支付"
            ]
        }

    def _generate_overall_tips(self, destination: str, days: int, guide: Dict) -> Dict:
        """生成整体实用信息"""

        return {
            "weather_advice": f"出行前请查看{destination}天气预报，准备合适的衣物",
            "packing_list": [
                "身份证件",
                "手机及充电器",
                "舒适的步行鞋",
                "常用药品",
                "防晒用品（如需）",
                "雨具（根据天气）"
            ],
            "emergency_contacts": ["报警：110", "医疗急救：120", "旅游投诉：12301"],
            "payment_methods": "大部分场所支持支付宝/微信支付，建议携带少量现金"
        }

    def _extract_schedule_from_old_format(self, day_info: Dict) -> List[Dict]:
        """从旧格式提取行程安排"""

        schedule = []
        periods = ["morning", "lunch", "afternoon", "dinner", "evening"]

        for period in periods:
            if period in day_info and day_info[period]:
                period_data = day_info[period]

                item = {
                    "period": period,
                    "time_range": period_data.get("time", ""),
                    "activity": period_data.get("activity", ""),
                    "location": period_data.get("attraction", period_data.get("activity", ""))
                }

                # 添加费用信息
                if "estimated_cost" in period_data:
                    item["estimated_cost"] = period_data["estimated_cost"]

                schedule.append(item)

        return schedule


def create_detailed_guide_generator(llm=None) -> DetailedGuideGenerator:
    """创建详细攻略生成器"""
    return DetailedGuideGenerator(llm)
