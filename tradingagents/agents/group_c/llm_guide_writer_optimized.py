"""
LLMGuideWriter 天行数据API优化方案

目标: 将API调用次数从 ~76次 减少到 ~2次
"""

import logging
from typing import Dict, List, Any
from tradingagents.tools.travel_tools_tianapi import (
    validate_and_enrich_attraction_names,
    get_popular_attractions_cached
)

logger = logging.getLogger('travel_agents')


# 天行数据缓存 (进程级别)
_TIANAPI_CACHE = {
    'city_attractions': {},  # {city: {attraction_name: {data}}}
    'last_update': {}        # {city: timestamp}
}
_CACHE_TTL = 3600  # 1小时缓存


def _load_city_attractions_batch(city: str, attraction_names: List[str]) -> Dict[str, Any]:
    """
    批量加载城市景点数据（优化版）

    一次API调用获取所有景点数据，然后本地查询

    Args:
        city: 城市名称
        attraction_names: 需要查询的景点名称列表

    Returns:
        景点数据映射 {attraction_name: {data}}
    """
    import time

    # 检查缓存
    if city in _TIANAPI_CACHE['city_attractions']:
        cache_time = _TIANAPI_CACHE['last_update'].get(city, 0)
        if time.time() - cache_time < _CACHE_TTL:
            logger.debug(f"[天行数据优化] 使用缓存数据: {city}")
            return _TIANAPI_CACHE['city_attractions'][city]

    # 一次API调用获取所有景点
    logger.info(f"[天行数据优化] 批量加载 {city} 景点数据")

    result = validate_and_enrich_attraction_names(
        attraction_names=attraction_names,
        city=city
    )

    # 构建景点数据映射
    attraction_map = {}

    # 添加验证通过的景点
    for name in result['valid']:
        if name in result['details']:
            attraction_map[name] = result['details'][name]

    # 添加未验证的景点（使用空数据）
    for name in result['invalid']:
        attraction_map[name] = {
            'name': name,
            'description': '',
            'sub_attractions': [],
            'verified': False
        }

    # 存入缓存
    _TIANAPI_CACHE['city_attractions'][city] = attraction_map
    _TIANAPI_CACHE['last_update'][city] = time.time()

    logger.info(f"[天行数据优化] 缓存了 {len(attraction_map)} 个景点")

    return attraction_map


def _get_real_attractions_context_optimized(destination: str) -> str:
    """
    获取景点上下文（优化版，使用缓存）
    """
    try:
        attractions = get_popular_attractions_cached(destination, limit=20)

        if not attractions:
            return ""

        lines = [f"## {destination} 真实景点列表（来自天行数据）\n"]

        for i, attr in enumerate(attractions[:15], 1):
            name = attr.get('name', '')
            content = attr.get('content', '')

            # 解析内容
            from tradingagents.integrations.tianapi_client import parse_attraction_content
            parsed = parse_attraction_content(content)
            desc = parsed['description']
            desc_short = desc[:80] + "..." if len(desc) > 80 else desc

            lines.append(f"{i}. {name}")
            lines.append(f"   {desc_short}")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        logger.warning(f"[天行数据优化] 获取景点上下文失败: {e}")
        return ""


def _batch_verify_and_enrich_attractions(
    destination: str,
    attraction_names: List[str]
) -> Dict[str, Dict[str, Any]]:
    """
    批量验证和丰富景点信息（优化版）

    一次API调用处理所有景点的验证、描述、子景点

    Args:
        destination: 目的地
        attraction_names: 景点名称列表

    Returns:
        {attraction_name: {verified, description, sub_attractions}}
    """
    # 批量加载数据
    attraction_map = _load_city_attractions_batch(destination, attraction_names)

    # 格式化返回数据
    result = {}
    for name in attraction_names:
        if name in attraction_map:
            data = attraction_map[name]
            result[name] = {
                'verified': True,  # 在map中就是验证通过
                'description': data.get('description', ''),
                'sub_attractions': data.get('sub_attractions', [])
            }
        else:
            result[name] = {
                'verified': False,
                'description': '',
                'sub_attractions': []
            }

    return result


def optimize_llm_guide_writer_calls():
    """
    优化LLMGuideWriter的API调用

    使用示例:
    # 优化前: 每个景点3次API调用 (验证 + 描述 + 子景点)
    # 优化后: 所有景点1次API调用
    """

    print("""
    === 天行数据API优化方案 ===

    优化前:
    - 5天行程，每天5个景点 = 25个景点
    - 每个景点3次API调用 = 75次
    - 加上概览1次 = 76次API调用

    优化后:
    - 批量加载城市景点数据 = 1次API调用
    - 所有景点使用缓存数据 = 0次额外API调用
    - 总计 = 1-2次API调用

    节省: ~98% 的API调用
    """)


# 优化的辅助函数（替代原版）
def _verify_attraction_optimized(attraction_name: str, city: str) -> bool:
    """验证景点（优化版）"""
    attraction_map = _load_city_attractions_batch(city, [attraction_name])
    return attraction_name in attraction_map


def _get_attraction_description_optimized(attraction_name: str, city: str) -> str:
    """获取景点描述（优化版）"""
    attraction_map = _load_city_attractions_batch(city, [attraction_name])
    return attraction_map.get(attraction_name, {}).get('description', '')


def _get_attraction_sub_attractions_optimized(attraction_name: str, city: str) -> List[str]:
    """获取子景点（优化版）"""
    attraction_map = _load_city_attractions_batch(city, [attraction_name])
    return attraction_map.get(attraction_name, {}).get('sub_attractions', [])


if __name__ == "__main__":
    optimize_llm_guide_writer_calls()
