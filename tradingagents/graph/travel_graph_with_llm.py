"""
使用 LLM Analysts 的旅行规划图

这是使用真实 LLM 分析师的版本，提供更智能的旅行规划
"""

from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage

# 复用原有的LLM创建函数
from tradingagents.graph.trading_graph import create_llm_by_provider

# 导入旅行 analysts
from tradingagents.agents.analysts.attraction_analyst import create_attraction_analyst
from tradingagents.agents.analysts.itinerary_planner import create_itinerary_planner
from tradingagents.agents.analysts.budget_analyst import create_budget_analyst

# 导入旅行工具
from tradingagents.utils.destination_classifier import DestinationClassifier
from tradingagents.utils.unified_data_interface import UnifiedDataProvider

import logging
logger = logging.getLogger('travel_agents')


class TravelPlanningState(Dict):
    """旅行规划状态字典"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置默认值
        self.setdefault("messages", [])
        self.setdefault("current_step", "init")
        self.setdefault("error", None)


# ============================================================
# Agent 节点函数（使用 LLM）
# ============================================================

def destination_classifier_node(state: Dict) -> Dict:
    """目的地分类节点"""
    destination = state.get("destination", "")

    classification = DestinationClassifier.classify(destination)

    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"识别目的地: {destination} -> 类型: {classification['type']}",
        name="DestinationClassifier"
    ))

    state["destination_type"] = classification["type"]
    state["destination_info"] = classification
    state["messages"] = messages
    state["current_step"] = "destination_classified"

    return state


def data_collector_node(state: Dict) -> Dict:
    """数据收集节点"""
    destination = state.get("destination", "")
    days = state.get("days", 5)
    interest_type = state.get("interest_type", "")

    logger.info(f"[数据收集] 开始收集 {destination} 的数据")

    provider = UnifiedDataProvider()

    # 收集数据
    attractions_result = provider.search_attractions(destination, interest_type)
    weather_result = provider.get_weather(destination, min(days, 7))
    transport_result = provider.estimate_transport_cost("中国", destination)

    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"数据收集完成: 找到 {attractions_result.get('count', 0)} 个景点",
        name="DataCollector"
    ))

    state["attractions"] = attractions_result
    state["weather_forecast"] = weather_result
    state["transport_info"] = transport_result
    state["messages"] = messages
    state["current_step"] = "data_collected"

    return state


def attraction_analyst_node(state: Dict) -> Dict:
    """景点分析节点（使用 LLM）"""
    llm = state.get("_llm")

    if not llm:
        logger.warning("[景点分析师] 未配置 LLM，跳过")
        return state

    agent = create_attraction_analyst(llm)

    try:
        result = agent(state)
        messages = state.get("messages", [])
        messages.append(AIMessage(
            content=f"景点分析完成",
            name="AttractionAnalyst"
        ))
        result["messages"] = messages
        return result
    except Exception as e:
        logger.error(f"[景点分析师] 执行失败: {e}")
        return state


def itinerary_planner_node(state: Dict) -> Dict:
    """行程规划节点（使用 LLM）"""
    llm = state.get("_llm")

    if not llm:
        logger.warning("[行程规划师] 未配置 LLM，使用简化方案")
        # 生成简化行程
        from tradingagents.agents.analysts.itinerary_planner import generate_simple_itinerary
        itinerary = generate_simple_itinerary(
            state.get("destination", ""),
            state.get("days", 5),
            state.get("budget", "medium"),
            state.get("travelers", 2)
        )
        state["detailed_itinerary"] = itinerary
        state["current_step"] = "itinerary_planned"
        return state

    agent = create_itinerary_planner(llm)

    try:
        result = agent(state)
        messages = state.get("messages", [])
        messages.append(AIMessage(
            content=f"行程规划完成: {state.get('days')}天详细行程",
            name="ItineraryPlanner"
        ))
        result["messages"] = messages
        return result
    except Exception as e:
        logger.error(f"[行程规划师] 执行失败: {e}")
        return state


def budget_analyst_node(state: Dict) -> Dict:
    """预算分析节点（使用 LLM）"""
    llm = state.get("_llm")

    if not llm:
        logger.warning("[预算分析师] 未配置 LLM，使用简化方案")
        # 简化预算计算
        transport = state.get("transport_info", {}).get("price_estimate", {})
        transport_cost = transport.get("second_class", 0) or transport.get("economy_avg", 0)

        days = state.get("days", 5)
        travelers = state.get("travelers", 2)
        budget = state.get("budget", "medium")

        accommodation = 500 * days * travelers
        meals = 300 * days * travelers
        attractions = 200 * days * travelers
        misc = (accommodation + meals + attractions) * 0.1

        total = transport_cost + accommodation + meals + attractions + misc

        state["budget_breakdown"] = {
            "transportation": {"amount": int(transport_cost)},
            "accommodation": {"amount": int(accommodation)},
            "meals": {"amount": int(meals)},
            "attractions": {"amount": int(attractions)},
            "miscellaneous": {"amount": int(misc)},
            "total_budget": int(total)
        }
        state["current_step"] = "budget_analyzed"
        return state

    agent = create_budget_analyst(llm)

    try:
        result = agent(state)
        messages = state.get("messages", [])
        messages.append(AIMessage(
            content=f"预算分析完成: 预计总费用",
            name="BudgetAnalyst"
        ))
        result["messages"] = messages
        return result
    except Exception as e:
        logger.error(f"[预算分析师] 执行失败: {e}")
        return state


# ============================================================
# 条件边函数
# ============================================================

def should_use_llm(state: Dict) -> str:
    """判断是否使用 LLM 分析"""
    if state.get("_llm"):
        return "use_llm"
    else:
        return "skip_llm"


# ============================================================
# 旅行规划图类
# ============================================================

class TravelAgentsGraphWithLLM:
    """
    旅行规划 Agent 系统（带 LLM）

    使用真实的 LLM 进行智能分析
    """

    def __init__(
        self,
        llm_provider: str = "deepseek",
        llm_model: str = "deepseek-chat",
        temperature: float = 0.7,
        **kwargs
    ):
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.temperature = temperature

        # 根据不同的 provider 设置 backend_url
        backend_url = ""
        if llm_provider.lower() == "siliconflow":
            backend_url = "https://api.siliconflow.cn/v1"
        elif llm_provider.lower() == "deepseek":
            backend_url = "https://api.deepseek.com"

        # 创建 LLM
        self.llm = create_llm_by_provider(
            provider=llm_provider,
            model=llm_model,
            backend_url=backend_url,
            temperature=temperature,
            max_tokens=2000,
            timeout=60
        )

        # 创建状态图
        self.workflow = StateGraph(TravelPlanningState)

        # 添加节点
        self.workflow.add_node("destination_classifier", destination_classifier_node)
        self.workflow.add_node("data_collector", data_collector_node)
        self.workflow.add_node("attraction_analyst", attraction_analyst_node)
        self.workflow.add_node("itinerary_planner", itinerary_planner_node)
        self.workflow.add_node("budget_analyst", budget_analyst_node)

        # 设置入口点
        self.workflow.set_entry_point("destination_classifier")

        # 添加边
        self.workflow.add_edge("destination_classifier", "data_collector")
        self.workflow.add_edge("data_collector", "attraction_analyst")
        self.workflow.add_edge("attraction_analyst", "itinerary_planner")
        self.workflow.add_edge("itinerary_planner", "budget_analyst")
        self.workflow.add_edge("budget_analyst", END)

        # 编译图
        self.graph = self.workflow.compile()

        logger.info(f"[TravelAgentsGraphWithLLM] 初始化完成")

    def plan(
        self,
        destination: str,
        days: int = 5,
        budget: str = "medium",
        travelers: int = 2,
        interest_type: str = "",
        selected_style: str = ""
    ) -> Dict[str, Any]:
        """规划旅行"""
        logger.info(f"[TravelAgentsGraphWithLLM] 开始规划: {destination}, {days}天")

        # 初始化状态
        initial_state = TravelPlanningState({
            "destination": destination,
            "days": days,
            "budget": budget,
            "travelers": travelers,
            "interest_type": interest_type,
            "selected_style": selected_style,
            "_llm": self.llm,  # 传入 LLM 实例
            "current_step": "init"
        })

        # 运行图
        result = self.graph.invoke(initial_state)

        logger.info(f"[TravelAgentsGraphWithLLM] 规划完成")

        return result


def create_travel_graph_with_llm(
    llm_provider: str = "deepseek",
    llm_model: str = "deepseek-chat",
    **kwargs
) -> TravelAgentsGraphWithLLM:
    """创建带 LLM 的旅行规划图"""
    return TravelAgentsGraphWithLLM(
        llm_provider=llm_provider,
        llm_model=llm_model,
        **kwargs
    )


# ============================================================
# 使用示例
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  旅行规划系统 - LLM 版本")
    print("=" * 60)

    # 创建旅行规划图
    graph = create_travel_graph_with_llm(
        llm_provider="deepseek",
        llm_model="deepseek-chat"
    )

    # 规划旅行
    print("\n正在规划北京之旅...")
    result = graph.plan(
        destination="北京",
        days=5,
        budget="medium",
        travelers=2,
        interest_type="历史"
    )

    print("\n规划结果:")
    print(f"  目的地: {result['destination']}")
    print(f"  类型: {result['destination_type']}")
    print(f"  步骤: {result['current_step']}")

    if result.get("budget_breakdown"):
        budget = result["budget_breakdown"]
        print(f"\n  预算: {budget.get('total_budget', 0)} 元")
        print(f"  日均: {budget.get('daily_average', 0)} 元")
        print(f"  人均: {budget.get('per_person_average', 0)} 元")
