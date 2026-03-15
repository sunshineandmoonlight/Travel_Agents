"""
景点分析师 - Attraction Analyst

分析目的地景点，推荐最佳旅游路线
"""

from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any, Optional
import json

# 导入旅行相关工具
from tradingagents.utils.destination_classifier import DestinationClassifier
from tradingagents.utils.unified_data_interface import UnifiedDataProvider


def get_attraction_system_prompt() -> str:
    """返回景点分析师的系统提示词"""
    return """你是一位专业的旅行景点分析师。

你的职责：
1. 分析目的地景点信息
2. 根据用户兴趣推荐景点
3. 规划最佳游览路线
4. 提供景点介绍和游玩建议

输入信息：
- destination: 目的地
- days: 天数
- interest_type: 兴趣类型（历史、自然、美食、购物等）
- travelers: 人数

输出格式：
{
    "recommended_attractions": [
        {
            "name": "景点名称",
            "description": "景点描述",
            "recommended_duration": "建议游玩时长",
            "best_time_to_visit": "最佳游览时间",
            "highlights": ["亮点1", "亮点2"],
            "tips": "游玩建议"
        }
    ],
    "daily_route": [
        {
            "day": 1,
            "attractions": ["景点1", "景点2"],
            "route_description": "路线描述"
        }
    ],
    "total_review": "总体评价和建议"
}

请根据目的地和用户兴趣，推荐最合适的景点。
"""


def create_attraction_analyst(llm, tools: Optional[Dict] = None):
    """
    创建景点分析师 Agent

    Args:
        llm: 语言模型实例
        tools: 可用工具字典

    Returns:
        可调用的 Agent 函数
    """

    def analyze_attractions(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析景点

        Args:
            state: 当前状态，包含用户输入和已收集的数据

        Returns:
            更新后的状态，包含景点分析结果
        """
        destination = state.get("destination", "")
        days = state.get("days", 5)
        interest_type = state.get("interest_type", "")
        travelers = state.get("travelers", 2)

        # 获取已收集的景点数据
        attractions_data = state.get("attractions", {})
        attraction_list = attractions_data.get("attractions", [])

        if not attraction_list:
            # 如果没有数据，使用统一数据接口获取
            provider = UnifiedDataProvider()
            result = provider.search_attractions(destination, interest_type)
            attraction_list = result.get("attractions", [])

        # 构建 LLM 提示
        prompt = ChatPromptTemplate.from_messages([
            ("system", get_attraction_system_prompt()),
            ("human", """请分析以下目的地的景点：

目的地: {destination}
天数: {days}
兴趣类型: {interest_type}
人数: {travelers}

可用景点:
{attractions_info}

请推荐最佳景点和游览路线。""")
        ])

        # 格式化景点信息
        attractions_info = ""
        for i, attr in enumerate(attraction_list[:10], 1):
            attractions_info += f"{i}. {attr.get('name', '')}: {attr.get('address', '')}\n"

        # 调用 LLM
        messages = prompt.format_messages(
            destination=destination,
            days=days,
            interest_type=interest_type or "一般",
            travelers=travelers,
            attractions_info=attractions_info or "暂无景点信息"
        )

        try:
            response = llm.invoke(messages)
            analysis_result = response.content

            # 尝试解析 JSON 结果
            try:
                # 提取 JSON 部分
                if "```json" in analysis_result:
                    json_str = analysis_result.split("```json")[1].split("```")[0].strip()
                elif "```" in analysis_result:
                    json_str = analysis_result.split("```")[1].split("```")[0].strip()
                else:
                    json_str = analysis_result

                recommendations = json.loads(json_str)
            except:
                # 如果解析失败，使用简化结果
                recommendations = {
                    "recommended_attractions": [
                        {
                            "name": attr.get("name", ""),
                            "description": attr.get("address", ""),
                            "recommended_duration": "2-3小时",
                            "best_time_to_visit": "上午",
                            "highlights": [],
                            "tips": "建议提前预约"
                        }
                        for attr in attraction_list[:5]
                    ],
                    "daily_route": [],
                    "total_review": f"为{destination}推荐了{len(attraction_list)}个景点"
                }

        except Exception as e:
            # 降级方案：直接返回原始数据
            recommendations = {
                "recommended_attractions": [
                    {
                        "name": attr.get("name", ""),
                        "description": attr.get("address", ""),
                        "recommended_duration": "2-3小时"
                    }
                    for attr in attraction_list[:5]
                ],
                "error": str(e)
            }

        # 更新状态
        state["attraction_analysis"] = recommendations
        state["current_step"] = "attraction_analyzed"

        return state

    return analyze_attractions


# 使用示例
if __name__ == "__main__":
    # 测试代码
    from tradingagents.graph.trading_graph import create_llm_by_provider

    llm = create_llm_by_provider(
        provider="deepseek",
        model="deepseek-chat",
        backend_url="",
        temperature=0.7,
        max_tokens=2000,
        timeout=60
    )

    agent = create_attraction_analyst(llm)

    # 测试状态
    test_state = {
        "destination": "北京",
        "days": 5,
        "interest_type": "历史",
        "travelers": 2,
        "attractions": {}
    }

    result = agent(test_state)
    print("景点分析结果:")
    print(json.dumps(result.get("attraction_analysis", {}), ensure_ascii=False, indent=2))
