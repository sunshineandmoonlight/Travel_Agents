"""
智能体工具函数 - 天行数据集成

为各个智能体提供便捷的天行数据访问接口
"""

import logging
from typing import List, Dict, Any, Optional
from tradingagents.integrations.tianapi_client import (
    TianAPIClient,
    get_popular_attractions_cached,
    parse_attraction_content
)

logger = logging.getLogger('travel_agents')


def get_city_attractions_for_agent(
    city: str,
    limit: int = 50,
    format_for_llm: bool = True
) -> str | List[Dict[str, Any]]:
    """
    获取城市景点列表（供智能体使用）

    Args:
        city: 城市名称
        limit: 返回数量
        format_for_llm: 是否格式化为LLM友好的文本

    Returns:
        如果 format_for_llm=True: 返回格式化的文本
        否则: 返回景点列表
    """
    try:
        attractions = get_popular_attractions_cached(city, limit)

        if not attractions:
            logger.warning(f"[智能体工具] 城市 {city} 没有找到景点数据")
            return "" if format_for_llm else []

        if format_for_llm:
            # 格式化为LLM友好的文本
            lines = [f"## {city} 真实景点列表\n"]

            for i, attr in enumerate(attractions, 1):
                name = attr.get('name', '')
                desc = parse_attraction_content(attr.get('content', ''))['description']
                desc_short = desc[:100] + "..." if len(desc) > 100 else desc

                lines.append(f"{i}. **{name}**")
                lines.append(f"   {desc_short}")
                lines.append("")

            return "\n".join(lines)
        else:
            return attractions

    except Exception as e:
        logger.error(f"[智能体工具] 获取城市景点失败: {e}")
        return "" if format_for_llm else []


def get_attraction_sub_attractions(attraction_name: str, city: str) -> List[str]:
    """
    获取景点的子景点列表

    用于 ActivityEnricher 生成深度体验活动

    Args:
        attraction_name: 景点名称
        city: 城市名称

    Returns:
        子景点列表
    """
    try:
        client = TianAPIClient()
        attractions = client.get_scenic_attractions(city=city, num=100)

        for attr in attractions:
            if attr.get('name') == attraction_name:
                parsed = parse_attraction_content(attr.get('content', ''))
                return parsed.get('sub_attractions', [])

        return []

    except Exception as e:
        logger.error(f"[智能体工具] 获取子景点失败: {e}")
        return []


def validate_and_enrich_attraction_names(
    attraction_names: List[str],
    city: str
) -> Dict[str, Any]:
    """
    验证景点名称并返回详细信息

    用于 AttractionScheduler 确保行程中的景点真实存在

    Args:
        attraction_names: 景点名称列表
        city: 城市名称

    Returns:
        {
            'valid': ['虎丘', '拙政园'],           # 验证通过的景点
            'invalid': ['不存在的景点'],          # 验证失败的景点
            'details': {'虎丘': {...}},            # 景点详细信息
        }
    """
    try:
        client = TianAPIClient()
        city_attractions = client.get_scenic_attractions(city=city, num=100)

        # 创建景点名称映射
        attraction_map = {attr.get('name'): attr for attr in city_attractions}

        result = {
            'valid': [],
            'invalid': [],
            'details': {}
        }

        for name in attraction_names:
            if name in attraction_map:
                result['valid'].append(name)
                # 格式化详情
                parsed = parse_attraction_content(attraction_map[name].get('content', ''))
                result['details'][name] = {
                    'name': name,
                    'description': parsed['description'],
                    'sub_attractions': parsed['sub_attractions'],
                    'province': attraction_map[name].get('province'),
                    'city': attraction_map[name].get('city')
                }
            else:
                result['invalid'].append(name)

        return result

    except Exception as e:
        logger.error(f"[智能体工具] 验证景点名称失败: {e}")
        return {
            'valid': [],
            'invalid': attraction_names,
            'details': {}
        }


def suggest_attractions_by_preference(
    city: str,
    preferences: Dict[str, Any],
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    根据用户偏好推荐景点

    用于 DestinationMatcher 和 AttractionScheduler

    Args:
        city: 城市名称
        preferences: 用户偏好
            - travel_type: 旅行类型（文化/自然/美食等）
            - pace_preference: 节奏偏好（紧凑/悠闲）
            - budget_level: 预算水平
        limit: 返回数量

    Returns:
        推荐的景点列表
    """
    try:
        attractions = get_popular_attractions_cached(city, limit=50)

        if not attractions:
            return []

        # 根据偏好筛选和排序
        scored_attractions = []

        for attr in attractions:
            score = 0
            name = attr.get('name', '')
            desc = attr.get('content', '')

            # 基于旅行类型评分
            travel_type = preferences.get('travel_type', '')
            if travel_type == '文化':
                if any(keyword in name or keyword in desc for keyword in
                       ['寺', '庙', '宫', '古城', '博物馆', '园林', '塔']):
                    score += 3
            elif travel_type == '自然':
                if any(keyword in name or keyword in desc for keyword in
                       ['山', '湖', '河', '海', '公园', '谷', '峰']):
                    score += 3
            elif travel_type == '美食':
                if any(keyword in name or keyword in desc for keyword in
                       ['街', '城', '广场', '夜市']):
                    score += 2

            # 基于预算评分
            budget_level = preferences.get('budget_level', '')
            if budget_level == '经济':
                if '免费' in desc or '公园' in name:
                    score += 2

            scored_attractions.append((attr, score))

        # 排序并返回Top N
        scored_attractions.sort(key=lambda x: x[1], reverse=True)
        return [attr for attr, score in scored_attractions[:limit]]

    except Exception as e:
        logger.error(f"[智能体工具] 推荐景点失败: {e}")
        return []


def create_attraction_tools() -> List[Dict]:
    """
    创建LangChain工具，供智能体调用

    Returns:
        LangChain工具列表
    """
    from langchain_core.tools import tool

    @tool
    def get_city_attractions(city: str, limit: int = 20) -> str:
        """获取城市的真实景点列表

        Args:
            city: 城市名称（如"苏州"、"杭州"）
            limit: 返回数量（默认20）

        Returns:
            城市的真实景点列表，包含景点名称和描述
        """
        return get_city_attractions_for_agent(city, limit, format_for_llm=True)

    @tool
    def get_attraction_details(attraction_name: str, city: str) -> str:
        """获取景点的详细信息

        Args:
            attraction_name: 景点名称
            city: 城市名称

        Returns:
            景点的详细描述和子景点列表
        """
        result = validate_and_enrich_attraction_names([attraction_name], city)

        if attraction_name in result['details']:
            detail = result['details'][attraction_name]
            output = f"景点：{detail['name']}\n"
            output += f"描述：{detail['description']}\n"
            if detail['sub_attractions']:
                output += f"包含景点：{', '.join(detail['sub_attractions'][:10])}"
            return output
        else:
            return f"未找到景点 {attraction_name} 的详细信息"

    @tool
    def get_attraction_sub_attractions(attraction_name: str, city: str) -> str:
        """获取景点的子景点列表

        Args:
            attraction_name: 景点名称
            city: 城市名称

        Returns:
            子景点列表，用于生成深度体验活动
        """
        sub_attractions = get_attraction_sub_attractions(attraction_name, city)

        if sub_attractions:
            return f"{attraction_name}的子景点：{', '.join(sub_attractions[:10])}"
        else:
            return f"{attraction_name}没有子景点信息"

    return [get_city_attractions, get_attraction_details, get_attraction_sub_attractions]


# 导出
__all__ = [
    'get_city_attractions_for_agent',
    'get_attraction_sub_attractions',
    'validate_and_enrich_attraction_names',
    'suggest_attractions_by_preference',
    'create_attraction_tools'
]
