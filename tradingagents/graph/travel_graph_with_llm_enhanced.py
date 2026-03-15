"""
使用 LLM Analysts 的旅行规划图（增强版）

记录每个Agent的执行过程和分析结果，用于展示多智能体的协作过程
"""

from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage
from datetime import datetime
import time
import json

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
        self.setdefault("messages", [])
        self.setdefault("current_step", "init")
        self.setdefault("error", None)
        self.setdefault("agent_logs", [])  # 新增：Agent执行日志
        self.setdefault("plan_request_id", None)  # 新增：规划请求ID


# ============================================================
# Agent 日志记录工具
# ============================================================

def log_agent_execution(
    state: Dict,
    agent_name: str,
    agent_display_name: str,
    agent_type: str,
    execution_order: int,
    input_data: Dict,
    output_data: Dict = None,
    analysis_report: str = None,
    tool_calls: List = None,
    status: str = "completed",
    error_message: str = None,
    llm_provider: str = None,
    llm_model: str = None,
    duration_ms: int = None
) -> Dict:
    """记录Agent执行日志到状态中"""
    log_entry = {
        "agent_name": agent_name,
        "agent_display_name": agent_display_name,
        "agent_type": agent_type,
        "execution_order": execution_order,
        "status": status,
        "started_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat() if status == "completed" else None,
        "duration_ms": duration_ms,
        "input_data": input_data,
        "output_data": output_data or {},
        "analysis_report": analysis_report,
        "tool_calls": tool_calls or [],
        "error_message": error_message,
        "llm_provider": llm_provider,
        "llm_model": llm_model
    }

    state.setdefault("agent_logs", [])
    state["agent_logs"].append(log_entry)

    return log_entry


# ============================================================
# Agent 节点函数（带详细日志记录）
# ============================================================

def destination_classifier_node(state: Dict) -> Dict:
    """目的地分类节点"""
    start_time = time.time()

    destination = state.get("destination", "")
    input_data = {"destination": destination}

    try:
        classification = DestinationClassifier.classify(destination)

        # 生成分析报告
        report = f"""# 目的地分类报告

## 分类结果
- **目的地**: {destination}
- **类型**: {classification['type']}
- **英文名**: {classification.get('english_name', 'N/A')}
- **所属区域**: {classification.get('region', 'N/A')}

## 分析说明
根据目的地名称，系统自动识别该目的地为{'国内' if classification['type'] == 'domestic' else '国际'}目的地。
{'国内目的地将使用高德地图等国内数据源，国际目的地将使用SerpAPI等国际数据源。' if classification['type'] else ''}

## 数据源选择
- {'高德地图API (景点、天气、交通)' if classification['type'] == 'domestic' else 'SerpAPI (Google搜索) + Open-Meteo (天气)'}

---

*执行时间: {int((time.time() - start_time) * 1000)}ms*
"""

        # 记录日志
        log_agent_execution(
            state=state,
            agent_name="destination_classifier",
            agent_display_name="目的地分类器",
            agent_type="classifier",
            execution_order=len(state.get("agent_logs", [])) + 1,
            input_data=input_data,
            output_data=classification,
            analysis_report=report,
            status="completed",
            duration_ms=int((time.time() - start_time) * 1000)
        )

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

    except Exception as e:
        logger.error(f"[目的地分类器] 执行失败: {e}")
        log_agent_execution(
            state=state,
            agent_name="destination_classifier",
            agent_display_name="目的地分类器",
            agent_type="classifier",
            execution_order=len(state.get("agent_logs", [])) + 1,
            input_data=input_data,
            status="error",
            error_message=str(e),
            duration_ms=int((time.time() - start_time) * 1000)
        )
        raise


def data_collector_node(state: Dict) -> Dict:
    """数据收集节点"""
    start_time = time.time()

    destination = state.get("destination", "")
    days = state.get("days", 5)
    interest_type = state.get("interest_type", "")

    input_data = {
        "destination": destination,
        "days": days,
        "interest_type": interest_type
    }

    try:
        logger.info(f"[数据收集器] 开始收集 {destination} 的数据")

        provider = UnifiedDataProvider()

        # 收集数据
        attractions_result = provider.search_attractions(destination, interest_type)
        weather_result = provider.get_weather(destination, min(days, 7))
        transport_result = provider.estimate_transport_cost("中国", destination)

        # 生成分析报告
        attractions_count = attractions_result.get('count', 0)
        weather_days = weather_result.get('count', 0)

        report = f"""# 数据收集报告

## 收集概况
- **目的地**: {destination}
- **行程天数**: {days}天
- **兴趣类型**: {interest_type or '全部'}

## 数据收集结果

### 1. 景点数据
- **找到景点数**: {attractions_count}个
- **数据来源**: {'高德地图API' if state.get('destination_type') == 'domestic' else 'SerpAPI/Google'}

### 2. 天气数据
- **预报天数**: {weather_days}天
- **数据来源**: Open-Meteo

### 3. 交通数据
- **数据来源**: {'高德地图' if state.get('destination_type') == 'domestic' else '估算'}
- **包含**: 预估费用、出行方式建议

## 数据质量评估
{'✅ 数据完整，可以进行下一步分析' if attractions_count > 0 else '⚠️ 景点数据较少，建议扩大搜索范围'}

---

*执行时间: {int((time.time() - start_time) * 1000)}ms*
"""

        messages = state.get("messages", [])
        messages.append(AIMessage(
            content=f"数据收集完成: 找到 {attractions_count} 个景点",
            name="DataCollector"
        ))

        # 记录日志
        log_agent_execution(
            state=state,
            agent_name="data_collector",
            agent_display_name="数据收集器",
            agent_type="collector",
            execution_order=len(state.get("agent_logs", [])) + 1,
            input_data=input_data,
            output_data={
                "attractions": attractions_result,
                "weather": weather_result,
                "transport": transport_result
            },
            analysis_report=report,
            status="completed",
            duration_ms=int((time.time() - start_time) * 1000)
        )

        state["attractions"] = attractions_result
        state["weather_forecast"] = weather_result
        state["transport_info"] = transport_result
        state["messages"] = messages
        state["current_step"] = "data_collected"

        return state

    except Exception as e:
        logger.error(f"[数据收集器] 执行失败: {e}")
        log_agent_execution(
            state=state,
            agent_name="data_collector",
            agent_display_name="数据收集器",
            agent_type="collector",
            execution_order=len(state.get("agent_logs", [])) + 1,
            input_data=input_data,
            status="error",
            error_message=str(e),
            duration_ms=int((time.time() - start_time) * 1000)
        )
        raise


def attraction_analyst_node(state: Dict) -> Dict:
    """景点分析节点（使用 LLM）"""
    start_time = time.time()
    llm = state.get("_llm")

    input_data = {
        "destination": state.get("destination"),
        "days": state.get("days"),
        "interest_type": state.get("interest_type"),
        "attractions_data": state.get("attractions", {}).get("data", [])[:5]  # 前5个景点
    }

    if not llm:
        logger.warning("[景点分析师] 未配置 LLM，跳过")
        log_agent_execution(
            state=state,
            agent_name="attraction_analyst",
            agent_display_name="景点分析师",
            agent_type="analyst",
            execution_order=len(state.get("agent_logs", [])) + 1,
            input_data=input_data,
            status="skipped",
            analysis_report="## 景点分析\n\n⚠️ 未配置LLM，跳过智能分析。",
            duration_ms=int((time.time() - start_time) * 1000)
        )
        return state

    agent = create_attraction_analyst(llm)

    try:
        result = agent(state)

        # 生成分析报告
        attractions = result.get("recommended_attractions", [])
        report = f"""# 景点分析报告

## 分析概述
- **目的地**: {state.get('destination')}
- **推荐景点数**: {len(attractions)}个
- **兴趣类型**: {state.get('interest_type', '全部')}

## 推荐景点列表

"""
        for i, attr in enumerate(attractions[:10], 1):
            report += f"""
### {i}. {attr.get('name', '未知')}
- **描述**: {attr.get('description', '暂无描述')[:100]}...
- **推荐理由**: {attr.get('recommendation_reason', '符合您的兴趣偏好')}
- **预计游览时间**: {attr.get('recommended_duration', '2-3小时')}
- **建议**: {attr.get('tips', '注意开放时间')}

"""

        report += f"""
## 分析总结
基于您的兴趣偏好（{state.get('interest_type', '全部')}），为您推荐了以上{len(attractions)}个景点。
这些景点是根据真实数据、用户评价和专业推荐综合筛选得出。

---

*执行时间: {int((time.time() - start_time) * 1000)}ms*
*LLM模型: {state.get('_llm_model', 'unknown')}*
"""

        # 记录日志
        log_agent_execution(
            state=state,
            agent_name="attraction_analyst",
            agent_display_name="景点分析师",
            agent_type="analyst",
            execution_order=len(state.get("agent_logs", [])) + 1,
            input_data=input_data,
            output_data={"recommended_attractions": attractions},
            analysis_report=report,
            status="completed",
            llm_provider=state.get("_llm_provider"),
            llm_model=state.get("_llm_model"),
            duration_ms=int((time.time() - start_time) * 1000)
        )

        messages = state.get("messages", [])
        messages.append(AIMessage(
            content=f"景点分析完成",
            name="AttractionAnalyst"
        ))
        result["messages"] = messages

        return result

    except Exception as e:
        logger.error(f"[景点分析师] 执行失败: {e}")
        log_agent_execution(
            state=state,
            agent_name="attraction_analyst",
            agent_display_name="景点分析师",
            agent_type="analyst",
            execution_order=len(state.get("agent_logs", [])) + 1,
            input_data=input_data,
            status="error",
            error_message=str(e),
            llm_provider=state.get("_llm_provider"),
            llm_model=state.get("_llm_model"),
            duration_ms=int((time.time() - start_time) * 1000)
        )
        return state


def itinerary_planner_node(state: Dict) -> Dict:
    """行程规划节点（使用 LLM）"""
    start_time = time.time()
    llm = state.get("_llm")

    input_data = {
        "destination": state.get("destination"),
        "days": state.get("days"),
        "budget": state.get("budget"),
        "travelers": state.get("travelers"),
        "travel_style": state.get("travel_style")
    }

    if not llm:
        logger.warning("[行程规划师] 未配置 LLM，使用简化方案")
        from tradingagents.agents.analysts.itinerary_planner import generate_simple_itinerary

        itinerary = generate_simple_itinerary(
            state.get("destination", ""),
            state.get("days", 5),
            state.get("budget", "medium"),
            state.get("travelers", 2)
        )

        report = f"""# 行程规划报告

## 规划概述
- **目的地**: {state.get('destination')}
- **行程天数**: {state.get('days')}天
- **预算级别**: {state.get('budget')}
- **旅行人数**: {state.get('travelers')}人

## 每日行程安排
（简化版，未使用LLM生成）

⚠️ 由于未配置LLM，使用了基础行程模板。

---

*执行时间: {int((time.time() - start_time) * 1000)}ms*
"""

        log_agent_execution(
            state=state,
            agent_name="itinerary_planner",
            agent_display_name="行程规划师",
            agent_type="planner",
            execution_order=len(state.get("agent_logs", [])) + 1,
            input_data=input_data,
            output_data={"itinerary": itinerary},
            analysis_report=report,
            status="completed",
            duration_ms=int((time.time() - start_time) * 1000)
        )

        state["detailed_itinerary"] = itinerary
        state["current_step"] = "itinerary_planned"
        return state

    agent = create_itinerary_planner(llm)

    try:
        result = agent(state)

        # 生成分析报告
        itinerary = result.get("detailed_itinerary", {})
        daily_itinerary = itinerary.get("daily_itinerary", [])

        report = f"""# 行程规划报告

## 规划概述
- **目的地**: {state.get('destination')}
- **行程天数**: {state.get('days')}天
- **预算级别**: {state.get('budget')}
- **旅行人数**: {state.get('travelers')}人
- **旅行风格**: {state.get('travel_style', '探索')}

## 详细行程

"""
        for day_plan in daily_itinerary[:7]:
            report += f"""
### 第{day_plan.get('day', '?')}天: {day_plan.get('theme', '探索')}
- **上午**: {day_plan.get('morning', {}).get('activity', '自由活动')}
- **午餐**: {day_plan.get('lunch', {}).get('activity', '用餐')}
- **下午**: {day_plan.get('afternoon', {}).get('activity', '继续探索')}
- **晚餐**: {day_plan.get('dinner', {}).get('activity', '用餐')}
- **晚上**: {day_plan.get('evening', {}).get('activity', '休息')}

"""

        report += f"""
## 规划说明
此行程根据您的偏好精心设计，平衡了景点游览、休息时间和用餐安排。
每日行程合理安排，避免过度疲劳。

---

*执行时间: {int((time.time() - start_time) * 1000)}ms*
*LLM模型: {state.get('_llm_model', 'unknown')}*
"""

        # 记录日志
        log_agent_execution(
            state=state,
            agent_name="itinerary_planner",
            agent_display_name="行程规划师",
            agent_type="planner",
            execution_order=len(state.get("agent_logs", [])) + 1,
            input_data=input_data,
            output_data={"itinerary": itinerary},
            analysis_report=report,
            status="completed",
            llm_provider=state.get("_llm_provider"),
            llm_model=state.get("_llm_model"),
            duration_ms=int((time.time() - start_time) * 1000)
        )

        messages = state.get("messages", [])
        messages.append(AIMessage(
            content=f"行程规划完成: {state.get('days')}天详细行程",
            name="ItineraryPlanner"
        ))
        result["messages"] = messages

        return result

    except Exception as e:
        logger.error(f"[行程规划师] 执行失败: {e}")
        log_agent_execution(
            state=state,
            agent_name="itinerary_planner",
            agent_display_name="行程规划师",
            agent_type="planner",
            execution_order=len(state.get("agent_logs", [])) + 1,
            input_data=input_data,
            status="error",
            error_message=str(e),
            llm_provider=state.get("_llm_provider"),
            llm_model=state.get("_llm_model"),
            duration_ms=int((time.time() - start_time) * 1000)
        )
        return state


def budget_analyst_node(state: Dict) -> Dict:
    """预算分析节点（使用 LLM）"""
    start_time = time.time()
    llm = state.get("_llm")

    input_data = {
        "destination": state.get("destination"),
        "days": state.get("days"),
        "budget": state.get("budget"),
        "travelers": state.get("travelers"),
        "transport_info": state.get("transport_info", {})
    }

    if not llm:
        logger.warning("[预算分析师] 未配置 LLM，使用简化方案")
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

        breakdown = {
            "transportation": {"amount": int(transport_cost)},
            "accommodation": {"amount": int(accommodation)},
            "meals": {"amount": int(meals)},
            "attractions": {"amount": int(attractions)},
            "miscellaneous": {"amount": int(misc)},
            "total_budget": int(total)
        }

        report = f"""# 预算分析报告

## 费用概述
- **目的地**: {state.get('destination')}
- **行程天数**: {days}天
- **出行人数**: {travelers}人
- **预算级别**: {budget}

## 费用明细

| 项目 | 金额(元) | 占比 |
|------|----------|------|
| 交通 | {int(transport_cost)} | {int(transport_cost/total*100)}% |
| 住宿 | {int(accommodation)} | {int(accommodation/total*100)}% |
| 餐饮 | {int(meals)} | {int(meals/total*100)}% |
| 景点 | {int(attractions)} | {int(attractions/total*100)}% |
| 其他 | {int(misc)} | {int(misc/total*100)}% |
| **总计** | **{int(total)}** | 100% |

## 分析建议
- **人均费用**: {int(total/travelers)}元
- **日均费用**: {int(total/days)}元

⚠️ 此为基础估算，实际费用因季节、预订时间等因素可能有所不同。

---

*执行时间: {int((time.time() - start_time) * 1000)}ms*
"""

        log_agent_execution(
            state=state,
            agent_name="budget_analyst",
            agent_display_name="预算分析师",
            agent_type="analyst",
            execution_order=len(state.get("agent_logs", [])) + 1,
            input_data=input_data,
            output_data={"budget_breakdown": breakdown},
            analysis_report=report,
            status="completed",
            duration_ms=int((time.time() - start_time) * 1000)
        )

        state["budget_breakdown"] = breakdown
        state["current_step"] = "budget_analyzed"
        return state

    agent = create_budget_analyst(llm)

    try:
        result = agent(state)
        breakdown = result.get("budget_breakdown", {})

        # 生成分析报告
        report = f"""# 预算分析报告

## 费用概述
- **目的地**: {state.get('destination')}
- **行程天数**: {state.get('days')}天
- **出行人数**: {state.get('travelers')}人
- **预算级别**: {state.get('budget')}
- **总预算**: {breakdown.get('total_budget', 0)}元

## 费用明细

| 项目 | 金额(元) | 说明 |
|------|----------|------|
| 交通 | {breakdown.get('transportation', {}).get('amount', 0)} | {breakdown.get('transportation', {}).get('description', '交通费用')} |
| 住宿 | {breakdown.get('accommodation', {}).get('amount', 0)} | {breakdown.get('accommodation', {}).get('description', '住宿费用')} |
| 餐饮 | {breakdown.get('meals', {}).get('amount', 0)} | {breakdown.get('meals', {}).get('description', '餐饮费用')} |
| 景点 | {breakdown.get('attractions', {}).get('amount', 0)} | {breakdown.get('attractions', {}).get('description', '景点费用')} |
| 其他 | {breakdown.get('miscellaneous', {}).get('amount', 0)} | {breakdown.get('miscellaneous', {}).get('description', '其他费用')} |

## 分析评估
- **预算评级**: {breakdown.get('budget_assessment', '合理')}
- **日均费用**: {breakdown.get('daily_average', 0)}元
- **人均费用**: {breakdown.get('per_person_average', 0)}元

## 省钱建议
{chr(10).join(f"- {tip}" for tip in breakdown.get('money_saving_tips', [])[:5])}

---

*执行时间: {int((time.time() - start_time) * 1000)}ms*
*LLM模型: {state.get('_llm_model', 'unknown')}*
"""

        # 记录日志
        log_agent_execution(
            state=state,
            agent_name="budget_analyst",
            agent_display_name="预算分析师",
            agent_type="analyst",
            execution_order=len(state.get("agent_logs", [])) + 1,
            input_data=input_data,
            output_data={"budget_breakdown": breakdown},
            analysis_report=report,
            status="completed",
            llm_provider=state.get("_llm_provider"),
            llm_model=state.get("_llm_model"),
            duration_ms=int((time.time() - start_time) * 1000)
        )

        messages = state.get("messages", [])
        messages.append(AIMessage(
            content=f"预算分析完成: 预计总费用",
            name="BudgetAnalyst"
        ))
        result["messages"] = messages

        return result

    except Exception as e:
        logger.error(f"[预算分析师] 执行失败: {e}")
        log_agent_execution(
            state=state,
            agent_name="budget_analyst",
            agent_display_name="预算分析师",
            agent_type="analyst",
            execution_order=len(state.get("agent_logs", [])) + 1,
            input_data=input_data,
            status="error",
            error_message=str(e),
            llm_provider=state.get("_llm_provider"),
            llm_model=state.get("_llm_model"),
            duration_ms=int((time.time() - start_time) * 1000)
        )
        return state


# ============================================================
# 旅行规划图类（增强版）
# ============================================================

class TravelAgentsGraphWithLLMEnhanced:
    """
    旅行规划 Agent 系统（增强版）

    记录每个Agent的执行过程和分析结果
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

        # 创建 LLM
        self.llm = create_llm_by_provider(
            provider=llm_provider,
            model=llm_model,
            backend_url="",
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

        logger.info(f"[TravelAgentsGraphWithLLMEnhanced] 初始化完成")

    def plan(
        self,
        destination: str,
        days: int = 5,
        budget: str = "medium",
        travelers: int = 2,
        interest_type: str = "",
        selected_style: str = ""
    ) -> Dict[str, Any]:
        """规划旅行（带详细日志）"""
        logger.info(f"[TravelAgentsGraphWithLLMEnhanced] 开始规划: {destination}, {days}天")

        # 初始化状态
        initial_state = TravelPlanningState({
            "destination": destination,
            "days": days,
            "budget": budget,
            "travelers": travelers,
            "interest_type": interest_type,
            "selected_style": selected_style,
            "_llm": self.llm,
            "_llm_provider": llm_provider,
            "_llm_model": llm_model,
            "current_step": "init",
            "agent_logs": []
        })

        # 运行图
        result = self.graph.invoke(initial_state)

        logger.info(f"[TravelAgentsGraphWithLLMEnhanced] 规划完成")
        logger.info(f"[TravelAgentsGraphWithLLMEnhanced] Agent执行日志数量: {len(result.get('agent_logs', []))}")

        return result


def create_travel_graph_with_llm_enhanced(
    llm_provider: str = "deepseek",
    llm_model: str = "deepseek-chat",
    **kwargs
) -> TravelAgentsGraphWithLLMEnhanced:
    """创建带详细日志的旅行规划图"""
    return TravelAgentsGraphWithLLMEnhanced(
        llm_provider=llm_provider,
        llm_model=llm_model,
        **kwargs
    )
