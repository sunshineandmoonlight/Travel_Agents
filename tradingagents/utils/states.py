"""
旅行规划State定义
"""

from typing import TypedDict, List, Dict, Optional, Literal
from langchain_core.messages import BaseMessage


class TravelPlanningState(TypedDict):
    """统一的旅行规划State（兼容国内+国际）"""

    # ==================== 用户输入 ====================
    user_input: str
    destination: str
    destination_type: Literal["domestic", "international", "auto"]
    start_date: str
    end_date: str
    days: int
    budget: float
    travelers: int
    interests: List[str]
    special_requirements: str

    # ==================== 目的地识别结果 ====================
    destination_info: Dict

    # ==================== 数据收集结果 ====================
    attractions: List[Dict]
    weather_forecast: Dict
    transport_options: Dict
    location_highlights: List[str]

    # ==================== 方案生成 ====================
    proposals: List[Dict]
    selected_proposal: Optional[str]

    # ==================== 详细规划 ====================
    detailed_itinerary: Optional[Dict]
    budget_breakdown: Optional[Dict]
    practical_info: Optional[Dict]

    # ==================== 调整历史 ====================
    adjustment_history: List[Dict]

    # ==================== 最终输出 ====================
    final_plan: Optional[Dict]

    # ==================== 系统字段 ====================
    messages: List[BaseMessage]
    current_step: str
    error: Optional[str]
