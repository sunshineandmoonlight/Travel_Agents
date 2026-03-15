"""
TravelAgents - 旅行规划多Agent系统

基于原有TradingAgents架构改造的旅行规划系统
复用了LLM适配器、配置系统、日志系统等核心功能
"""

import os
from typing import Dict, Any, Optional, List, Literal
from datetime import datetime

from langchain_core.messages import BaseMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# 复用原有的LLM创建函数
from tradingagents.graph.trading_graph import create_llm_by_provider

# 导入旅行相关的工具
from tradingagents.utils.destination_classifier import DestinationClassifier
from tradingagents.utils.unified_data_interface import UnifiedDataProvider

# 简单日志（避免复杂的配置系统）
import logging
logger = logging.getLogger('travel_agents')


# ============================================================
# 旅行规划状态定义
# ============================================================

class TravelPlanningState(TypedDict):
    """旅行规划状态（对应原来的AgentState）"""
    # 用户输入
    destination: str                    # 目的地
    days: int                           # 天数
    budget: str                         # 预算级别
    travelers: int                      # 人数
    interest_type: str                  # 兴趣类型
    selected_style: str                 # 用户选择的方案类型

    # 系统识别
    destination_type: str               # domestic/international
    destination_info: Dict              # 目的地详细信息

    # 数据收集结果
    attractions: Dict                   # 景点数据
    weather_forecast: Dict              # 天气预报
    transport_info: Dict                # 交通信息

    # 方案生成
    proposals: Dict                     # 三种旅行方案

    # 详细行程
    detailed_itinerary: Dict            # 每日详细行程

    # 预算分析
    budget_breakdown: Dict              # 费用明细

    # 消息历史（对应原系统）
    messages: List[BaseMessage]

    # 元数据
    current_step: str                   # 当前步骤
    error: Optional[str]                # 错误信息


# ============================================================
# Agent 节点函数（对应原系统的analysts）
# ============================================================

def destination_classifier_node(state: TravelPlanningState) -> TravelPlanningState:
    """
    目的地分类节点（对应原系统的market_analyst）

    识别目的地类型（国内/国际）
    """
    destination = state.get("destination", "")

    logger.info(f"[目的地分类] 开始识别: {destination}")

    classification = DestinationClassifier.classify(destination)

    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"识别目的地: {destination} -> 类型: {classification['type']}",
        name="DestinationClassifier"
    ))

    logger.info(f"[目的地分类] 完成: {classification['type']}")

    return {
        **state,
        "destination_type": classification["type"],
        "destination_info": classification,
        "messages": messages,
        "current_step": "destination_classified"
    }


def data_collector_node(state: TravelPlanningState) -> TravelPlanningState:
    """
    数据收集节点（对应原系统的researchers）

    收集景点、天气、交通等数据
    """
    destination = state.get("destination", "")
    days = state.get("days", 5)
    interest_type = state.get("interest_type", "")

    logger.info(f"[数据收集] 开始收集 {destination} 的数据")

    provider = UnifiedDataProvider()

    # 收集景点数据
    attractions_result = provider.search_attractions(destination, interest_type)
    logger.info(f"[数据收集] 景点: {attractions_result.get('count', 0)} 个")

    # 收集天气数据
    weather_result = provider.get_weather(destination, min(days, 7))
    logger.info(f"[数据收集] 天气: {weather_result.get('count', 0)} 天")

    # 收集交通费用（从中国出发）
    transport_result = provider.estimate_transport_cost("中国", destination)
    logger.info(f"[数据收集] 交通: 已获取费用估算")

    messages = state.get("messages", [])

    attraction_count = attractions_result.get("count", 0)
    weather_count = weather_result.get("count", 0)

    messages.append(AIMessage(
        content=f"数据收集完成: 找到 {attraction_count} 个景点，{weather_count} 天天气预报",
        name="DataCollector"
    ))

    logger.info(f"[数据收集] 完成")

    return {
        **state,
        "attractions": attractions_result,
        "weather_forecast": weather_result,
        "transport_info": transport_result,
        "messages": messages,
        "current_step": "data_collected"
    }


def proposal_generator_node(state: TravelPlanningState) -> TravelPlanningState:
    """
    方案生成节点（对应原系统的analysts综合分析）

    根据收集的数据生成3种旅行方案
    """
    destination = state.get("destination", "")
    days = state.get("days", 5)
    budget = state.get("budget", "medium")
    travelers = state.get("travelers", 2)

    logger.info(f"[方案生成] 开始为 {destination} 生成 {days} 天方案")

    # 这里可以调用LLM生成更智能的方案
    # 暂时使用模板数据

    proposals = {
        "immersive": {
            "name": "深度沉浸",
            "description": f"深度体验{destination}的文化与生活",
            "style": "immersive",
            "intensity": "medium",
            "budget_level": "medium",
            "estimated_cost": 0,
            "highlights": [],
            "daily_itinerary": []
        },
        "exploration": {
            "name": "全面探索",
            "description": f"打卡{destination}的主要景点和地标",
            "style": "exploration",
            "intensity": "high",
            "budget_level": "medium",
            "estimated_cost": 0,
            "highlights": [],
            "daily_itinerary": []
        },
        "relaxed": {
            "name": "休闲度假",
            "description": f"在{destination}享受悠闲时光",
            "style": "relaxed",
            "intensity": "low",
            "budget_level": "high",
            "estimated_cost": 0,
            "highlights": [],
            "daily_itinerary": []
        }
    }

    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"生成了3种旅行方案: 深度沉浸、全面探索、休闲度假",
        name="ProposalGenerator"
    ))

    logger.info(f"[方案生成] 完成")

    return {
        **state,
        "proposals": proposals,
        "messages": messages,
        "current_step": "proposals_generated"
    }


def itinerary_planner_node(state: TravelPlanningState) -> TravelPlanningState:
    """
    行程规划节点（对应原系统的trader）

    根据用户选择的方案类型，生成详细行程
    """
    selected_style = state.get("selected_style", "exploration")
    proposals = state.get("proposals", {})
    days = state.get("days", 5)

    logger.info(f"[行程规划] 生成 {selected_style} 风格的 {days} 天行程")

    proposal = proposals.get(selected_style, {})

    # 生成详细行程（简化版）
    daily_itinerary = []
    for day in range(1, days + 1):
        daily_itinerary.append({
            "day": day,
            "date": "",
            "activities": [],
            "meals": {"breakfast": "", "lunch": "", "dinner": ""},
            "accommodation": "",
            "transportation": "",
            "estimated_cost": 0
        })

    itinerary = {
        "style": selected_style,
        "proposal": proposal,
        "daily": daily_itinerary,
        "total_days": days
    }

    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"生成了{days}天的详细行程（{proposal.get('name', '未知')}）",
        name="ItineraryPlanner"
    ))

    logger.info(f"[行程规划] 完成")

    return {
        **state,
        "detailed_itinerary": itinerary,
        "messages": messages,
        "current_step": "itinerary_planned"
    }


def budget_analyst_node(state: TravelPlanningState) -> TravelPlanningState:
    """
    预算分析节点（对应原系统的risk_manager）

    计算旅行总费用
    """
    destination = state.get("destination", "")
    days = state.get("days", 5)
    travelers = state.get("travelers", 2)
    budget = state.get("budget", "medium")

    logger.info(f"[预算分析] 计算 {travelers} 人 {days} 天费用")

    transport_info = state.get("transport_info", {})

    # 简化费用计算
    transport_cost = 0
    if "price_estimate" in transport_info:
        prices = transport_info["price_estimate"]
        if isinstance(prices, dict):
            transport_cost = prices.get("economy_avg") or prices.get("second_class") or prices.get("economy") or 0

    # 住宿费用
    accommodation_per_night = 500 if budget == "low" else 800 if budget == "medium" else 1500
    accommodation_cost = accommodation_per_night * days * travelers

    # 餐饮费用
    meal_per_day = 200 if budget == "low" else 400 if budget == "medium" else 800
    meal_cost = meal_per_day * days * travelers

    # 景点门票费用
    attraction_cost = 300 * days * travelers

    total_cost = transport_cost + accommodation_cost + meal_cost + attraction_cost

    budget_breakdown = {
        "transportation": transport_cost,
        "accommodation": accommodation_cost,
        "meals": meal_cost,
        "attractions": attraction_cost,
        "misc": total_cost * 0.1,
        "total": total_cost * 1.1
    }

    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"预算分析完成: 预计总费用 {budget_breakdown['total']:.0f} 元",
        name="BudgetAnalyst"
    ))

    logger.info(f"[预算分析] 完成: 总费用 {budget_breakdown['total']:.0f} 元")

    return {
        **state,
        "budget_breakdown": budget_breakdown,
        "messages": messages,
        "current_step": "budget_analyzed"
    }


# ============================================================
# 条件边函数（对应原系统的conditional_logic）
# ============================================================

def should_continue_data_collection(state: TravelPlanningState) -> Literal["proposal_generator", "end"]:
    """判断是否继续数据收集"""
    attractions = state.get("attractions", {})
    weather = state.get("weather_forecast", {})

    if attractions.get("success") and weather.get("success"):
        return "proposal_generator"
    else:
        return "end"


def should_generate_itinerary(state: TravelPlanningState) -> Literal["itinerary_planner", "end"]:
    """判断是否生成详细行程"""
    selected_style = state.get("selected_style")

    if selected_style and selected_style in ["immersive", "exploration", "relaxed"]:
        return "itinerary_planner"
    else:
        return "end"


def should_analyze_budget(state: TravelPlanningState) -> Literal["budget_analyst", "end"]:
    """判断是否分析预算"""
    itinerary = state.get("detailed_itinerary", {})

    if itinerary and itinerary.get("daily"):
        return "budget_analyst"
    else:
        return "end"


# ============================================================
# 旅行规划图类（对应原系统的TradingAgentsGraph）
# ============================================================

class TravelAgentsGraph:
    """
    旅行规划Agent系统

    基于原有TradingAgents架构改造，复用了：
    - LLM适配器系统
    - 配置管理系统
    - 日志系统
    - 状态管理模式
    """

    def __init__(
        self,
        llm_provider: str = "deepseek",
        llm_model: str = "deepseek-chat",
        debug: bool = False,
        config: Dict[str, Any] = None
    ):
        """
        初始化旅行规划图

        Args:
            llm_provider: LLM供应商
            llm_model: LLM模型名称
            debug: 调试模式
            config: 配置字典
        """
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.debug = debug
        self.config = config or {}

        logger.info(f"[TravelAgentsGraph] 初始化: provider={llm_provider}, model={llm_model}")

        # 创建状态图
        self.workflow = StateGraph(TravelPlanningState)

        # 添加节点（对应原系统的analysts、trader等）
        self.workflow.add_node("destination_classifier", destination_classifier_node)
        self.workflow.add_node("data_collector", data_collector_node)
        self.workflow.add_node("proposal_generator", proposal_generator_node)
        self.workflow.add_node("itinerary_planner", itinerary_planner_node)
        self.workflow.add_node("budget_analyst", budget_analyst_node)

        # 设置入口点
        self.workflow.set_entry_point("destination_classifier")

        # 添加边（对应原系统的conditional edges）
        self.workflow.add_edge("destination_classifier", "data_collector")
        self.workflow.add_conditional_edges(
            "data_collector",
            should_continue_data_collection,
            {
                "proposal_generator": "proposal_generator",
                "end": END
            }
        )
        self.workflow.add_conditional_edges(
            "proposal_generator",
            should_generate_itinerary,
            {
                "itinerary_planner": "itinerary_planner",
                "end": END
            }
        )
        self.workflow.add_conditional_edges(
            "itinerary_planner",
            should_analyze_budget,
            {
                "budget_analyst": "budget_analyst",
                "end": END
            }
        )
        self.workflow.add_edge("budget_analyst", END)

        # 编译图
        self.graph = self.workflow.compile()

        logger.info(f"[TravelAgentsGraph] 图编译完成")

    def plan(
        self,
        destination: str,
        days: int = 5,
        budget: str = "medium",
        travelers: int = 2,
        interest_type: str = "",
        selected_style: str = ""
    ) -> Dict[str, Any]:
        """
        规划旅行

        Args:
            destination: 目的地
            days: 天数
            budget: 预算级别
            travelers: 人数
            interest_type: 兴趣类型
            selected_style: 方案类型

        Returns:
            旅行规划结果
        """
        logger.info(f"[TravelAgentsGraph] 开始规划: {destination}, {days}天")

        # 初始化状态（对应原系统的initial_state）
        initial_state: TravelPlanningState = {
            "destination": destination,
            "days": days,
            "budget": budget,
            "travelers": travelers,
            "interest_type": interest_type,
            "selected_style": selected_style,
            "destination_type": "",
            "destination_info": {},
            "attractions": {},
            "weather_forecast": {},
            "transport_info": {},
            "proposals": {},
            "detailed_itinerary": {},
            "budget_breakdown": {},
            "messages": [],
            "current_step": "init",
            "error": None
        }

        # 运行图
        result = self.graph.invoke(initial_state)

        logger.info(f"[TravelAgentsGraph] 规划完成: {result.get('current_step', 'unknown')}")

        return result

    def stream_plan(
        self,
        destination: str,
        days: int = 5,
        budget: str = "medium",
        travelers: int = 2,
        interest_type: str = "",
        selected_style: str = ""
    ):
        """
        流式规划旅行（用于实时进度显示）

        Args:
            同 plan()

        Returns:
            生成器，逐步产生状态更新
        """
        initial_state: TravelPlanningState = {
            "destination": destination,
            "days": days,
            "budget": budget,
            "travelers": travelers,
            "interest_type": interest_type,
            "selected_style": selected_style,
            "destination_type": "",
            "destination_info": {},
            "attractions": {},
            "weather_forecast": {},
            "transport_info": {},
            "proposals": {},
            "detailed_itinerary": {},
            "budget_breakdown": {},
            "messages": [],
            "current_step": "init",
            "error": None
        }

        for event in self.graph.stream(initial_state):
            yield event


# ============================================================
# 便捷函数（对应原系统的create_trading_graph）
# ============================================================

def create_travel_graph(
    llm_provider: str = "deepseek",
    llm_model: str = "deepseek-chat",
    **kwargs
) -> TravelAgentsGraph:
    """
    创建旅行规划图（对应create_trading_graph）

    Args:
        llm_provider: LLM供应商
        llm_model: LLM模型名称
        **kwargs: 其他参数

    Returns:
        TravelAgentsGraph 实例
    """
    return TravelAgentsGraph(
        llm_provider=llm_provider,
        llm_model=llm_model,
        **kwargs
    )


# ============================================================
# 使用示例
# ============================================================

if __name__ == "__main__":
    # 创建旅行规划图
    travel_graph = create_travel_graph(
        llm_provider="deepseek",
        llm_model="deepseek-chat"
    )

    # 规划旅行
    result = travel_graph.plan(
        destination="北京",
        days=5,
        budget="medium",
        travelers=2,
        interest_type="历史",
        selected_style="exploration"
    )

    print("=" * 60)
    print("旅行规划结果")
    print("=" * 60)

    print(f"目的地: {result['destination']}")
    print(f"类型: {result['destination_type']}")
    print(f"天数: {result['days']}")
    print(f"人数: {result['travelers']}")

    print("\n消息:")
    for msg in result['messages']:
        print(f"  [{msg.name}] {msg.content}")

    if result.get('budget_breakdown'):
        print(f"\n预算:")
        for key, value in result['budget_breakdown'].items():
            print(f"  {key}: {value}")
