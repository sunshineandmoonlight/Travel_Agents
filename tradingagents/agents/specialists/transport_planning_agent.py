"""
交通规划智能体

专门负责规划详细的交通路线和方式
"""

from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any
import json


def get_transport_planning_prompt() -> str:
    """返回交通规划的系统提示词"""
    return """你是一位熟悉各地交通的出行规划专家。

你的任务是为游客规划详细、实用、经济的交通路线。

重要要求：
1. **具体路线**：提供具体的交通方式、换乘站点、步行距离
2. **准确时间**：提供准确的行程时间估算
3. **合理费用**：提供真实的交通费用
4. **实用建议**：提供如何省钱、如何避开高峰的建议

输入信息：
- from_location: 出发地点
- to_location: 目的地
- city: 所在城市
- day: 第几天

输出格式（严格遵循JSON格式）：
{
    "recommended_method": "最佳交通方式",
    "alternatives": [
        {
            "method": "地铁",
            "route": "具体路线：起点站 → 换乘站 → 终点站",
            "duration": "约40分钟",
            "cost": 6,
            "walking_distance": "约500米",
            "steps": [
                "从起点步行500米到地铁站",
                "乘坐X号线往Y方向3站",
                "在Z站下车步行5分钟到达"
            ],
            "pros": ["优点1", "优点2"],
            "cons": ["缺点1"]
        },
        {
            "method": "打车/网约车",
            "route": "直达",
            "duration": "约25分钟",
            "cost": 35,
            "walking_distance": 0,
            "steps": ["在路边或用APP叫车"],
            "pros": ["舒适快捷", "点对点直达"],
            "cons": ["费用较高", "可能堵车"]
        }
    ],
    "tips": [
        "交通贴士1：避开早晚高峰(7-9点，17-19点)",
        "交通贴士2：使用支付宝/微信扫码支付",
        "交通贴士3：推荐办理交通卡或使用乘车码"
    ],
    "total_estimated_cost": 6,
    "best_choice": "地铁（经济方便）"
}

参考示例：
对于从"天安门东"到"颐和园"，不要只说"地铁/打车结合"，
而要说："推荐：地铁4号线(西直门换乘)→地铁6号线(北宫门)，约50分钟，¥6。路线：天安门东站→西直门站换乘→北宫门站下车，步行5分钟到颐和园东宫门。备选：打车约35分钟，¥40-50。贴士：避开早高峰(7-9点)，使用"亿通行"APP扫码乘车。"
"""


def create_transport_planning_agent(llm):
    """创建交通规划智能体"""

    def plan_transport(state: Dict[str, Any]) -> Dict[str, Any]:
        """规划交通"""
        from_location = state.get("from_location", "")
        to_location = state.get("to_location", "")
        city = state.get("city", "")
        day = state.get("day", 1)

        prompt = ChatPromptTemplate.from_messages([
            ("system", get_transport_planning_prompt()),
            ("human", """请规划从 {from_location} 到 {to_location} 的交通路线：

出发地: {from_location}
目的地: {to_location}
所在城市: {city}

请提供详细的交通规划，包含多种交通方式对比。""")
        ])

        messages = prompt.format_messages(
            from_location=from_location,
            to_location=to_location,
            city=city,
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
                    transport_data = json.loads(json_str)
                else:
                    # 创建基本数据
                    transport_data = {
                        "recommended_method": "地铁",
                        "alternatives": [
                            {
                                "method": "地铁",
                                "route": f"{from_location} → {to_location}",
                                "duration": "约40分钟",
                                "cost": 6,
                                "steps": ["步行到地铁站", "乘坐地铁", "步行到达目的地"],
                                "pros": ["经济", "准时"],
                                "cons": ["可能需要换乘", "人流较多"]
                            },
                            {
                                "method": "打车",
                                "route": "直达",
                                "duration": "约25分钟",
                                "cost": 35,
                                "steps": ["叫车", "直达目的地"],
                                "pros": ["舒适", "快捷"],
                                "cons": ["费用高", "可能堵车"]
                            }
                        ],
                        "tips": ["避开高峰时段", "使用手机支付"],
                        "total_estimated_cost": 6,
                        "best_choice": "地铁（经济）"
                    }
            else:
                transport_data = content

            return {
                **state,
                f"transport_{day}_{from_location}_{to_location}": transport_data,
                "current_step": f"transport_planned_{day}"
            }

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"交通规划失败: {e}")

            return {
                **state,
                f"transport_{day}_{from_location}_{to_location}": {
                    "recommended_method": "地铁/公交",
                    "alternatives": [{
                        "method": "地铁",
                        "duration": "约40分钟",
                        "cost": 30,
                        "tips": "使用导航APP查看具体路线"
                    }],
                    "tips": ["提前规划路线", "避开高峰时段"]
                }
            }

    return plan_transport


def plan_simple_transport(from_loc: str, to_loc: str, city: str) -> Dict[str, Any]:
    """规划简单交通（非LLM版本）"""
    return {
        "method": "地铁/打车",
        "duration": "约40分钟",
        "cost": 30,
        "tips": f"从{from_loc}到{to_loc}建议使用导航APP查看实时路线"
    }
