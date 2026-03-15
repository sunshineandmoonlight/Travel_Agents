"""
Group C 智能体模块

负责详细规划：
- C1: 景点排程师 (AttractionScheduler) - 安排景点游览时间表
- C2: 交通规划师 (TransportPlanner) - 规划景点间交通方式
- C3: 餐饮推荐师 (DiningRecommender) - 推荐午餐晚餐区域和特色美食
- C4: 住宿顾问 (AccommodationAdvisor) - 推荐酒店/民宿区域
- C5: 攻略格式化师 (GuideFormatter) - 整合所有内容为完整攻略
- C6: LLM攻略生成器 (LLMGuideWriter) - 生成LLM优化版攻略文本

新增：LLM工具调用版本智能体（使用 bind_tools 机制）
"""

from .attraction_scheduler import (
    schedule_attractions,
    attraction_scheduler_node,
)

from .transport_planner import (
    plan_transport,
    transport_planner_node,
    enhance_schedule_with_transport,
)

from .dining_recommender import (
    recommend_dining,
    dining_recommender_node,
)

from .accommodation_advisor import (
    recommend_accommodation,
    accommodation_advisor_node,
)

from .guide_formatter import (
    format_detailed_guide,
    guide_formatter_node,
)

from .llm_guide_writer import (
    write_detailed_guide_with_llm as write_llm_guide,
    llm_guide_writer_node,
)

# LLM工具调用版本智能体（新增）
from .llm_tool_agents import (
    AttractionSchedulerWithTools,
    DiningRecommenderWithTools,
    TransportPlannerWithTools,
    create_attraction_scheduler_with_tools,
    create_dining_recommender_with_tools,
    create_transport_planner_with_tools,
    attraction_scheduler_llm_tools_node,
    dining_recommender_llm_tools_node,
    transport_planner_llm_tools_node,
)

# 工具绑定模块
from .tool_bindings import (
    bind_tools_to_agent,
    attraction_scheduler_node_with_tools,
    dining_recommender_node_with_tools,
    transport_planner_node_with_tools,
    call_weather_tool,
    call_restaurant_tool,
    call_route_tool,
)

__all__ = [
    # 景点排程师
    "schedule_attractions",
    "attraction_scheduler_node",
    # 交通规划师
    "plan_transport",
    "transport_planner_node",
    "enhance_schedule_with_transport",
    # 餐饮推荐师
    "recommend_dining",
    "dining_recommender_node",
    # 住宿顾问
    "recommend_accommodation",
    "accommodation_advisor_node",
    # 攻略格式化师
    "format_detailed_guide",
    "guide_formatter_node",
    # LLM攻略生成器
    "write_llm_guide",
    "llm_guide_writer_node",
    # LLM工具调用版本智能体（新增）
    "AttractionSchedulerWithTools",
    "DiningRecommenderWithTools",
    "TransportPlannerWithTools",
    "create_attraction_scheduler_with_tools",
    "create_dining_recommender_with_tools",
    "create_transport_planner_with_tools",
    "attraction_scheduler_llm_tools_node",
    "dining_recommender_llm_tools_node",
    "transport_planner_llm_tools_node",
    # 工具绑定
    "bind_tools_to_agent",
    "attraction_scheduler_node_with_tools",
    "dining_recommender_node_with_tools",
    "transport_planner_node_with_tools",
    "call_weather_tool",
    "call_restaurant_tool",
    "call_route_tool",
]
