"""
旅行规划工具集

为智能体提供实时API调用能力
"""

from .travel_tools import (
    AttractionSearchTool,
    RestaurantSearchTool,
    WeatherForecastTool,
    ImageSearchTool,
    RoutePlanningTool,
    DestinationSearchTool,
    get_attraction_search_tool,
    get_restaurant_search_tool,
    get_weather_forecast_tool,
    get_image_search_tool,
    get_route_planning_tool,
    get_transport_tool,
    get_destination_search_tool,
)

from .langchain_tools import (
    attraction_search_tool,
    restaurant_search_tool,
    weather_forecast_tool,
    route_planning_tool,
    image_search_tool,
    ALL_TRAVEL_TOOLS,
    GROUP_C_TOOLS,
    TOOLS_MAP,
    get_tools_by_names,
    get_all_travel_tools,
    get_group_c_tools,
)

__all__ = [
    # 原始工具类
    "AttractionSearchTool",
    "RestaurantSearchTool",
    "WeatherForecastTool",
    "ImageSearchTool",
    "RoutePlanningTool",
    "DestinationSearchTool",
    "get_attraction_search_tool",
    "get_restaurant_search_tool",
    "get_weather_forecast_tool",
    "get_image_search_tool",
    "get_route_planning_tool",
    "get_transport_tool",
    "get_destination_search_tool",
    # LangChain 工具
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
    "get_group_c_tools",
]
