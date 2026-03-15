"""
Group C 智能体工具绑定模块

展示如何在 Group C 智能体（景点排程师、餐饮推荐师、交通规划师）中
绑定和使用 LangChain 工具。
"""

from typing import Dict, Any, List, Optional
import logging
import os

logger = logging.getLogger('travel_agents')


# ============================================================
# 工具绑定示例
# ============================================================

def bind_tools_to_agent(agent_name: str, llm):
    """
    为智能体绑定相应的工具

    Args:
        agent_name: 智能体名称 (attraction_scheduler/dining_recommender/transport_planner)
        llm: LLM 实例

    Returns:
        绑定了工具的 LLM 实例
    """
    from tradingagents.tools.langchain_tools import (
        attraction_search_tool,
        restaurant_search_tool,
        weather_forecast_tool,
        route_planning_tool,
        get_tools_by_names
    )

    # 检查 LLM 是否支持 bind_tools
    if not hasattr(llm, 'bind_tools'):
        logger.warning(f"[{agent_name}] LLM 不支持 bind_tools 方法")
        return llm

    # 根据智能体类型选择工具
    if agent_name == "attraction_scheduler":
        # 景点排程师：需要天气和景点搜索工具
        tools = [
            weather_forecast_tool,
            attraction_search_tool
        ]
        logger.info(f"[景点排程师] 绑定工具: weather_forecast, attraction_search")

    elif agent_name == "dining_recommender":
        # 餐饮推荐师：需要餐厅搜索工具
        tools = [
            restaurant_search_tool
        ]
        logger.info(f"[餐饮推荐师] 绑定工具: restaurant_search")

    elif agent_name == "transport_planner":
        # 交通规划师：需要路径规划工具
        tools = [
            route_planning_tool
        ]
        logger.info(f"[交通规划师] 绑定工具: route_planning")

    else:
        logger.warning(f"[{agent_name}] 未知的智能体类型")
        return llm

    # 绑定工具到 LLM
    try:
        llm_with_tools = llm.bind_tools(tools)
        logger.info(f"[{agent_name}] 成功绑定 {len(tools)} 个工具")
        return llm_with_tools
    except Exception as e:
        logger.error(f"[{agent_name}] 工具绑定失败: {e}")
        return llm


# ============================================================
# 带工具的智能体节点函数
# ============================================================

def attraction_scheduler_node_with_tools(state: Dict) -> Dict:
    """
    景点排程师节点（带工具绑定）

    使用工具获取天气预报和景点信息
    """
    destination = state.get("selected_destination")
    dest_data = state.get("selected_destination_data", {})
    style_proposal = state.get("selected_style_proposal", {})
    days = state.get("days", 5)
    start_date = state.get("start_date")

    # 获取 LLM
    llm = state.get("_llm")
    if not llm:
        logger.error("[景点排程师] 缺少 LLM 实例")
        return state

    # 绑定工具
    llm_with_tools = bind_tools_to_agent("attraction_scheduler", llm)

    # 调用原有的排程函数（使用绑定了工具的 LLM）
    from .attraction_scheduler import schedule_attractions

    result = schedule_attractions(
        destination=destination,
        dest_data=dest_data,
        style_proposal=style_proposal,
        days=days,
        start_date=start_date,
        llm=llm_with_tools
    )

    # 更新状态
    from langchain_core.messages import AIMessage
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"景点排程完成: {days}天时间安排",
        name="AttractionScheduler"
    ))

    state["scheduled_attractions"] = result.get("scheduled_attractions", [])
    state["messages"] = messages

    return state


def dining_recommender_node_with_tools(state: Dict) -> Dict:
    """
    餐饮推荐师节点（带工具绑定）

    使用工具搜索餐厅
    """
    destination = state.get("selected_destination")
    scheduled_attractions = state.get("scheduled_attractions", [])
    user_portrait = state.get("user_portrait", {})
    budget_level = user_portrait.get("budget_level", "medium")

    # 获取 LLM
    llm = state.get("_llm")
    if not llm:
        logger.error("[餐饮推荐师] 缺少 LLM 实例")
        return state

    # 绑定工具
    llm_with_tools = bind_tools_to_agent("dining_recommender", llm)

    # 调用原有的推荐函数（使用绑定了工具的 LLM）
    from .dining_recommender import recommend_dining

    result = recommend_dining(
        destination=destination,
        scheduled_attractions=scheduled_attractions,
        budget_level=budget_level,
        llm=llm_with_tools
    )

    # 更新状态
    from langchain_core.messages import AIMessage
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"餐饮推荐完成",
        name="DiningRecommender"
    ))

    state["dining_plan"] = result
    state["messages"] = messages

    return state


def transport_planner_node_with_tools(state: Dict) -> Dict:
    """
    交通规划师节点（带工具绑定）

    使用工具规划路径
    """
    destination = state.get("selected_destination")
    scheduled_attractions = state.get("scheduled_attractions", [])
    user_portrait = state.get("user_portrait", {})
    budget_level = user_portrait.get("budget_level", "medium")

    # 获取 LLM
    llm = state.get("_llm")
    if not llm:
        logger.error("[交通规划师] 缺少 LLM 实例")
        return state

    # 绑定工具
    llm_with_tools = bind_tools_to_agent("transport_planner", llm)

    # 调用原有的规划函数（使用绑定了工具的 LLM）
    from .transport_planner import plan_transport

    result = plan_transport(
        destination=destination,
        scheduled_attractions=scheduled_attractions,
        budget_level=budget_level,
        llm=llm_with_tools
    )

    # 更新状态
    from langchain_core.messages import AIMessage
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"交通规划完成: 总费用{result.get('total_transport_cost', 0)}元",
        name="TransportPlanner"
    ))

    state["transport_plan"] = result
    state["messages"] = messages

    return state


# ============================================================
# 直接工具调用辅助函数
# ============================================================

def call_weather_tool(city: str, days: int = 7) -> Optional[Dict]:
    """
    直接调用天气工具（不通过 LLM）

    Args:
        city: 城市名称
        days: 天数

    Returns:
        天气预报数据
    """
    try:
        from tradingagents.tools.travel_tools import get_weather_forecast_tool

        tool = get_weather_forecast_tool()
        return tool.get_forecast(city=city, days=days)
    except Exception as e:
        logger.error(f"[天气工具] 调用失败: {e}")
        return None


def call_restaurant_tool(city: str, area: str = "", limit: int = 10) -> List[Dict]:
    """
    直接调用餐厅工具（不通过 LLM）

    Args:
        city: 城市名称
        area: 区域
        limit: 数量限制

    Returns:
        餐厅列表
    """
    try:
        from tradingagents.tools.travel_tools import get_restaurant_search_tool

        tool = get_restaurant_search_tool()
        return tool.search_restaurants(city=city, area=area, limit=limit)
    except Exception as e:
        logger.error(f"[餐厅工具] 调用失败: {e}")
        return []


def call_route_tool(origin: str, destination: str, city: str = "") -> Optional[Dict]:
    """
    直接调用路径规划工具（不通过 LLM）

    Args:
        origin: 出发地
        destination: 目的地
        city: 城市

    Returns:
        路径规划结果
    """
    try:
        from tradingagents.tools.travel_tools import get_route_planning_tool

        tool = get_route_planning_tool()
        return tool.plan_route(origin=origin, destination=destination, city=city)
    except Exception as e:
        logger.error(f"[路径规划工具] 调用失败: {e}")
        return None


# ============================================================
# 导出
# ============================================================

__all__ = [
    "bind_tools_to_agent",
    "attraction_scheduler_node_with_tools",
    "dining_recommender_node_with_tools",
    "transport_planner_node_with_tools",
    "call_weather_tool",
    "call_restaurant_tool",
    "call_route_tool",
]
