"""
天行数据 API 客户端

提供旅游景区、天气、新闻等数据
API文档：https://www.tianapi.com/
"""

import os
import requests
import logging
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import time

logger = logging.getLogger('travel_agents')

# 加载环境变量
load_dotenv()

TIANAPI_KEY = os.getenv("TIANAPI_KEY", "")
TIANAPI_BASE_URL = "http://apis.tianapi.com"  # 使用新域名

if not TIANAPI_KEY:
    logger.warning("[天行数据] TIANAPI_KEY 未配置")


class TianAPIClient:
    """天行数据API客户端"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or TIANAPI_KEY
        self.base_url = TIANAPI_BASE_URL
        self.session = requests.Session()
        # 禁用代理以确保API请求正常工作
        self.session.trust_env = False
        self.session.proxies = {'http': None, 'https': None}

    def _request(
        self,
        endpoint: str,
        params: Dict[str, Any],
        method: str = "GET"
    ) -> Dict[str, Any]:
        """
        发送API请求

        Args:
            endpoint: API端点
            params: 请求参数
            method: 请求方法

        Returns:
            API响应数据
        """
        url = f"{self.base_url}{endpoint}"
        params['key'] = self.api_key

        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=10)
            else:
                response = self.session.post(url, data=params, timeout=10)

            response.raise_for_status()
            data = response.json()

            # 检查响应状态
            if data.get('code') == 200:
                # 天行数据API返回格式: {code, msg, newslist/list}
                # 优先返回整个data，让调用方根据需要提取newslist或list
                return data
            else:
                logger.error(f"[天行数据] API返回错误: {data.get('msg', 'Unknown error')}")
                return {}

        except requests.exceptions.RequestException as e:
            logger.error(f"[天行数据] 请求失败: {e}")
            return {}
        except Exception as e:
            logger.error(f"[天行数据] 解析响应失败: {e}")
            return {}

    def get_scenic_attractions(
        self,
        city: str,
        province: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        num: int = 20
    ) -> List[Dict[str, Any]]:
        """
        获取旅游景区列表

        Args:
            city: 城市名称（如"苏州"、"杭州"）
            province: 省份名称（可选）
            keyword: 搜索关键词（可选）
            page: 页码
            num: 每页数量

        Returns:
            景点列表
        """
        params = {
            'city': city,
            'page': page,
            'num': num
        }

        if province:
            params['province'] = province
        if keyword:
            params['keyword'] = keyword

        logger.info(f"[天行数据] 获取景点列表: city={city}, keyword={keyword}")

        result = self._request('/scenic/index', params)
        # 天行数据API返回格式: {code, msg, result: {list: [...]}}
        return result.get('result', {}).get('list', [])

    def get_attraction_detail(
        self,
        id: Optional[str] = None,
        name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        获取景点详情

        Args:
            id: 景点ID
            name: 景点名称（ID和name二选一）

        Returns:
            景点详情
        """
        params = {}

        if id:
            params['id'] = id
        elif name:
            params['name'] = name
        else:
            logger.warning("[天行数据] 获取景点详情需要id或name参数")
            return None

        logger.info(f"[天行数据] 获取景点详情: id={id}, name={name}")

        result = self._request('/scenic/index', params)
        newslist = result.get('newslist', [])

        if newslist:
            return newslist[0]
        return None

    def search_attractions(
        self,
        keyword: str,
        page: int = 1,
        num: int = 20
    ) -> List[Dict[str, Any]]:
        """
        搜索景点

        Args:
            keyword: 搜索关键词
            page: 页码
            num: 每页数量

        Returns:
            景点列表
        """
        return self.get_scenic_attractions(
            city="",
            keyword=keyword,
            page=page,
            num=num
        )

    def get_attractions_by_province(
        self,
        province: str,
        page: int = 1,
        num: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取省份所有景点

        Args:
            province: 省份名称
            page: 页码
            num: 每页数量

        Returns:
            景点列表
        """
        params = {
            'province': province,
            'page': page,
            'num': num
        }

        logger.info(f"[天行数据] 获取省份景点: province={province}")

        result = self._request('/scenic/index', params)
        # 天行数据API返回 result.list 字段
        return result.get('list', [])


# 热门城市景点缓存
_ATTRACTION_CACHE = {}
_CACHE_TTL = 3600  # 1小时缓存


def get_popular_attractions_cached(city: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    获取热门城市景点（带缓存）

    Args:
        city: 城市名称
        limit: 返回数量

    Returns:
        景点列表
    """
    global _ATTRACTION_CACHE
    import time

    cache_key = f"{city}:{limit}"
    now = time.time()

    # 检查缓存
    if cache_key in _ATTRACTION_CACHE:
        cached_data, cached_time = _ATTRACTION_CACHE[cache_key]
        if now - cached_time < _CACHE_TTL:
            logger.debug(f"[天行数据] 使用缓存: {city}")
            return cached_data

    # 请求API
    client = TianAPIClient()
    attractions = client.get_scenic_attractions(city=city, num=limit)

    # 存入缓存
    _ATTRACTION_CACHE[cache_key] = (attractions, now)

    return attractions


def parse_attraction_content(content: str) -> Dict[str, Any]:
    """
    解析景点内容

    Args:
        content: 景点描述内容

    Returns:
        解析后的数据
    """
    result = {
        'description': '',
        'sub_attractions': []
    }

    if not content:
        return result

    # 清理内容
    content = content.strip()

    # 检查是否包含"包含景点:"字段
    if '包含景点:' in content or '包含景点：' in content:
        parts = content.split('包含景点:' if '包含景点:' in content else '包含景点：')
        result['description'] = parts[0].strip()

        if len(parts) > 1:
            # 解析子景点列表
            sub_attractions_str = parts[1].strip()
            # 按空格或中文分隔符分割
            import re
            sub_attractions = re.split(r'[\s，、]+', sub_attractions_str)
            result['sub_attractions'] = [a for a in sub_attractions if a]
    else:
        result['description'] = content

    return result


def format_attraction_for_display(attraction: Dict[str, Any]) -> Dict[str, Any]:
    """
    格式化景点数据用于前端显示

    Args:
        attraction: 原始景点数据

    Returns:
        格式化后的数据
    """
    parsed = parse_attraction_content(attraction.get('content', ''))

    return {
        'name': attraction.get('name', ''),
        'description': parsed['description'],
        'province': attraction.get('province', ''),
        'city': attraction.get('city', ''),
        'sub_attractions': parsed['sub_attractions'],
        'source': 'tianapi'
    }


# 导出
__all__ = [
    'TianAPIClient',
    'get_popular_attractions_cached',
    'parse_attraction_content',
    'format_attraction_for_display'
]
