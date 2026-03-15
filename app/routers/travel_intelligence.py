"""
目的地情报 API路由

提供目的地情报查询的API接口
"""

import os
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["目的地情报"])


# ============================================================
# 数据模型
# ============================================================

class IntelligenceRequest(BaseModel):
    """情报分析请求"""
    destination: str = Field(..., min_length=1, max_length=100)
    travel_date: Optional[str] = Field(None, description="旅行日期 YYYY-MM-DD")
    include_news: bool = True
    include_risks: bool = True
    include_events: bool = True
    include_culture: bool = True
    format: str = Field("json", description="输出格式: json/markdown")


class IntelligenceResponse(BaseModel):
    """情报分析响应"""
    destination: str
    travel_date: Optional[str]
    generated_at: str
    overall_risk: str
    overall_risk_text: str
    risk_level: int
    news_count: int
    events_count: int
    recommendations: list
    data: dict


class NewsItem(BaseModel):
    """新闻条目"""
    title: str
    source: str
    published_at: str
    summary: str
    sentiment: str
    category: str


class RiskAssessment(BaseModel):
    """风险评估"""
    overall_risk: str
    overall_risk_text: str
    risk_level: int
    recommendation: str
    risk_factors: list


class EventItem(BaseModel):
    """活动信息"""
    name: str
    type: str
    start_date: str
    end_date: str
    location: str
    description: str
    recommendation: str


# ============================================================
# API端点
# ============================================================

@router.get("/{destination}")
async def get_destination_intelligence(
    destination: str,
    travel_date: Optional[str] = None,
    format: str = Query("json", description="输出格式"),
    include_raw: bool = False
):
    """
    获取目的地情报

    参数：
    - destination: 目的地名称
    - travel_date: 旅行日期 (可选)
    - format: 输出格式 (json/markdown)
    - include_raw: 是否包含原始数据
    """
    try:
        # 导入智能体
        from tradingagents.agents.analysts.destination_intelligence import analyze_destination

        logger.info(f"[目的地情报] 分析请求: {destination}, 日期: {travel_date}")

        # 执行分析
        report = await analyze_destination(destination, travel_date)

        if format == "markdown":
            # 返回Markdown格式
            from tradingagents.agents.analysts.destination_intelligence import get_destination_intelligence_agent
            agent = get_destination_intelligence_agent()
            markdown = agent.format_intelligence_report(report)

            from fastapi.responses import Response
            return Response(
                content=markdown,
                media_type="text/markdown",
                headers={
                    "Content-Disposition": f"attachment; filename={destination}_情报报告.md"
                }
            )
        else:
            # 返回JSON格式
            risk_assessment = report.get("risk_assessment", {})

            return IntelligenceResponse(
                destination=report["destination"],
                travel_date=report.get("travel_date"),
                generated_at=report["generated_at"],
                overall_risk=risk_assessment.get("overall_risk", "unknown"),
                overall_risk_text=risk_assessment.get("overall_risk_text", ""),
                risk_level=risk_assessment.get("risk_level", 0),
                news_count=len(report.get("news", [])),
                events_count=len(report.get("events", [])),
                recommendations=report.get("recommendations", []),
                data=report if include_raw else None
            )

    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=f"智能体加载失败: {str(e)}"
        )
    except Exception as e:
        logger.error(f"[目的地情报] 分析失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"分析失败: {str(e)}"
        )


@router.get("/{destination}/news")
async def get_destination_news(
    destination: str,
    days: int = Query(7, ge=1, le=30, description="搜索最近几天的新闻"),
    limit: int = Query(10, ge=1, le=50)
):
    """
    获取目的地新闻

    参数：
    - destination: 目的地名称
    - days: 搜索最近几天
    - limit: 返回数量限制
    """
    try:
        from tradingagents.agents.analysts.destination_intelligence import get_destination_intelligence_agent

        agent = get_destination_intelligence_agent()
        news = await agent._search_news(destination, days)

        return {
            "destination": destination,
            "news": news[:limit],
            "total": len(news),
            "search_days": days
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取新闻失败: {str(e)}"
        )


# ============================================================
# 三种独立新闻模块
# ============================================================

@router.get("/{destination}/news/travel")
async def get_travel_news(
    destination: str,
    limit: int = Query(10, ge=1, le=20)
):
    """
    获取旅游新闻 - 专门的旅游资讯

    参数：
    - destination: 目的地名称
    - limit: 返回数量限制
    """
    try:
        from tradingagents.services.destination_intelligence_service import get_intelligence_service
        service = get_intelligence_service()

        logger.info(f"[旅游新闻API] 开始获取 {destination} 的新闻，限制: {limit}")
        news = await service._fetch_travel_news(destination, limit)
        logger.info(f"[旅游新闻API] 获取到 {len(news)} 条新闻")

        return {
            "destination": destination,
            "news_type": "travel",
            "news": news,
            "total": len(news),
            "source": "tianapi"
        }

    except Exception as e:
        logger.error(f"[旅游新闻] 获取失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取旅游新闻失败: {str(e)}"
        )


@router.get("/{destination}/news/area")
async def get_area_news(
    destination: str,
    limit: int = Query(10, ge=1, le=20)
):
    """
    获取地区新闻 - 本地/城市相关新闻

    参数：
    - destination: 目的地名称
    - limit: 返回数量限制
    """
    try:
        from tradingagents.services.destination_intelligence_service import get_intelligence_service
        service = get_intelligence_service()

        news = await service._fetch_area_news(destination, limit)

        return {
            "destination": destination,
            "news_type": "area",
            "news": news,
            "total": len(news),
            "source": "tianapi"
        }

    except Exception as e:
        logger.error(f"[地区新闻] 获取失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取地区新闻失败: {str(e)}"
        )


@router.get("/{destination}/news/general")
async def get_general_news(
    destination: str,
    limit: int = Query(10, ge=1, le=20)
):
    """
    获取综合新闻 - 综合、社会、体育、娱乐等

    参数：
    - destination: 目的地名称
    - limit: 返回数量限制
    """
    try:
        from tradingagents.services.destination_intelligence_service import get_intelligence_service
        service = get_intelligence_service()

        news = await service._fetch_general_news(destination, limit)

        return {
            "destination": destination,
            "news_type": "general",
            "news": news,
            "total": len(news),
            "source": "tianapi"
        }

    except Exception as e:
        logger.error(f"[综合新闻] 获取失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取综合新闻失败: {str(e)}"
        )


@router.get("/{destination}/risks")
async def get_destination_risks(
    destination: str,
    travel_date: Optional[str] = None
):
    """
    获取目的地风险评估

    参数：
    - destination: 目的地名称
    - travel_date: 旅行日期
    """
    try:
        from tradingagents.agents.analysts.destination_intelligence import get_destination_intelligence_agent

        agent = get_destination_intelligence_agent()
        risks = await agent._assess_risks(destination, travel_date)

        return risks

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"风险评估失败: {str(e)}"
        )


@router.get("/{destination}/events")
async def get_destination_events(
    destination: str,
    travel_date: Optional[str] = None,
    limit: int = Query(10, ge=1, le=20)
):
    """
    获取目的地活动推荐

    参数：
    - destination: 目的地名称
    - travel_date: 旅行日期
    - limit: 返回数量限制
    """
    try:
        from tradingagents.agents.analysts.destination_intelligence import get_destination_intelligence_agent

        agent = get_destination_intelligence_agent()
        events = await agent._find_events(destination, travel_date)

        return {
            "destination": destination,
            "events": events[:limit],
            "total": len(events),
            "travel_date": travel_date
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取活动失败: {str(e)}"
        )


@router.get("/{destination}/culture")
async def get_destination_culture(
    destination: str
):
    """
    获取目的地文化推荐

    参数：
    - destination: 目的地名称
    """
    try:
        from tradingagents.agents.analysts.destination_intelligence import get_destination_intelligence_agent

        agent = get_destination_intelligence_agent()
        culture = await agent._recommend_culture(destination)

        return {
            "destination": destination,
            "cultural_experiences": culture,
            "generated_at": str(datetime.now())
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取文化推荐失败: {str(e)}"
        )


@router.post("/refresh")
async def refresh_destination_intelligence(
    destination: str,
    travel_date: Optional[str] = None
):
    """
    刷新目的地情报

    强制重新获取最新情报，跳过缓存

    参数：
    - destination: 目的地名称
    - travel_date: 旅行日期
    """
    try:
        from tradingagents.agents.analysts.destination_intelligence import analyze_destination

        # 执行分析
        report = await analyze_destination(destination, travel_date)

        return {
            "success": True,
            "destination": destination,
            "message": "情报已刷新",
            "generated_at": report["generated_at"],
            "news_count": len(report.get("news", [])),
            "events_count": len(report.get("events", []))
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"刷新失败: {str(e)}"
        )


@router.get("/stats")
async def get_intelligence_stats():
    """获取情报系统统计"""
    from tradingagents.agents.analysts.destination_intelligence import get_destination_intelligence_agent

    agent = get_destination_intelligence_agent()

    return {
        "cache_size": len(agent._cache),
        "cache_ttl": agent._cache_ttl,
        "supported_destinations": [
            "杭州", "北京", "上海", "成都", "三亚", "西安",
            "拉萨", "新疆", "丽江", "桂林", "厦门"
        ],
        "available_services": [
            "news_search",
            "risk_assessment",
            "event_discovery",
            "culture_recommendation",
            "weather_info",
            "exchange_rate",
            "attractions_search"
        ]
    }


# ============================================================
# 新增：真实API端点
# ============================================================

@router.get("/{destination}/weather")
async def get_destination_weather(
    destination: str
):
    """
    获取目的地天气信息

    集成高德天气API，提供实时天气和预报
    """
    try:
        from tradingagents.services.destination_intelligence_service import get_intelligence_service

        service = get_intelligence_service()
        weather = await service._get_weather(destination)

        return {
            "success": True,
            "destination": destination,
            "weather": weather,
            "source": "amap" if service.amap_key else "mock"
        }

    except Exception as e:
        logger.error(f"[天气API] 获取失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取天气失败: {str(e)}"
        )


@router.get("/{destination}/exchange-rate")
async def get_destination_exchange_rate(
    destination: str
):
    """
    获取目的地汇率信息

    集成ExchangeRate-API，提供实时汇率
    """
    try:
        from tradingagents.services.destination_intelligence_service import get_intelligence_service

        service = get_intelligence_service()
        rate = await service._get_exchange_rate(destination)

        return {
            "success": True,
            "destination": destination,
            "exchange_rate": rate,
            "updated_at": str(datetime.now())
        }

    except Exception as e:
        logger.error(f"[汇率API] 获取失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取汇率失败: {str(e)}"
        )


@router.get("/{destination}/attractions")
async def get_destination_attractions(
    destination: str,
    limit: int = Query(10, ge=1, le=20)
):
    """
    获取目的地景点信息

    集成SerpAPI Google搜索
    """
    try:
        from tradingagents.services.destination_intelligence_service import get_intelligence_service

        service = get_intelligence_service()
        attractions = await service._get_attractions(destination)

        return {
            "success": True,
            "destination": destination,
            "attractions": attractions[:limit],
            "total": len(attractions),
            "source": "serpapi" if service.serpapi_key else "mock"
        }

    except Exception as e:
        logger.error(f"[景点API] 获取失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取景点失败: {str(e)}"
        )


@router.get("/{destination}/realtime")
async def get_destination_realtime_intelligence(
    destination: str,
    travel_date: Optional[str] = None
):
    """
    获取目的地实时情报（整合所有真实API）

    返回：
    - 新闻（天行数据）
    - 天气（高德天气）
    - 汇率（ExchangeRate-API）
    - 景点（SerpAPI）
    - 风险评估
    """
    try:
        from tradingagents.services.destination_intelligence_service import get_destination_intelligence

        intelligence = await get_destination_intelligence(destination, travel_date)

        return {
            "success": True,
            "data": intelligence,
            "sources": {
                "news": "tianapi" if os.getenv("TIANAPI_KEY") else "mock",
                "weather": "amap" if os.getenv("AMAP_API_KEY") else "mock",
                "exchange_rate": "exchangerate-api",
                "attractions": "serpapi" if os.getenv("SERPAPI_KEY") else "mock"
            }
        }

    except Exception as e:
        logger.error(f"[实时情报] 获取失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取实时情报失败: {str(e)}"
        )


# ============================================================
# 便捷路由：快速检查（用于规划时调用）
# ============================================================

@router.post("/quick-check")
async def quick_check_destination(
    destination: str,
    travel_date: Optional[str] = None
):
    """
    快速检查目的地

    在旅行规划时调用，快速检查目的地是否有重大风险或特别推荐的活动

    返回精简版情报
    """
    try:
        from tradingagents.agents.analysts.destination_intelligence import analyze_destination

        report = await analyze_destination(destination, travel_date)

        risks = report.get("risk_assessment", {})
        events = report.get("events", [])

        # 检查是否有高风险
        has_high_risk = risks.get("risk_level", 0) >= 4

        # 检查是否有推荐活动
        recommended_events = [e for e in events if "推荐" in e.get("recommendation", "")]

        return {
            "destination": destination,
            "safe": not has_high_risk,
            "risk_level": risks.get("risk_level", 1),
            "risk_summary": risks.get("overall_risk_text", ""),
            "has_recommendations": len(recommended_events) > 0,
            "top_recommendations": recommended_events[:3] if recommended_events else [],
            "quick_tips": report.get("recommendations", [])[:3]
        }

    except Exception as e:
        logger.error(f"[快速检查] 失败: {e}")
        return {
            "destination": destination,
            "safe": True,  # 出错时默认安全
            "risk_level": 1,
            "risk_summary": "无法获取实时情报",
            "has_recommendations": False,
            "top_recommendations": [],
            "quick_tips": ["建议出行前查询最新情报"]
        }
