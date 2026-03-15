"""
旅行工具的 LangChain 包装器

将旅行工具转换为 LangChain StructuredTool 格式，
以便智能体可以使用 @tool 装饰器或 bind_tools() 方法绑定工具。
"""

from typing import Dict, Any, List, Optional
import logging
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

logger = logging.getLogger('travel_agents')


# ============================================================
# 工具参数定义（Pydantic 模型）
# ============================================================

class AttractionSearchInput(BaseModel):
    """景点搜索工具输入"""
    city: str = Field(description="城市名称，如'北京'、'上海'")
    keywords: Optional[str] = Field(default="景点", description="搜索关键词，如'博物馆'、'公园'")
    limit: int = Field(default=10, description="返回数量限制")


class RestaurantSearchInput(BaseModel):
    """餐厅搜索工具输入"""
    city: str = Field(description="城市名称")
    area: str = Field(default="", description="区域名称，如'王府井'、'西湖'")
    limit: int = Field(default=10, description="返回数量限制")


class WeatherForecastInput(BaseModel):
    """天气预报工具输入"""
    city: str = Field(description="城市名称")
    days: int = Field(default=7, description="预报天数")


class RoutePlanningInput(BaseModel):
    """路径规划工具输入"""
    origin: str = Field(description="出发地，如'故宫'")
    destination: str = Field(description="目的地，如'长城'")
    city: str = Field(default="", description="城市名称，用于限定范围")


class ImageSearchInput(BaseModel):
    """图片搜索工具输入"""
    attraction_name: str = Field(description="景点名称")
    city: str = Field(default="", description="城市名称（帮助提高准确性）")


# ============================================================
# 工具包装器函数
# ============================================================

def search_attractions(city: str, keywords: str = "景点", limit: int = 10) -> str:
    """
    搜索城市内的景点

    Args:
        city: 城市名称
        keywords: 搜索关键词
        limit: 返回数量限制

    Returns:
        景点列表的 JSON 字符串
    """
    try:
        from tradingagents.tools.travel_tools import get_attraction_search_tool

        tool = get_attraction_search_tool()
        attractions = tool.search_attractions(city=city, keywords=keywords, limit=limit)

        if attractions:
            result = {
                "success": True,
                "city": city,
                "count": len(attractions),
                "attractions": attractions
            }
            import json
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            return f"未在{city}找到匹配的景点"

    except Exception as e:
        logger.error(f"[景点搜索工具] 调用失败: {e}")
        return f"景点搜索失败: {str(e)}"


def search_restaurants(city: str, area: str = "", limit: int = 10) -> str:
    """
    搜索餐厅

    Args:
        city: 城市名称
        area: 区域名称
        limit: 返回数量限制

    Returns:
        餐厅列表的 JSON 字符串
    """
    try:
        from tradingagents.tools.travel_tools import get_restaurant_search_tool

        tool = get_restaurant_search_tool()
        restaurants = tool.search_restaurants(city=city, area=area, limit=limit)

        if restaurants:
            result = {
                "success": True,
                "city": city,
                "area": area,
                "count": len(restaurants),
                "restaurants": restaurants
            }
            import json
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            return f"未在{city}{area}找到匹配的餐厅"

    except Exception as e:
        logger.error(f"[餐厅搜索工具] 调用失败: {e}")
        return f"餐厅搜索失败: {str(e)}"


def get_weather_forecast(city: str, days: int = 7) -> str:
    """
    获取天气预报

    Args:
        city: 城市名称
        days: 预报天数

    Returns:
        天气预报的 JSON 字符串
    """
    try:
        from tradingagents.tools.travel_tools import get_weather_forecast_tool

        tool = get_weather_forecast_tool()
        forecast = tool.get_forecast(city=city, days=days)

        if forecast:
            result = {
                "success": True,
                "city": city,
                "days": days,
                "forecast": forecast
            }
            import json
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            return f"无法获取{city}的天气预报"

    except Exception as e:
        logger.error(f"[天气预报工具] 调用失败: {e}")
        return f"天气预报获取失败: {str(e)}"


def plan_route(origin: str, destination: str, city: str = "") -> str:
    """
    规划路径

    Args:
        origin: 出发地
        destination: 目的地
        city: 城市

    Returns:
        路径规划的 JSON 字符串
    """
    try:
        from tradingagents.tools.travel_tools import get_route_planning_tool

        tool = get_route_planning_tool()
        route = tool.plan_route(origin=origin, destination=destination, city=city)

        if route:
            result = {
                "success": True,
                "origin": origin,
                "destination": destination,
                "route": route
            }
            import json
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            return f"无法规划从{origin}到{destination}的路径"

    except Exception as e:
        logger.error(f"[路径规划工具] 调用失败: {e}")
        return f"路径规划失败: {str(e)}"


def search_attraction_image(attraction_name: str, city: str = "") -> str:
    """
    搜索景点图片

    Args:
        attraction_name: 景点名称
        city: 城市名称

    Returns:
        图片 URL 的 JSON 字符串
    """
    try:
        from tradingagents.tools.travel_tools import get_image_search_tool

        tool = get_image_search_tool()
        image_url = tool.search_attraction_image(attraction_name=attraction_name, city=city)

        if image_url:
            result = {
                "success": True,
                "attraction": attraction_name,
                "city": city,
                "image_url": image_url
            }
            import json
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            return f"未找到{attraction_name}的图片"

    except Exception as e:
        logger.error(f"[图片搜索工具] 调用失败: {e}")
        return f"图片搜索失败: {str(e)}"


# ============================================================
# LangChain 工具定义
# ============================================================

# 景点搜索工具
attraction_search_tool = StructuredTool.from_function(
    func=search_attractions,
    name="attraction_search",
    description="""
    搜索指定城市的旅游景点。

    当需要知道某个城市有哪些景点时使用此工具。
    可以根据关键词搜索特定类型的景点，如博物馆、公园、历史遗址等。

    输入参数：
    - city: 城市名称（必需）
    - keywords: 搜索关键词（可选，默认为"景点"）
    - limit: 返回数量限制（可选，默认10）

    返回景点列表，包含名称、地址、评分、类型等信息。
    """,
    args_schema=AttractionSearchInput
)

# 餐厅搜索工具
restaurant_search_tool = StructuredTool.from_function(
    func=search_restaurants,
    name="restaurant_search",
    description="""
    搜索指定城市的餐厅。

    当需要为用户推荐餐厅或美食时使用此工具。
    可以指定城市和区域来缩小搜索范围。

    输入参数：
    - city: 城市名称（必需）
    - area: 区域名称（可选，如"王府井"）
    - limit: 返回数量限制（可选，默认10）

    返回餐厅列表，包含名称、地址、评分、人均消费等信息。
    """,
    args_schema=RestaurantSearchInput
)

# 天气预报工具
weather_forecast_tool = StructuredTool.from_function(
    func=get_weather_forecast,
    name="weather_forecast",
    description="""
    获取指定城市的天气预报。

    在规划旅行行程时，使用此工具了解目的地天气情况，
    以便根据天气调整活动安排（如雨天安排室内活动）。

    输入参数：
    - city: 城市名称（必需）
    - days: 预报天数（可选，默认7天）

    返回天气预报，包含温度、天气状况、降水概率等信息。
    """,
    args_schema=WeatherForecastInput
)

# 路径规划工具
route_planning_tool = StructuredTool.from_function(
    func=plan_route,
    name="route_planning",
    description="""
    规划两个地点之间的路径。

    当需要了解如何从一个景点到达另一个景点时使用此工具。
    可以估算交通时间、费用，并推荐交通方式。

    输入参数：
    - origin: 出发地名称（必需）
    - destination: 目的地名称（必需）
    - city: 城市名称（可选，用于限定范围）

    返回路径信息，包含距离、时间、费用、推荐交通方式等。
    """,
    args_schema=RoutePlanningInput
)

# 图片搜索工具
image_search_tool = StructuredTool.from_function(
    func=search_attraction_image,
    name="attraction_image_search",
    description="""
    搜索景点的图片。

    当需要获取景点图片用于展示或参考时使用此工具。

    输入参数：
    - attraction_name: 景点名称（必需）
    - city: 城市名称（可选，帮助提高准确性）

    返回图片 URL。
    """,
    args_schema=ImageSearchInput
)


# ============================================================
# 工具集合导出
# ============================================================

# 所有工具列表
ALL_TRAVEL_TOOLS = [
    attraction_search_tool,
    restaurant_search_tool,
    weather_forecast_tool,
    route_planning_tool,
    image_search_tool
]

# Group C 工具（景点排程师、餐饮推荐师、交通规划师）
GROUP_C_TOOLS = [
    attraction_search_tool,
    restaurant_search_tool,
    weather_forecast_tool,
    route_planning_tool
]

# 工具映射字典
TOOLS_MAP = {
    "attraction_search": attraction_search_tool,
    "restaurant_search": restaurant_search_tool,
    "weather_forecast": weather_forecast_tool,
    "route_planning": route_planning_tool,
    "image_search": image_search_tool
}


def get_tools_by_names(tool_names: List[str]) -> List:
    """
    根据工具名称列表获取工具

    Args:
        tool_names: 工具名称列表

    Returns:
        工具列表
    """
    tools = []
    for name in tool_names:
        if name in TOOLS_MAP:
            tools.append(TOOLS_MAP[name])
    return tools


def get_all_travel_tools() -> List:
    """获取所有旅行工具"""
    return ALL_TRAVEL_TOOLS


def get_group_c_tools() -> List:
    """获取 Group C 智能体使用的工具"""
    return GROUP_C_TOOLS


# ============================================================
# 导出
# ============================================================

__all__ = [
    "attraction_search_tool",
    "restaurant_search_tool",
    "weather_forecast_tool",
    "route_planning_tool",
    "image_search_tool",
    "ALL_TRAVEL_TOOLS",
    "GROUP_C_TOOLS",
    "TOOLS_MAP",
    "get_tools_by_names",
    "get_all_travel_tools",
    "get_group_c_tools"
]
