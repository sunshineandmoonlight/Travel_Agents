"""
预算分析师 - Budget Analyst

分析旅行费用，提供详细的预算分解
"""

from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any
import json


def get_budget_system_prompt() -> str:
    """返回预算分析师的系统提示词"""
    return """你是一位专业的旅行预算分析师。

你的职责：
1. 分析旅行的各项费用
2. 提供详细的预算分解
3. 给出节省建议
4. 评估费用合理性

输入信息：
- destination: 目的地
- days: 天数
- budget: 预算级别 (low/medium/high)
- travelers: 人数
- detailed_itinerary: 详细行程
- transport_info: 交通信息

输出格式：
{
    "budget_breakdown": {
        "transportation": {
            "amount": 金额,
            "description": "交通费用说明",
            "cost_saving_tips": "节省建议"
        },
        "accommodation": {
            "amount": 金额,
            "description": "住宿费用说明",
            "cost_saving_tips": "节省建议"
        },
        "meals": {
            "amount": 金额,
            "description": "餐饮费用说明",
            "cost_saving_tips": "节省建议"
        },
        "attractions": {
            "amount": 金额,
            "description": "景点门票费用说明",
            "cost_saving_tips": "节省建议"
        },
        "miscellaneous": {
            "amount": 金额,
            "description": "其他费用说明",
            "cost_saving_tips": "节省建议"
        }
    },
    "total_budget": 总金额,
    "daily_average": 日均费用,
    "per_person_average": 人均费用,
    "budget_assessment": "预算评估 (合理/偏高/偏低)",
    "recommendations": ["建议1", "建议2"],
    "money_saving_tips": ["省钱技巧1", "省钱技巧2"]
}
"""


def create_budget_analyst(llm):
    """创建预算分析师 Agent"""

    def analyze_budget(state: Dict[str, Any]) -> Dict[str, Any]:
        """分析预算"""
        destination = state.get("destination", "")
        days = state.get("days", 5)
        budget = state.get("budget", "medium")
        travelers = state.get("travelers", 2)
        itinerary = state.get("detailed_itinerary", {})
        transport_info = state.get("transport_info", {})

        # 获取交通费用
        transport_cost = 0
        if transport_info.get("price_estimate"):
            prices = transport_info["price_estimate"]
            if transport_info.get("type") == "high_speed_rail":
                transport_cost = prices.get("second_class", 0)
            else:
                transport_cost = prices.get("economy_avg", 0)

        # 估算费用
        breakdown = estimate_budget_breakdown(
            destination, days, budget, travelers, transport_cost, itinerary
        )

        # 构建 LLM 提示（用于优化建议）
        prompt = ChatPromptTemplate.from_messages([
            ("system", get_budget_system_prompt()),
            ("human", """请分析以下旅行预算：

目的地: {destination}
天数: {days}
预算级别: {budget}
人数: {travelers}

当前预算估算:
{budget_info}

请提供预算分析和省钱建议。""")
        ])

        budget_info = f"""
交通: {breakdown['transportation']['amount']}元
住宿: {breakdown['accommodation']['amount']}元
餐饮: {breakdown['meals']['amount']}元
景点: {breakdown['attractions']['amount']}元
其他: {breakdown['miscellaneous']['amount']}元
总计: {breakdown['total_budget']}元
"""

        messages = prompt.format_messages(
            destination=destination,
            days=days,
            budget=budget,
            travelers=travelers,
            budget_info=budget_info
        )

        try:
            response = llm.invoke(messages)
            analysis = response.content

            # 尝试获取建议
            recommendations = []
            money_saving_tips = []

            if "建议" in analysis:
                # 简单提取建议
                lines = analysis.split("\n")
                for line in lines:
                    if "建议" in line or "省钱" in line or "节省" in line:
                        if "省钱" in line:
                            money_saving_tips.append(line.strip())
                        else:
                            recommendations.append(line.strip())

            if not recommendations:
                recommendations = [
                    "提前预订可享受折扣",
                    "选择非旺季出行可节省30%费用",
                    "当地公共交通比打车更经济"
                ]

            if not money_saving_tips:
                money_saving_tips = [
                    "住宿选择经济型酒店或民宿",
                    "餐饮尝试当地街头美食",
                    "景点购买联票更划算"
                ]

            breakdown["recommendations"] = recommendations[:3]
            breakdown["money_saving_tips"] = money_saving_tips[:3]

        except Exception as e:
            breakdown["recommendations"] = [
                "提前预订可享受折扣",
                "选择非旺季出行可节省费用"
            ]
            breakdown["money_saving_tips"] = [
                "住宿选择经济型酒店",
                "餐饮尝试当地美食"
            ]

        state["budget_breakdown"] = breakdown
        state["current_step"] = "budget_analyzed"

        return state

    return analyze_budget


def estimate_budget_breakdown(
    destination: str,
    days: int,
    budget: str,
    travelers: int,
    transport_cost: int,
    itinerary: Dict
) -> Dict:
    """估算预算分解"""
    # 预算设置
    accommodation_per_night = {
        "low": 300,
        "medium": 500,
        "high": 1000
    }
    meal_per_day = {
        "low": 150,
        "medium": 300,
        "high": 600
    }
    attraction_per_day = {
        "low": 100,
        "medium": 200,
        "high": 500
    }

    # 计算各项费用
    accommodation_cost = accommodation_per_night[budget] * days * travelers
    meal_cost = meal_per_day[budget] * days * travelers
    attraction_cost = attraction_per_day[budget] * days * travelers
    misc_cost = (accommodation_cost + meal_cost + attraction_cost) * 0.1  # 10%

    total = transport_cost + accommodation_cost + meal_cost + attraction_cost + misc_cost

    return {
        "transportation": {
            "amount": int(transport_cost),
            "description": f"往返{destination}的交通费用",
            "cost_saving_tips": "提前预订可享受折扣"
        },
        "accommodation": {
            "amount": int(accommodation_cost),
            "description": f"{days}晚住宿费用（{budget}级别）",
            "cost_saving_tips": "选择民宿或青年旅舍更经济"
        },
        "meals": {
            "amount": int(meal_cost),
            "description": f"{days}天餐饮费用",
            "cost_saving_tips": "尝试当地街头美食体验"
        },
        "attractions": {
            "amount": int(attraction_cost),
            "description": f"景点门票和活动费用",
            "cost_saving_tips": "购买景点联票或套票"
        },
        "miscellaneous": {
            "amount": int(misc_cost),
            "description": "其他费用（购物、应急等）",
            "cost_saving_tips": "预留应急资金"
        },
        "total_budget": int(total),
        "daily_average": int(total / days),
        "per_person_average": int(total / travelers),
        "budget_assessment": "合理" if budget == "medium" else "偏高" if budget == "high" else "经济"
    }
