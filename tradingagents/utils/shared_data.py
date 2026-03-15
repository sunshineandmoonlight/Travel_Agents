"""
智能体间数据共享模块

实现Group B和Group C智能体之间的数据共享，避免重复API调用。
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger('travel_agents')


class SharedDataManager:
    """
    共享数据管理器

    管理智能体间共享的数据，如API搜索结果、中间状态等。
    """

    def __init__(self):
        """初始化共享数据管理器"""
        self._shared_data: Dict[str, Any] = {}

    def set(self, key: str, value: Any, source_agent: str = "unknown") -> None:
        """
        设置共享数据

        Args:
            key: 数据键
            value: 数据值
            source_agent: 来源智能体
        """
        self._shared_data[key] = {
            "value": value,
            "source": source_agent,
            "timestamp": datetime.now()
        }
        logger.debug(f"[数据共享] 存储 {key} | 来源: {source_agent}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取共享数据

        Args:
            key: 数据键
            default: 默认值

        Returns:
            数据值
        """
        if key in self._shared_data:
            data = self._shared_data[key]
            logger.debug(f"[数据共享] 获取 {key} | 来源: {data['source']}")
            return data["value"]
        return default

    def has(self, key: str) -> bool:
        """检查是否存在共享数据"""
        return key in self._shared_data

    def remove(self, key: str) -> None:
        """移除共享数据"""
        if key in self._shared_data:
            del self._shared_data[key]
            logger.debug(f"[数据共享] 移除 {key}")

    def clear(self) -> None:
        """清空所有共享数据"""
        count = len(self._shared_data)
        self._shared_data.clear()
        logger.info(f"[数据共享] 清空 {count} 条共享数据")

    def get_all_metadata(self) -> Dict[str, Dict]:
        """获取所有共享数据的元数据"""
        metadata = {}
        for key, data in self._shared_data.items():
            metadata[key] = {
                "source": data["source"],
                "timestamp": data["timestamp"],
                "type": type(data["value"]).__name__
            }
        return metadata


# 全局共享数据管理器
_global_shared_data_manager: Optional[SharedDataManager] = None


def get_shared_data_manager() -> SharedDataManager:
    """获取全局共享数据管理器实例"""
    global _global_shared_data_manager
    if _global_shared_data_manager is None:
        _global_shared_data_manager = SharedDataManager()
        logger.info("[数据共享] 创建全局共享数据管理器")
    return _global_shared_data_manager


def reset_shared_data_manager() -> None:
    """重置全局共享数据管理器"""
    global _global_shared_data_manager
    _global_shared_data_manager = None
    logger.info("[数据共享] 重置全局共享数据管理器")


# ============================================================
# 共享数据键常量
# ============================================================

class SharedDataKeys:
    """共享数据键常量"""

    # Group B 搜索结果
    GROUP_B_ATTRACTIONS = "group_b:attractions"
    GROUP_B_API_SOURCES = "group_b:api_sources"
    GROUP_B_DESTINATION_DATA = "group_b:destination_data"

    # 天气数据
    WEATHER_FORECAST = "weather:forecast"
    WEATHER_CITY = "weather:city"

    # 餐厅数据
    RESTAURANTS = "restaurants:data"

    # 交通数据
    ROUTE_DATA = "route:data"


# ============================================================
# 智能体数据保存辅助函数
# ============================================================

def save_group_b_search_results(
    attractions: List[Dict[str, Any]],
    api_sources: List[str],
    destination_data: Dict[str, Any]
) -> None:
    """
    保存 Group B 的搜索结果供后续使用

    Args:
        attractions: Group B 搜索到的景点列表
        api_sources: 使用的API列表
        destination_data: 目的地数据
    """
    manager = get_shared_data_manager()

    manager.set(
        SharedDataKeys.GROUP_B_ATTRACTIONS,
        {
            "attractions": attractions,
            "count": len(attractions),
            "timestamp": datetime.now().isoformat()
        },
        source_agent="Group_B"
    )

    manager.set(
        SharedDataKeys.GROUP_B_API_SOURCES,
        api_sources,
        source_agent="Group_B"
    )

    manager.set(
        SharedDataKeys.GROUP_B_DESTINATION_DATA,
        destination_data,
        source_agent="Group_B"
    )

    logger.info(f"[数据共享] 保存 Group B 搜索结果: {len(attractions)} 个景点, API: {api_sources}")


def load_group_b_attractions() -> Optional[List[Dict[str, Any]]]:
    """
    加载 Group B 的景点搜索结果

    Returns:
        景点列表，如果不存在则返回 None
    """
    manager = get_shared_data_manager()

    if not manager.has(SharedDataKeys.GROUP_B_ATTRACTIONS):
        return None

    data = manager.get(SharedDataKeys.GROUP_B_ATTRACTIONS)
    logger.info(f"[数据共享] 复用 Group B 景点数据: {data.get('count', 0)} 个")
    return data.get("attractions")


def save_weather_forecast(city: str, forecast: List[Dict[str, Any]]) -> None:
    """保存天气预报供后续使用"""
    manager = get_shared_data_manager()

    manager.set(
        SharedDataKeys.WEATHER_FORECAST,
        {
            "city": city,
            "forecasts": forecast,
            "days": len(forecast),
            "timestamp": datetime.now().isoformat()
        },
        source_agent="AttractionScheduler"
    )

    manager.set(
        SharedDataKeys.WEATHER_CITY,
        city,
        source_agent="AttractionScheduler"
    )


def load_weather_forecast(city: str) -> Optional[List[Dict[str, Any]]]:
    """加载天气预报（如果城市匹配）"""
    manager = get_shared_data_manager()

    cached_city = manager.get(SharedDataKeys.WEATHER_CITY)
    if cached_city == city and manager.has(SharedDataKeys.WEATHER_FORECAST):
        data = manager.get(SharedDataKeys.WEATHER_FORECAST)
        logger.info(f"[数据共享] 复用天气预报: {city}, {data.get('days', 0)} 天")
        return data.get("forecasts")

    return None


def get_api_sources_used() -> List[str]:
    """获取已使用的API列表"""
    manager = get_shared_data_manager()
    return manager.get(SharedDataKeys.GROUP_B_API_SOURCES, [])


__all__ = [
    "SharedDataManager",
    "get_shared_data_manager",
    "reset_shared_data_manager",
    "SharedDataKeys",
    "save_group_b_search_results",
    "load_group_b_attractions",
    "save_weather_forecast",
    "load_weather_forecast",
    "get_api_sources_used",
]
