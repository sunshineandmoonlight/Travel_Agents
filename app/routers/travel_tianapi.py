"""
天行数据旅游景区API路由

提供真实景点数据查询接口
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/travel/tianapi", tags=["Travel-TianAPI"])


class ScenicAttractionRequest(BaseModel):
    """景点查询请求"""
    city: str
    province: Optional[str] = None
    keyword: Optional[str] = None
    page: int = 1
    num: int = 20


class ScenicAttractionResponse(BaseModel):
    """景点响应"""
    name: str
    description: str
    province: str
    city: str
    sub_attractions: List[str]
    source: str


@router.get("/attractions")
async def get_attractions(
    city: str = Query(..., description="城市名称"),
    province: Optional[str] = Query(None, description="省份名称"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, description="页码"),
    num: int = Query(20, description="每页数量")
):
    """
    获取旅游景区列表

    使用天行数据API查询真实的景点信息

    **示例**:
    - 获取苏州所有景点: /api/travel/tianapi/attractions?city=苏州
    - 搜索"虎丘": /api/travel/tianapi/attractions?city=苏州&keyword=虎丘
    - 获取江苏省景点: /api/travel/tianapi/attractions?province=江苏

    **返回数据**:
    ```json
    {
      "code": 200,
      "msg": "success",
      "data": [
        {
          "name": "虎丘",
          "description": "被誉为"吴中第一名胜"的虎丘...",
          "province": "江苏",
          "city": "苏州",
          "sub_attractions": ["二山门", "憨憨泉", "剑池", ...],
          "source": "tianapi"
        }
      ],
      "total": 150
    }
    ```
    """
    try:
        from tradingagents.integrations.tianapi_client import (
            TianAPIClient,
            format_attraction_for_display
        )

        client = TianAPIClient()

        # 调用天行数据API
        attractions_list = client.get_scenic_attractions(
            city=city,
            province=province,
            keyword=keyword,
            page=page,
            num=num
        )

        # 格式化数据
        formatted_attractions = []
        for attraction in attractions_list:
            formatted = format_attraction_for_display(attraction)
            formatted_attractions.append(ScenicAttractionResponse(**formatted))

        return {
            "code": 200,
            "msg": "success",
            "data": formatted_attractions,
            "total": len(formatted_attractions)
        }

    except Exception as e:
        logger.error(f"获取景点列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/attractions/search")
async def search_attractions(
    keyword: str = Query(..., description="搜索关键词"),
    page: int = Query(1, description="页码"),
    num: int = Query(20, description="每页数量")
):
    """
    搜索景点（全国范围）

    **示例**:
    - 搜索"故宫": /api/travel/tianapi/attractions/search?keyword=故宫
    """
    try:
        from tradingagents.integrations.tianapi_client import (
            TianAPIClient,
            format_attraction_for_display
        )

        client = TianAPIClient()
        attractions_list = client.search_attractions(
            keyword=keyword,
            page=page,
            num=num
        )

        formatted_attractions = []
        for attraction in attractions_list:
            formatted = format_attraction_for_display(attraction)
            formatted_attractions.append(ScenicAttractionResponse(**formatted))

        return {
            "code": 200,
            "msg": "success",
            "data": formatted_attractions,
            "total": len(formatted_attractions)
        }

    except Exception as e:
        logger.error(f"搜索景点失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/attractions/province/{province}")
async def get_attractions_by_province(
    province: str,
    page: int = Query(1, description="页码"),
    num: int = Query(50, description="每页数量")
):
    """
    获取省份所有景点

    **示例**:
    - 获取江苏省景点: /api/travel/tianapi/attractions/province/江苏
    """
    try:
        from tradingagents.integrations.tianapi_client import (
            TianAPIClient,
            format_attraction_for_display
        )

        client = TianAPIClient()
        attractions_list = client.get_attractions_by_province(
            province=province,
            page=page,
            num=num
        )

        formatted_attractions = []
        for attraction in attractions_list:
            formatted = format_attraction_for_display(attraction)
            formatted_attractions.append(ScenicAttractionResponse(**formatted))

        return {
            "code": 200,
            "msg": "success",
            "data": formatted_attractions,
            "total": len(formatted_attractions)
        }

    except Exception as e:
        logger.error(f"获取省份景点失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/attractions/popular/{city}")
async def get_popular_attractions(
    city: str,
    limit: int = Query(20, description="返回数量")
):
    """
    获取热门城市景点（带缓存）

    **示例**:
    - 获取苏州热门景点: /api/travel/tianapi/attractions/popular/苏州?limit=10
    """
    try:
        from tradingagents.integrations.tianapi_client import (
            get_popular_attractions_cached,
            format_attraction_for_display
        )

        attractions_list = get_popular_attractions_cached(city, limit)

        formatted_attractions = []
        for attraction in attractions_list:
            formatted = format_attraction_for_display(attraction)
            formatted_attractions.append(ScenicAttractionResponse(**formatted))

        return {
            "code": 200,
            "msg": "success",
            "data": formatted_attractions,
            "total": len(formatted_attractions),
            "cached": True
        }

    except Exception as e:
        logger.error(f"获取热门景点失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class AttractionMappingRequest(BaseModel):
    """景点名称映射请求"""
    attraction_names: List[str]
    city: str


@router.post("/attractions/validate")
async def validate_attraction_names(request: AttractionMappingRequest):
    """
    验证并映射景点名称

    检查给定的景点名称是否存在于天行数据中，
    返回正确的景点名称和详细信息

    **请求体**:
    ```json
    {
      "attraction_names": ["虎丘", "拙政园", "狮子林"],
      "city": "苏州"
    }
    ```

    **响应**:
    ```json
    {
      "code": 200,
      "data": {
        "valid": ["虎丘", "拙政园"],
        "invalid": ["狮子林"],
        "details": [...]
      }
    }
    ```
    """
    try:
        from tradingagents.integrations.tianapi_client import TianAPIClient

        client = TianAPIClient()
        validated = {
            "valid": [],
            "invalid": [],
            "details": {}
        }

        # 获取城市所有景点（用于验证）
        city_attractions = client.get_scenic_attractions(
            city=request.city,
            num=100
        )

        # 创建景点名称集合
        attraction_names = set()
        for attr in city_attractions:
            name = attr.get('name', '')
            if name:
                attraction_names.add(name)

        # 验证每个景点名称
        for name in request.attraction_names:
            if name in attraction_names:
                validated["valid"].append(name)
                # 获取详细信息
                for attr in city_attractions:
                    if attr.get('name') == name:
                        validated["details"][name] = format_attraction_for_display(attr)
                        break
            else:
                validated["invalid"].append(name)

        return {
            "code": 200,
            "msg": "success",
            "data": validated
        }

    except Exception as e:
        logger.error(f"验证景点名称失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
