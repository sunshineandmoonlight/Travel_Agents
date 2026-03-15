"""
分阶段旅行规划消息流图 (v3.4)

基于LangGraph的状态流架构，将函数式调用改造为消息传递模式
支持Group B和Group C的并行执行优化
"""
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage

import logging
logger = logging.getLogger('travel_agents')

# ============================================================
# 并行执行开关
# ============================================================

# 设置为 True 启用并行执行，False 使用顺序执行
ENABLE_PARALLEL_EXECUTION = True

# ============================================================
# AgentState 定义
# ============================================================

class StagedTravelState(TypedDict):
    """分阶段旅行规划状态"""
    # 消息历史（LangGraph标准）
    messages: Annotated[List[BaseMessage], "消息历史"]

    # 当前执行的智能体
    current_agent: str

    # 当前阶段
    current_stage: str  # "init" | "requirement_analysis" | "destination_matching" | "style_design" | "guide_generation" | "complete"

    # 用户输入
    user_requirements: Dict[str, Any]

    # 组A输出：需求分析
    user_portrait: Optional[Dict[str, Any]]

    # 组A输出：匹配的目的地
    matched_destinations: Optional[List[Dict[str, Any]]]

    # 组A输出：排名后的目的地
    ranked_destinations: Optional[List[Dict[str, Any]]]

    # 用户选择的目的地
    selected_destination: Optional[str]

    # 组B输出：风格方案
    style_proposals: Optional[List[Dict[str, Any]]]

    # 用户选择的风格
    selected_style: Optional[str]

    # 组C输出：详细攻略
    detailed_guide: Optional[Dict[str, Any]]

    # 错误信息
    error: Optional[str]

    # LLM实例（内部使用）
    _llm: Optional[Any]


# ============================================================
# 组A: 需求分析与目的地推荐节点
# ============================================================

def user_requirement_analyst_node(state: StagedTravelState) -> StagedTravelState:
    """
    A1: 需求分析智能体节点

    分析用户需求，生成用户画像
    """
    from tradingagents.agents.group_a import UserRequirementAnalyst

    llm = state.get("_llm")
    requirements = state.get("user_requirements", {})

    logger.info(f"[A1-节点] 需求分析: {requirements}")

    try:
        # 使用通信式智能体
        agent = UserRequirementAnalyst(llm=llm)
        agent.initialize()

        portrait = agent.analyze_requirements(requirements)

        agent.shutdown()

        # 添加消息到历史
        messages = state.get("messages", [])
        messages.append(AIMessage(
            content=f"需求分析完成: {portrait.get('travel_type', '')}, {portrait.get('pace_preference', '')}",
            name="UserRequirementAnalyst"
        ))

        return {
            **state,
            "user_portrait": portrait,
            "current_agent": "destination_matcher",
            "current_stage": "destination_matching",
            "messages": messages
        }

    except Exception as e:
        logger.error(f"[A1-节点] 需求分析失败: {e}")
        return {
            **state,
            "error": f"需求分析失败: {str(e)}",
            "messages": state.get("messages", []) + [AIMessage(content=f"需求分析失败: {e}", name="UserRequirementAnalyst")]
        }


def destination_matcher_node(state: StagedTravelState) -> StagedTravelState:
    """
    A2: 地区匹配智能体节点

    根据用户画像匹配目的地
    """
    from tradingagents.agents.group_a import DestinationMatcher

    llm = state.get("_llm")
    user_portrait = state.get("user_portrait", {})
    requirements = state.get("user_requirements", {})
    travel_scope = requirements.get("travel_scope", "domestic")

    logger.info(f"[A2-节点] 地区匹配: {travel_scope}")

    try:
        agent = DestinationMatcher(llm=llm)
        agent.initialize()

        candidates = agent.match_destinations(user_portrait, travel_scope)

        agent.shutdown()

        messages = state.get("messages", [])
        messages.append(AIMessage(
            content=f"地区匹配完成: 找到 {len(candidates)} 个目的地",
            name="DestinationMatcher"
        ))

        return {
            **state,
            "matched_destinations": candidates,
            "current_agent": "ranking_scorer",
            "messages": messages
        }

    except Exception as e:
        logger.error(f"[A2-节点] 地区匹配失败: {e}")
        return {
            **state,
            "error": f"地区匹配失败: {str(e)}",
            "messages": state.get("messages", []) + [AIMessage(content=f"地区匹配失败: {e}", name="DestinationMatcher")]
        }


def ranking_scorer_node(state: StagedTravelState) -> StagedTravelState:
    """
    A3: 排名打分智能体节点

    对候选目的地排名，返回Top N
    """
    from tradingagents.agents.group_a import RankingScorer

    llm = state.get("_llm")
    candidates = state.get("matched_destinations", [])
    user_portrait = state.get("user_portrait", {})
    top_n = state.get("user_requirements", {}).get("destination_count", 4)

    logger.info(f"[A3-节点] 排名打分: {len(candidates)} 个候选 -> Top {top_n}")

    try:
        agent = RankingScorer(llm=llm)
        agent.initialize()

        ranked = agent.rank_and_select_top(candidates, user_portrait, top_n)

        agent.shutdown()

        messages = state.get("messages", [])
        destinations_str = ", ".join([d["destination"] for d in ranked])
        messages.append(AIMessage(
            content=f"排名完成: Top {top_n} 目的地 - {destinations_str}",
            name="RankingScorer"
        ))

        return {
            **state,
            "ranked_destinations": ranked,
            "current_agent": "style_designer",
            "current_stage": "style_design",
            "messages": messages
        }

    except Exception as e:
        logger.error(f"[A3-节点] 排名打分失败: {e}")
        return {
            **state,
            "error": f"排名打分失败: {str(e)}",
            "messages": state.get("messages", []) + [AIMessage(content=f"排名打分失败: {e}", name="RankingScorer")]
        }


# ============================================================
# 组B: 风格方案设计节点
# ============================================================

def style_designer_node(state: StagedTravelState) -> StagedTravelState:
    """
    组B智能体节点：生成4种风格方案

    根据配置选择并行或顺序执行
    """
    # 根据配置选择执行方式
    if ENABLE_PARALLEL_EXECUTION:
        return _parallel_style_designer_impl(state)
    else:
        return _sequential_style_designer_impl(state)


def _parallel_style_designer_impl(state: StagedTravelState) -> StagedTravelState:
    """并行执行4个风格设计师"""
    from tradingagents.graph.parallel_execution import ParallelStyleDesigners

    llm = state.get("_llm")
    selected_destination = state.get("selected_destination")
    user_portrait = state.get("user_portrait", {})
    requirements = state.get("user_requirements", {})
    days = requirements.get("days", 5)

    dest_data = {
        "tags": user_portrait.get("primary_interests", []),
        "highlights": [],
        "budget_level": {"medium": 500}
    }

    logger.info(f"[B-节点-并行] 风格方案设计: {selected_destination}")

    try:
        parallel_designers = ParallelStyleDesigners(llm)
        proposals = parallel_designers.create_all_proposals(
            selected_destination, dest_data, user_portrait, days
        )

        messages = state.get("messages", [])
        styles_str = ", ".join([p.get("style_name", "") for p in proposals])
        messages.append(AIMessage(
            content=f"风格方案设计完成(并行): {styles_str}",
            name="StyleDesigner"
        ))

        return {
            **state,
            "style_proposals": proposals,
            "current_agent": "guide_generator",
            "current_stage": "guide_generation",
            "messages": messages
        }

    except Exception as e:
        logger.error(f"[B-节点-并行] 风格方案设计失败: {e}")
        return {
            **state,
            "error": f"风格方案设计失败: {str(e)}",
            "messages": state.get("messages", []) + [AIMessage(content=f"风格方案设计失败: {e}", name="StyleDesigner")]
        }


def _sequential_style_designer_impl(state: StagedTravelState) -> StagedTravelState:
    """顺序执行4个风格设计师（降级方案）"""
    from tradingagents.agents.group_b import (
        ImmersiveDesignerAgent,
        ExplorationDesignerAgent,
        RelaxationDesignerAgent,
        HiddenGemDesignerAgent
    )

    llm = state.get("_llm")
    selected_destination = state.get("selected_destination")
    user_portrait = state.get("user_portrait", {})
    requirements = state.get("user_requirements", {})
    days = requirements.get("days", 5)

    dest_data = {
        "tags": user_portrait.get("primary_interests", []),
        "highlights": [],
        "budget_level": {"medium": 500}
    }

    logger.info(f"[B-节点-顺序] 风格方案设计: {selected_destination}")

    try:
        designers = [
            ImmersiveDesignerAgent(llm=llm),
            ExplorationDesignerAgent(llm=llm),
            RelaxationDesignerAgent(llm=llm),
            HiddenGemDesignerAgent(llm=llm)
        ]

        proposals = []
        for designer in designers:
            designer.initialize()
            proposal = designer.create_proposal(selected_destination, dest_data, user_portrait, days)
            proposals.append(proposal)
            designer.shutdown()

        messages = state.get("messages", [])
        styles_str = ", ".join([p.get("style_name", "") for p in proposals])
        messages.append(AIMessage(
            content=f"风格方案设计完成(顺序): {styles_str}",
            name="StyleDesigner"
        ))

        return {
            **state,
            "style_proposals": proposals,
            "current_agent": "guide_generator",
            "current_stage": "guide_generation",
            "messages": messages
        }

    except Exception as e:
        logger.error(f"[B-节点-顺序] 风格方案设计失败: {e}")
        return {
            **state,
            "error": f"风格方案设计失败: {str(e)}",
            "messages": state.get("messages", []) + [AIMessage(content=f"风格方案设计失败: {e}", name="StyleDesigner")]
        }


# ============================================================
# 组C: 详细攻略生成节点
# ============================================================

def guide_generator_node(state: StagedTravelState) -> StagedTravelState:
    """
    组C智能体节点：生成详细攻略

    包括景点排程、交通规划、餐饮推荐、住宿建议
    根据配置选择并行或顺序执行
    """
    # 根据配置选择执行方式
    if ENABLE_PARALLEL_EXECUTION:
        return _parallel_guide_generator_impl(state)
    else:
        return _sequential_guide_generator_impl(state)


def _parallel_guide_generator_impl(state: StagedTravelState) -> StagedTravelState:
    """并行执行Group C智能体"""
    from tradingagents.graph.parallel_execution import ParallelGroupC
    from langchain_core.messages import AIMessage

    llm = state.get("_llm")
    selected_destination = state.get("selected_destination")
    selected_style = state.get("selected_style", "immersive")
    user_portrait = state.get("user_portrait", {})
    requirements = state.get("user_requirements", {})
    days = requirements.get("days", 5)
    start_date = requirements.get("start_date", "2024-04-01")

    style_proposals = state.get("style_proposals", [])
    style_proposal = next((p for p in style_proposals if p.get("style_type") == selected_style), style_proposals[0] if style_proposals else {})

    dest_data = {
        "tags": user_portrait.get("primary_interests", []),
        "highlights": [],
        "budget_level": {"medium": 500}
    }

    logger.info(f"[C-节点-并行] 详细攻略生成: {selected_destination} - {selected_style}")

    try:
        parallel_c = ParallelGroupC(llm)
        results = parallel_c.execute_all(
            selected_destination, dest_data, style_proposal, days, start_date, user_portrait
        )

        messages = state.get("messages", [])
        messages.append(AIMessage(
            content=f"详细攻略生成完成(并行): {days}天行程",
            name="GuideGenerator"
        ))

        return {
            **state,
            "scheduled_attractions": results.get("scheduled_attractions"),
            "accommodation_plan": results.get("accommodation_plan"),
            "transport_plan": results.get("transport_plan"),
            "dining_plan": results.get("dining_plan"),
            "detailed_guide": results,
            "current_agent": "complete",
            "current_stage": "complete",
            "messages": messages
        }

    except Exception as e:
        logger.error(f"[C-节点-并行] 详细攻略生成失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            **state,
            "error": f"详细攻略生成失败: {str(e)}",
            "messages": state.get("messages", []) + [AIMessage(content=f"详细攻略生成失败: {e}", name="GuideGenerator")]
        }


def _sequential_guide_generator_impl(state: StagedTravelState) -> StagedTravelState:
    """顺序执行Group C智能体（降级方案）"""
    from tradingagents.agents.group_c import (
        AttractionSchedulerAgent,
        TransportPlannerAgent,
        DiningRecommenderAgent,
        AccommodationAdvisorAgent,
        LLMGuideWriterAgent
    )

    llm = state.get("_llm")
    selected_destination = state.get("selected_destination")
    selected_style = state.get("selected_style", "immersive")
    user_portrait = state.get("user_portrait", {})
    requirements = state.get("user_requirements", {})
    days = requirements.get("days", 5)
    start_date = requirements.get("start_date", "2024-04-01")

    # 获取选中的风格方案
    style_proposals = state.get("style_proposals", [])
    style_proposal = next((p for p in style_proposals if p.get("style_type") == selected_style), style_proposals[0] if style_proposals else {})

    # 模拟目的地数据
    dest_data = {
        "tags": user_portrait.get("primary_interests", []),
        "highlights": [],
        "budget_level": {"medium": 500}
    }

    budget_level = user_portrait.get("budget_level", "medium")
    travelers = user_portrait.get("total_travelers", 2)

    logger.info(f"[C-节点-顺序] 详细攻略生成: {selected_destination} - {selected_style}")

    try:
        # C1: 景点排程
        scheduler = AttractionSchedulerAgent(llm=llm)
        scheduler.initialize()
        scheduled_attractions = scheduler.create_schedule(
            selected_destination, dest_data, style_proposal, days, start_date
        )
        scheduler.shutdown()

        # C4: 住宿推荐（可以在顺序模式下与C1之后执行）
        accommodation_advisor = AccommodationAdvisorAgent(llm=llm)
        accommodation_advisor.initialize()
        accommodation_plan = accommodation_advisor.create_recommendations(
            selected_destination, days, budget_level, travelers
        )
        accommodation_advisor.shutdown()

        # C2: 交通规划
        transport_planner = TransportPlannerAgent(llm=llm)
        transport_planner.initialize()
        transport_plan = transport_planner.create_plan(
            selected_destination, scheduled_attractions, budget_level
        )
        transport_planner.shutdown()

        # C3: 餐饮推荐
        dining_recommender = DiningRecommenderAgent(llm=llm)
        dining_recommender.initialize()
        dining_plan = dining_recommender.create_recommendations(
            selected_destination, scheduled_attractions, budget_level
        )
        dining_recommender.shutdown()

        # C5: 攻略生成
        guide_writer = LLMGuideWriterAgent(llm=llm)
        guide_writer.initialize()

        user_requirements = {
            "user_portrait": user_portrait,
            "start_date": start_date
        }

        detailed_guide = guide_writer.write_guide(
            selected_destination, style_proposal, scheduled_attractions,
            transport_plan, dining_plan, accommodation_plan, user_requirements
        )
        guide_writer.shutdown()

        messages = state.get("messages", [])
        messages.append(AIMessage(
            content=f"详细攻略生成完成(顺序): {selected_destination} {days}天行程",
            name="GuideGenerator"
        ))

        return {
            **state,
            "scheduled_attractions": scheduled_attractions,
            "accommodation_plan": accommodation_plan,
            "transport_plan": transport_plan,
            "dining_plan": dining_plan,
            "detailed_guide": detailed_guide,
            "current_agent": "complete",
            "current_stage": "complete",
            "messages": messages
        }

    except Exception as e:
        logger.error(f"[C-节点-顺序] 详细攻略生成失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            **state,
            "error": f"详细攻略生成失败: {str(e)}",
            "messages": state.get("messages", []) + [AIMessage(content=f"详细攻略生成失败: {e}", name="GuideGenerator")]
        }


# ============================================================
# 条件路由函数
# ============================================================

def should_continue_to_style_design(state: StagedTravelState) -> str:
    """判断是否继续到风格设计阶段"""
    if state.get("error"):
        return "error"
    if state.get("selected_destination"):
        return "style_design"
    return "wait_for_selection"


def should_continue_to_guide_generation(state: StagedTravelState) -> str:
    """判断是否继续到攻略生成阶段"""
    if state.get("error"):
        return "error"
    if state.get("selected_style"):
        return "guide_generation"
    return "wait_for_selection"


# ============================================================
# StateGraph 构建函数
# ============================================================

def create_staged_travel_graph(
    llm=None,
    destination: str = "",
    travel_scope: str = "domestic",
    days: int = 5,
    budget: str = "medium",
    interests: List[str] = None,
    travelers: int = 2
) -> StateGraph:
    """
    创建分阶段旅行规划消息流图

    Args:
        llm: LLM实例
        destination: 目的地
        travel_scope: 旅行范围 (domestic/international)
        days: 天数
        budget: 预算等级
        interests: 兴趣列表
        travelers: 旅行人数

    Returns:
        StateGraph实例
    """
    # 创建状态图
    workflow = StateGraph(StagedTravelState)

    # 添加节点
    workflow.add_node("user_requirement_analyst", user_requirement_analyst_node)
    workflow.add_node("destination_matcher", destination_matcher_node)
    workflow.add_node("ranking_scorer", ranking_scorer_node)
    workflow.add_node("style_designer", style_designer_node)
    workflow.add_node("guide_generator", guide_generator_node)

    # 设置入口点
    workflow.set_entry_point("user_requirement_analyst")

    # 添加边 - 组A流程（串行）
    workflow.add_edge("user_requirement_analyst", "destination_matcher")
    workflow.add_edge("destination_matcher", "ranking_scorer")

    # 添加条件边 - 排名完成后等待用户选择目的地，然后到风格设计
    workflow.add_conditional_edges(
        "ranking_scorer",
        should_continue_to_style_design,
        {
            "style_design": "style_designer",
            "wait_for_selection": END,  # 等待用户输入
            "error": END
        }
    )

    # 添加条件边 - 风格设计完成后等待用户选择风格，然后到攻略生成
    workflow.add_conditional_edges(
        "style_designer",
        should_continue_to_guide_generation,
        {
            "guide_generation": "guide_generator",
            "wait_for_selection": END,  # 等待用户输入
            "error": END
        }
    )

    # 攻略生成完成后结束
    workflow.add_edge("guide_generator", END)

    return workflow


# ============================================================
# 执行函数
# ============================================================

def run_staged_travel_graph(
    requirements: Dict[str, Any],
    llm=None,
    selected_destination: str = None,
    selected_style: str = None
) -> Dict[str, Any]:
    """
    运行分阶段旅行规划图

    Args:
        requirements: 用户需求
        llm: LLM实例
        selected_destination: 用户选择的目的地（可选）
        selected_style: 用户选择的风格（可选）

    Returns:
        执行结果
    """
    # 创建图
    graph = create_staged_travel_graph(llm=llm)

    # 编译图
    app = graph.compile()

    # 初始化状态
    initial_state: StagedTravelState = {
        "messages": [HumanMessage(content=f"开始旅行规划: {requirements}")],
        "current_agent": "user_requirement_analyst",
        "current_stage": "requirement_analysis",
        "user_requirements": requirements,
        "user_portrait": None,
        "matched_destinations": None,
        "ranked_destinations": None,
        "selected_destination": selected_destination,
        "style_proposals": None,
        "selected_style": selected_style,
        "detailed_guide": None,
        "error": None,
        "_llm": llm
    }

    # 执行图
    try:
        result = app.invoke(initial_state)
        logger.info("[消息流图] 执行完成")
        return result
    except Exception as e:
        logger.error(f"[消息流图] 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            **initial_state,
            "error": str(e)
        }


# ============================================================
# 分阶段执行函数（用于API）
# ============================================================

def execute_stage_1_2_3(
    requirements: Dict[str, Any],
    llm=None
) -> Dict[str, Any]:
    """
    执行阶段1-3：需求分析 -> 地区匹配 -> 排名

    返回排名后的目的地列表，供用户选择
    """
    result = run_staged_travel_graph(requirements, llm)

    return {
        "user_portrait": result.get("user_portrait"),
        "ranked_destinations": result.get("ranked_destinations", []),
        "messages": [str(m) for m in result.get("messages", [])],
        "error": result.get("error")
    }


def execute_stage_4(
    requirements: Dict[str, Any],
    selected_destination: str,
    llm=None
) -> Dict[str, Any]:
    """
    执行阶段4：生成风格方案

    返回4种风格方案，供用户选择
    """
    result = run_staged_travel_graph(
        requirements,
        llm,
        selected_destination=selected_destination
    )

    return {
        "style_proposals": result.get("style_proposals", []),
        "messages": [str(m) for m in result.get("messages", [])],
        "error": result.get("error")
    }


def execute_stage_5(
    requirements: Dict[str, Any],
    selected_destination: str,
    selected_style: str,
    llm=None
) -> Dict[str, Any]:
    """
    执行阶段5：生成详细攻略

    返回完整的详细攻略
    """
    result = run_staged_travel_graph(
        requirements,
        llm,
        selected_destination=selected_destination,
        selected_style=selected_style
    )

    return {
        "detailed_guide": result.get("detailed_guide"),
        "messages": [str(m) for m in result.get("messages", [])],
        "error": result.get("error")
    }
