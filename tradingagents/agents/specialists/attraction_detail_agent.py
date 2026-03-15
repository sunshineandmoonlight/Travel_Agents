"""
景点详情生成智能体

专门负责为每个景点生成详细的、真实可用的游览信息
"""

from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any
import json


def get_attraction_detail_prompt() -> str:
    """返回景点详情生成的系统提示词"""
    return """你是一位资深的旅游景点规划专家，拥有丰富的实地导游经验。

你的任务是为每个景点生成详细、真实、实用的游览信息。

重要要求：
1. **真实具体**：所有信息必须真实可用，不要使用"探索独特之处"这类空泛描述
2. **详细描述**：提供50-100字的详细介绍，包含历史背景、建筑特色、文化价值
3. **实用建议**：提供具体的游览路线、避开人群技巧、拍照建议
4. **准确信息**：提供准确的门票价格、开放时间、最佳游览时间

输入信息：
- attraction_name: 景点名称
- city: 所在城市
- day: 第几天
- time_slot: 时间段

输出格式（严格遵循JSON格式）：
{
    "name": "景点名称",
    "description": "详细描述（80-120字），包含历史、特色、看点",
    "highlights": [
        "必看亮点1：具体描述",
        "必看亮点2：具体描述",
        "必看亮点3：具体描述"
    ],
    "suggested_route": "推荐游览路线，如：入口 → A景点 → B景点 → 出口",
    "time_needed": "建议游览时间，如：2-3小时",
    "best_time_to_visit": "最佳游览时间，如：早上9-11点人少",
    "photography_spots": [
        "拍照点1：位置和拍摄建议",
        "拍照点2：位置和拍摄建议"
    ],
    "tickets": {
        "price": 60,
        "notes": "购票建议：提前7天在公众号预约，学生票半价",
        "open_hours": "8:30-17:00（最晚16:00入园）"
    },
    "tips": [
        "实用贴士1：穿舒适鞋子，全程步行3公里",
        "实用贴士2：自带水和零食，景区内价格较高",
        "实用贴士3：避开旅行团高峰期（10-11点，14-15点）"
    ]
}

参考示例：
对于"故宫"，不要只说"探索故宫的独特之处"，
而要说："故宫是明清两代皇宫，现存最大古建筑群。太和殿金銮殿是皇帝举行大典之所，乾清宫是皇帝寝宫和处理政务之地，御花园是皇家园林。建议路线：午门进→太和殿→中和殿→保和殿→乾清宫→御花园→神武门出。重点看三大殿和御花园堆秀山（可俯瞰故宫全景）。"
"""


def create_attraction_detail_agent(llm):
    """创建景点详情生成智能体"""

    def generate_attraction_detail(state: Dict[str, Any]) -> Dict[str, Any]:
        """生成景点详情"""
        attraction_name = state.get("attraction_name", "")
        city = state.get("city", "")
        day = state.get("day", 1)
        time_slot = state.get("time_slot", "morning")

        prompt = ChatPromptTemplate.from_messages([
            ("system", get_attraction_detail_prompt()),
            ("human", """请为以下景点生成详细的游览信息：

景点名称: {attraction_name}
所在城市: {city}
游览时间: 第{day}天-{time_slot}

请生成详细、真实、实用的景点信息。""")
        ])

        messages = prompt.format_messages(
            attraction_name=attraction_name,
            city=city,
            day=day,
            time_slot=time_slot
        )

        try:
            response = llm.invoke(messages)
            content = response.content

            # 解析JSON响应
            if isinstance(content, str):
                # 提取JSON部分
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    detail_data = json.loads(json_str)
                else:
                    # 如果没有找到JSON，创建基本数据
                    detail_data = {
                        "name": attraction_name,
                        "description": f"{attraction_name}是{city}的著名景点，拥有丰富的历史文化和独特的建筑风格，值得细细品味。",
                        "highlights": [
                            f"欣赏{attraction_name}的独特建筑风格",
                            f"了解{attraction_name}的历史文化背景",
                            f"体验{attraction_name}的游览氛围"
                        ],
                        "suggested_route": f"按景区指示游览",
                        "time_needed": "2-3小时",
                        "best_time_to_visit": "上午",
                        "photography_spots": [
                            "景区入口处",
                            "主要景点前"
                        ],
                        "tickets": {
                            "price": 50,
                            "notes": "现场购票或提前预约",
                            "open_hours": "9:00-17:00"
                        },
                        "tips": [
                            "穿舒适的鞋子",
                            "自带饮用水",
                            "注意保护环境"
                        ]
                    }
            else:
                detail_data = content

            return {
                **state,
                f"attraction_detail_{day}_{time_slot}": detail_data,
                "current_step": f"attraction_detail_generated_{day}_{time_slot}"
            }

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"景点详情生成失败: {e}")

            # 返回基本数据
            return {
                **state,
                f"attraction_detail_{day}_{time_slot}": {
                    "name": attraction_name,
                    "description": f"{attraction_name}是{city}的热门景点，建议深入游览。",
                    "highlights": ["欣赏美景", "了解文化"],
                    "suggested_route": "常规游览路线",
                    "time_needed": "2小时",
                    "tickets": {"price": 50, "notes": "现场购票"}
                }
            }

    return generate_attraction_detail
