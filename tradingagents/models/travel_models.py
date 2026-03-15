"""
旅行规划系统数据结构定义

基于 v3.0 分阶段渐进式设计
参考文档: docs/travel_project/10_STAGED_SYSTEM_DESIGN.md
"""

from typing import Dict, List, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================
# 阶段2: 用户需求表单数据
# ============================================================

class TravelRequirementForm(BaseModel):
    """旅行需求表单"""
    # 基本信息
    travel_scope: Literal['domestic', 'international'] = Field(
        ..., description="旅行范围: 国内/国外"
    )
    start_date: str = Field(..., description="出发日期 YYYY-MM-DD")
    days: int = Field(..., ge=1, le=30, description="旅行天数")
    adults: int = Field(..., ge=1, le=20, description="成人人数")
    children: int = Field(default=0, ge=0, le=10, description="儿童人数")

    # 预算和偏好
    budget: Literal['economy', 'medium', 'luxury'] = Field(
        ..., description="预算等级"
    )
    interests: List[str] = Field(
        default_factory=list,
        description="兴趣标签列表"
    )
    special_requests: str = Field(
        default="",
        description="特殊需求"
    )


# ============================================================
# 阶段3: 推荐地区卡片数据
# ============================================================

class DestinationBudget(BaseModel):
    """目的地预算信息"""
    total: int = Field(..., description="总预算（元）")
    per_person: int = Field(..., description="人均预算（元）")
    currency: str = Field(default="CNY", description="货币")


class DestinationCard(BaseModel):
    """推荐地区卡片"""
    destination: str = Field(..., description="地区名称")
    image: str = Field(..., description="图片URL")
    match_score: int = Field(..., ge=0, le=100, description="匹配分数")

    recommendation_reason: str = Field(
        ...,
        description="推荐理由（2-3句话）"
    )

    estimated_budget: DestinationBudget = Field(
        ...,
        description="预估费用"
    )

    best_season: str = Field(..., description="最佳季节")
    suitable_for: List[str] = Field(
        default_factory=list,
        description="适合人群"
    )
    highlights: List[str] = Field(
        default_factory=list,
        description="热门景点（3-5个）"
    )

    # 可选：天气预览
    weather_preview: Optional[Dict[str, Any]] = Field(
        default=None,
        description="天气预览"
    )


# ============================================================
# 阶段4: 风格方案数据
# ============================================================

class DailyPreview(BaseModel):
    """每日预览"""
    day: int = Field(..., ge=1, description="第几天")
    title: str = Field(..., description="标题")
    attractions: List[str] = Field(
        default_factory=list,
        description="景点名称列表"
    )


class StyleProposal(BaseModel):
    """风格方案"""
    style_name: str = Field(..., description="方案名称")
    style_icon: str = Field(..., description="图标emoji")
    style_type: Literal['immersive', 'exploration', 'relaxation', 'hidden_gem'] = Field(
        ...,
        description="风格类型"
    )

    style_description: str = Field(..., description="风格描述")
    daily_pace: str = Field(..., description="每日节奏描述")
    intensity_level: int = Field(..., ge=1, le=5, description="强度等级")

    preview_itinerary: List[DailyPreview] = Field(
        default_factory=list,
        description="预览行程（每天1行）"
    )

    estimated_cost: int = Field(..., description="预估费用")
    best_for: str = Field(..., description="适合人群描述")
    highlights: List[str] = Field(
        default_factory=list,
        description="方案亮点"
    )


# ============================================================
# 阶段5: 详细攻略数据
# ============================================================

class TicketInfo(BaseModel):
    """门票信息"""
    price: int = Field(..., description="门票价格")
    booking: str = Field(..., description="预约方式")
    tips: List[str] = Field(default_factory=list, description="购票提示")


class TransportInfo(BaseModel):
    """交通信息"""
    method: str = Field(..., description="交通方式")
    route: str = Field(..., description="路线描述")
    duration: str = Field(..., description="耗时")
    cost: int = Field(..., description="费用")


class ScheduleItem(BaseModel):
    """行程安排项"""
    period: Literal['morning', 'lunch', 'afternoon', 'dinner', 'evening'] = Field(
        ...,
        description="时段"
    )
    time_range: str = Field(..., description="时间段 如 09:00-11:30")

    activity: str = Field(..., description="活动名称")
    location: str = Field(..., description="地点名称")
    description: Optional[str] = Field(None, description="详细描述")

    transport: Optional[TransportInfo] = Field(None, description="交通信息")
    ticket: Optional[TicketInfo] = Field(None, description="门票信息")
    tips: Optional[List[str]] = Field(None, description="游览建议")


class HotelType(BaseModel):
    """酒店类型"""
    category: str = Field(..., description="经济型/舒适型/品质型")
    price_range: str = Field(..., description="价格范围")
    examples: List[str] = Field(default_factory=list, description="酒店示例")


class AccommodationSuggestion(BaseModel):
    """住宿建议"""
    area: str = Field(..., description="推荐区域")
    reason: str = Field(..., description="推荐理由")
    hotel_types: List[HotelType] = Field(
        default_factory=list,
        description="酒店类型"
    )


class DailyWeather(BaseModel):
    """每日天气"""
    condition: str = Field(..., description="天气状况")
    temperature_min: int = Field(..., description="最低温度")
    temperature_max: int = Field(..., description="最高温度")
    aqi: Optional[int] = Field(None, description="空气质量指数")


class DailyItinerary(BaseModel):
    """每日行程"""
    day: int = Field(..., ge=1, description="第几天")
    date: str = Field(..., description="日期 YYYY-MM-DD")
    title: str = Field(..., description="标题")
    weather: DailyWeather = Field(..., description="天气信息")

    schedule: List[ScheduleItem] = Field(
        default_factory=list,
        description="行程安排"
    )

    accommodation: AccommodationSuggestion = Field(
        ...,
        description="住宿建议"
    )
    daily_budget: int = Field(..., description="当日预算")


class DetailedGuide(BaseModel):
    """详细攻略"""
    destination: str = Field(..., description="目的地")
    style_type: str = Field(..., description="风格类型")
    total_days: int = Field(..., description="总天数")
    total_budget: int = Field(..., description="总预算")

    daily_itineraries: List[DailyItinerary] = Field(
        default_factory=list,
        description="每日行程"
    )

    summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="汇总信息"
    )


# ============================================================
# API响应模型
# ============================================================

class UserPortrait(BaseModel):
    """用户画像"""
    travel_type: str = Field(..., description="旅行类型")
    primary_interests: List[str] = Field(default_factory=list, description="主要兴趣")
    pace_preference: str = Field(..., description="节奏偏好")
    budget_level: str = Field(..., description="预算等级")


class AgentAnalysis(BaseModel):
    """智能体分析结果"""
    agent_name: str = Field(..., description="智能体名称")
    agent_icon: str = Field(..., description="智能体图标")
    agent_type: str = Field(..., description="智能体类型")
    summary: str = Field(..., description="分析摘要")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="原始数据")


class DestinationAnalysis(BaseModel):
    """地区推荐响应"""
    success: bool
    destinations: List[DestinationCard]
    agent_analysis: Dict[str, Any] = Field(
        default_factory=dict,
        description="智能体分析"
    )


class StyleAnalysisResponse(BaseModel):
    """风格方案响应"""
    success: bool
    styles: List[StyleProposal]
    destination_info: Dict[str, Any] = Field(
        default_factory=dict
    )


class GuideResponse(BaseModel):
    """详细攻略响应"""
    success: bool
    guide: DetailedGuide
    agent_analysis: Dict[str, Any] = Field(
        default_factory=dict,
        description="智能体分析"
    )


# ============================================================
# 旅行规划State（用于LangGraph）
# ============================================================

class StagedTravelState(Dict):
    """
    分阶段旅行规划State

    用于 v3.0 分阶段渐进式设计
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置默认值
        self.setdefault("current_stage", "init")
        self.setdefault("messages", [])

        # 阶段1: 选择范围
        self.setdefault("travel_scope", None)

        # 阶段2: 收集需求
        self.setdefault("user_requirements", None)

        # 阶段3: 推荐地区
        self.setdefault("user_portrait", None)
        self.setdefault("candidate_destinations", [])
        self.setdefault("recommended_destinations", [])
        self.setdefault("selected_destination", None)

        # 阶段4: 风格方案
        self.setdefault("style_proposals", [])
        self.setdefault("selected_style", None)

        # 阶段5: 详细攻略
        self.setdefault("detailed_guide", None)

        # 系统字段
        self.setdefault("error", None)
        self.setdefault("_llm", None)


# ============================================================
# 常量定义
# ============================================================

# 兴趣标签完整列表
INTEREST_TAGS = [
    # 自然风光
    "自然风光", "山川", "海滨", "湖泊", "森林", "草原", "沙漠",

    # 历史文化
    "历史文化", "古迹", "寺庙", "博物馆", "古镇", "非遗",

    # 美食体验
    "美食体验", "小吃", "特色菜", "夜市", "餐厅",

    # 休闲度假
    "休闲度假", "温泉", "海滩", "度假村", "SPA",

    # 购物娱乐
    "购物娱乐", "商场", "夜市", "主题乐园",

    # 户外探险
    "户外探险", "徒步", "登山", "骑行", "滑雪",

    # 亲子娱乐
    "亲子娱乐", "主题乐园", "动物园", "科技馆",

    # 其他
    "摄影", "网红打卡", "小众秘境"
]

# 国内热门城市列表（推荐TOP 20）
DOMESTIC_HOT_CITIES = [
    # 直辖市
    "北京", "上海", "天津", "重庆",

    # 省会及热门城市
    "广州", "深圳", "成都", "杭州", "西安", "南京", "武汉", "长沙",
    "郑州", "沈阳", "大连", "青岛", "宁波", "厦门", "苏州", "哈尔滨",

    # 旅游城市
    "三亚", "丽江", "大理", "桂林", "张家界", "九寨沟", "黄山", "拉萨"
]

# 国际热门目的地列表（推荐TOP 20）
INTERNATIONAL_HOT_DESTINATIONS = [
    # 亚洲
    "日本", "韩国", "泰国", "新加坡", "马来西亚", "越南", "柬埔寨",
    "印尼", "菲律宾", "印度", "尼泊尔", "马尔代夫",

    # 欧洲
    "法国", "英国", "意大利", "西班牙", "希腊", "瑞士", "德国", "荷兰",

    # 大洋洲
    "澳大利亚", "新西兰",

    # 北美
    "美国", "加拿大"
]

# 旅行风格定义
TRAVEL_STYLES = {
    "immersive": {
        "name": "沉浸式",
        "icon": "🎭",
        "description": "深度体验，慢节奏感受",
        "daily_attractions": "2-3个",
        "pace": "慢",
        "intensity": 2,
        "best_for": "喜欢深度了解文化的人"
    },
    "exploration": {
        "name": "探索式",
        "icon": "🧭",
        "description": "多元打卡，丰富行程",
        "daily_attractions": "4-5个",
        "pace": "快",
        "intensity": 4,
        "best_for": "好奇宝宝，怕无聊"
    },
    "relaxation": {
        "name": "松弛式",
        "icon": "🌿",
        "description": "休闲为主，轻松度假",
        "daily_attractions": "1-2个",
        "pace": "最慢",
        "intensity": 1,
        "best_for": "度假为主，拒绝赶路"
    },
    "hidden_gem": {
        "name": "小众宝藏",
        "icon": "💎",
        "description": "避开人流，发现隐秘景点",
        "daily_attractions": "2-3个",
        "pace": "中等",
        "intensity": 3,
        "best_for": "探险爱好者"
    }
}
