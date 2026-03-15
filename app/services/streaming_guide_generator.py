"""
流式详细攻略生成服务

逐步返回每个智能体的生成结果，提供实时进度反馈
"""

from typing import Dict, Any, List, AsyncIterator
import logging
import asyncio
import json

logger = logging.getLogger(__name__)


class StreamingGuideGenerator:
    """流式攻略生成器"""

    def __init__(self, llm=None):
        self.llm = llm

    async def generate_detailed_guide_stream(self, basic_guide: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """
        流式生成详细攻略，逐步返回每个智能体的生成结果

        返回格式：
        {
            "type": "progress" | "step_result" | "complete",
            "step": "步骤名称",
            "day": 第几天,
            "progress": 进度百分比,
            "data": 步骤结果数据
        }
        """

        destination = basic_guide.get("destination", "")
        days = basic_guide.get("total_days", 5)
        daily_itinerary = basic_guide.get("daily_itineraries", [])

        total_steps = len(daily_itinerary) * 3  # 每天约3个主要步骤
        current_step = 0

        # 1. 开始阶段
        yield {
            "type": "progress",
            "step": "开始生成详细攻略",
            "progress": 5,
            "message": f"正在为 {destination} 生成详细攻略..."
        }

        await asyncio.sleep(0.5)

        # 逐天生成
        for day_idx, day_info in enumerate(daily_itinerary):
            day_number = day_info.get("day", day_idx + 1)

            # 2. 开始第N天
            yield {
                "type": "progress",
                "step": f"第{day_number}天攻略生成",
                "day": day_number,
                "progress": 5 + (day_idx * 80 // total_steps),
                "message": f"正在生成第{day_number}天详细攻略..."
            }

            await asyncio.sleep(0.3)

            schedule = day_info.get("schedule", [])

            # 如果没有schedule，从旧格式提取
            if not schedule:
                schedule = self._extract_schedule_from_old_format(day_info)

            # 处理当天每个活动
            for item_idx, item in enumerate(schedule):
                period = item.get("period", "")

                # 生成详细内容
                if period in ["lunch", "dinner"]:
                    # 用餐 - 生成餐厅推荐
                    yield {
                        "type": "progress",
                        "step": f"第{day_number}天{period}推荐餐厅",
                        "day": day_number,
                        "period": period,
                        "progress": 5 + ((day_idx * 3 + item_idx) * 80 // total_steps),
                        "message": f"正在推荐第{day_number}天{period}餐厅..."
                    }

                    await asyncio.sleep(0.2)

                    restaurant_data = await self._generate_restaurant_recommendation(
                        destination,
                        day_number,
                        period,
                        item
                    )

                    yield {
                        "type": "step_result",
                        "step": f"第{day_number}天{period}餐厅推荐",
                        "day": day_number,
                        "period": period,
                        "data": restaurant_data,
                        "summary": f"推荐餐厅：{restaurant_data.get('restaurant_name', '当地特色餐厅')}"
                    }

                elif period in ["morning", "afternoon", "evening"]:
                    # 游览 - 生成景点详情
                    activity = item.get("activity", "")
                    if activity and activity not in ["待定"]:
                        yield {
                            "type": "progress",
                            "step": f"第{day_number}天{activity}详情",
                            "day": day_number,
                            "progress": 5 + ((day_idx * 3 + item_idx) * 80 // total_steps),
                            "message": f"正在生成{activity}的详细攻略..."
                        }

                        await asyncio.sleep(0.2)

                        attraction_data = await self._generate_attraction_details(
                            destination,
                            day_number,
                            item
                        )

                        yield {
                            "type": "step_result",
                            "step": f"第{day_number}天{activity}详细攻略",
                            "day": day_number,
                            "activity": activity,
                            "data": attraction_data,
                            "summary": f"{attraction_data.get('description', '')[:50]}..."
                        }

        # 3. 完成
        yield {
            "type": "progress",
            "step": "攻略生成完成",
            "progress": 100,
            "message": "详细攻略已全部生成完成！"
        }

        yield {
            "type": "complete",
            "message": "攻略生成完成，即将显示..."
        }

    async def _generate_attraction_details(self, destination: str, day: int, item: Dict) -> Dict:
        """生成景点详情"""

        activity = item.get("activity", "")
        location = item.get("location", activity)

        # 这里应该调用专门的智能体，暂时返回模拟数据
        return {
            "name": location,
            "description": f"{location}是{destination}的著名景点，拥有丰富的历史文化和独特的建筑风格。建议游览时间2-3小时，仔细品味其文化魅力。",
            "highlights": [
                f"欣赏{location}的独特建筑风格",
                f"了解{location}的历史文化背景",
                f"体验{location}的游览氛围"
            ],
            "tickets": {
                "price": 60,
                "notes": "建议提前在官方平台预约，学生可享优惠"
            },
            "tips": [
                "穿着舒适的鞋子便于步行",
                "携带饮用水保持水分",
                "注意保护环境"
            ]
        }

    async def _generate_restaurant_recommendation(self, destination: str, day: int, meal_type: str, item: Dict) -> Dict:
        """生成餐厅推荐"""

        location = item.get("location", "")

        # 这里应该调用专门的智能体，暂时返回模拟数据
        restaurant_names = {
            "lunch": ["特色餐厅", "老字号餐厅"],
            "dinner": ["口碑饭店", "特色餐厅"]
        }

        name = restaurant_names.get(meal_type, "当地特色餐厅")[0]

        return {
            "restaurant": f"{location}附近的{name}",
            "address": f"{destination}{location}周边",
            "signature_dishes": [
                {"name": f"{destination}特色菜", "price": 68, "description": "当地特色风味"},
                {"name": "时令蔬菜", "price": 38, "description": "新鲜时蔬"}
            ],
            "average_cost": 80,
            "tips": "建议提前到达或预约"
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
                schedule.append(item)

        return schedule
