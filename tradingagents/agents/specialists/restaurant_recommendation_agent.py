"""
餐厅推荐智能体

专门负责推荐具体的、真实的餐厅信息
"""

from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any
import json


def get_restaurant_recommendation_prompt() -> str:
    """返回餐厅推荐的系统提示词"""
    return """你是一位资深的美食家，对各地餐厅了如指掌。

你的任务是为游客推荐具体的、真实的、值得去的餐厅。

重要要求：
1. **真实餐厅**：必须推荐真实存在的餐厅，不要编造
2. **具体信息**：提供餐厅名称、具体地址、招牌菜品
3. **准确价格**：提供合理的人均消费价格
4. **实用建议**：提供是否需要预订、排队情况、必点菜品

输入信息：
- city: 所在城市
- meal_type: 餐饮类型 (lunch/dinner)
- meal_time: 用餐时间
- area: 附近区域/景点
- day: 第几天

输出格式（严格遵循JSON格式）：
{
    "restaurant_name": "具体餐厅名称",
    "address": "餐厅具体地址",
    "location_description": "位置描述，如：位于XX景点步行5分钟",
    "cuisine_type": "菜系类型",
    "average_cost": 80,
    "signature_dishes": [
        {
            "name": "招牌菜1",
            "price": 68,
            "description": "菜品特色描述"
        },
        {
            "name": "招牌菜2",
            "price": 48,
            "description": "菜品特色描述"
        }
    ],
    "recommendation_reason": "推荐理由",
    "booking_required": false,
    "booking_info": "如需预订：提前1天预约或排队约30分钟",
    "peak_hours": "11:30-13:00 需排队或提前预约",
    "tips": [
        "用餐贴士1",
        "用餐贴士2"
    ]
}

参考示例：
对于北京故宫附近的午餐，不要只说"当地特色美食"，
而要说："推荐：四季民福烤鸭店(王府井店)，地址：王府井大街301号，人均¥120。招牌菜：精品烤鸭¥168（现片现上）、鸭汤¥28（清淡滋补）、鸭肝¥38（入口即化）。推荐理由：百年老字号，烤鸭工艺正宗，距故宫步行15分钟。需提前预约或排队约30分钟。"
"""


def create_restaurant_recommendation_agent(llm):
    """创建餐厅推荐智能体"""

    def recommend_restaurant(state: Dict[str, Any]) -> Dict[str, Any]:
        """推荐餐厅"""
        city = state.get("city", "")
        meal_type = state.get("meal_type", "lunch")
        meal_time = state.get("meal_time", "12:00-13:30")
        area = state.get("area", "")
        day = state.get("day", 1)

        prompt = ChatPromptTemplate.from_messages([
            ("system", get_restaurant_recommendation_prompt()),
            ("human", """请为以下用餐需求推荐餐厅：

所在城市: {city}
餐饮类型: {meal_type}
用餐时间: {meal_time}
附近区域: {area}

请推荐真实存在的、具体的餐厅，包含餐厅名称、地址、招牌菜品。""")
        ])

        messages = prompt.format_messages(
            city=city,
            meal_type=meal_type,
            meal_time=meal_time,
            area=area,
            day=day
        )

        try:
            response = llm.invoke(messages)
            content = response.content

            # 解析JSON响应
            if isinstance(content, str):
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    restaurant_data = json.loads(json_str)
                else:
                    # 创建基本数据
                    restaurant_data = {
                        "restaurant_name": f"{area}特色餐厅",
                        "address": f"{city}{area}附近",
                        "location_description": f"位于{area}周边",
                        "cuisine_type": "当地特色",
                        "average_cost": 80,
                        "signature_dishes": [
                            {
                                "name": f"{city}特色菜",
                                "price": 68,
                                "description": "当地特色风味"
                            },
                            {
                                "name": "时令蔬菜",
                                "price": 38,
                                "description": "新鲜时蔬"
                            }
                        ],
                        "recommendation_reason": f"品尝{city}地道美食",
                        "booking_required": False,
                        "tips": ["建议提前到达", "可尝试当地特色"]
                    }
            else:
                restaurant_data = content

            return {
                **state,
                f"restaurant_{day}_{meal_type}": restaurant_data,
                "current_step": f"restaurant_recommended_{day}_{meal_type}"
            }

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"餐厅推荐失败: {e}")

            return {
                **state,
                f"restaurant_{day}_{meal_type}": {
                    "restaurant_name": f"{area}附近特色餐厅",
                    "address": f"{city}{area}",
                    "average_cost": 80,
                    "signature_dishes": [
                        {"name": "当地特色菜", "price": 60, "description": "特色"}
                    ],
                    "tips": ["建议提前到达"]
                }
            }

    return recommend_restaurant
