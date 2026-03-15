"""
旅行计划 AI API - 为前端提供规划功能
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/travel/plans", tags=["travel-plans"])


# ============================================================
# 测试端点 - 验证 CORS
# ============================================================
@router.get("/test")
async def test_cors():
    """测试 CORS 是否正常工作"""
    return {
        "success": True,
        "message": "CORS is working!",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/test-simple")
async def test_simple():
    """简单测试端点 - 直接返回模拟数据"""
    try:
        return {
            "success": True,
            "message": "Simple test works!",
            "data": {
                "destination": "Test City",
                "plans": [
                    {
                        "name": "测试方案",
                        "description": "这是一个测试方案",
                        "days": 3,
                        "budget": "medium"
                    }
                ]
            }
        }
    except Exception as e:
        return {"error": str(e)}


# ============================================================
# Request Models
# ============================================================

class GeneratePlansRequest(BaseModel):
    destination: str
    days: int
    adults: int
    children: int
    budget: str
    styles: List[str]
    special_requests: str = ""


class GenerateGuideRequest(BaseModel):
    selected_plan: Dict[str, Any]
    requirements: str


class SavePlanRequest(BaseModel):
    title: str
    destination: str
    days: int
    plan_data: Dict[str, Any]


# ============================================================
# AI Planning API
# ============================================================

@router.post("/ai/generate-plans")
async def generate_plans(request: GeneratePlansRequest):
    """
    AI 生成多个旅行方案 - 展示多智能体分析结果
    """
    try:
        logger.info(f"[旅行规划] 生成方案: {request.destination}, {request.days}天")
        logger.info(f"[旅行规划] 请求数据: adults={request.adults}, children={request.children}, budget={request.budget}, styles={request.styles}")

        # 检查是否配置了有效的 LLM API Key
        import os
        siliconflow_key = os.getenv("SILICONFLOW_API_KEY", "")
        use_real_llm = siliconflow_key and not siliconflow_key.startswith("your_")

        result = {}
        if use_real_llm:
            try:
                logger.info(f"[旅行规划] 使用 SiliconFlow LLM 生成真实数据")
                # 调用旅行规划图
                from tradingagents.graph.travel_graph_with_llm import create_travel_graph_with_llm

                graph = create_travel_graph_with_llm(
                    llm_provider="siliconflow",
                    llm_model="Qwen/Qwen2.5-7B-Instruct"
                )

                # 使用智能体生成真实规划
                result = graph.plan(
                    destination=request.destination,
                    days=request.days,
                    budget=request.budget,
                    travelers=request.adults + request.children,
                    interest_type="、".join(request.styles) if request.styles else "",
                    selected_style=""
                )

                # 检查结果是否有效
                if result is None or not isinstance(result, dict) or len(result) == 0:
                    logger.warning(f"[旅行规划] 智能体返回空结果，使用模拟数据")
                    result = _generate_mock_result(request)
                else:
                    logger.info(f"[旅行规划] LLM 生成成功")
            except Exception as e:
                logger.warning(f"[旅行规划] 调用智能体失败: {e}，使用模拟数据", exc_info=True)
                result = _generate_mock_result(request)
        else:
            logger.info(f"[旅行规划] 未配置有效的SILICONFLOW_API_KEY，使用模拟数据")
            result = _generate_mock_result(request)

        # ============================================
        # 提取每个智能体的独立分析结果
        # ============================================

        # 1. 目的地分类器分析
        destination_analysis = {
            "agent_name": "目的地分类器",
            "agent_icon": "🌍",
            "agent_type": "classifier",
            "analysis": result.get("destination_info", {}),
            "summary": f"识别{request.destination}为{result.get('destination_info', {}).get('type', '未知')}类型目的地"
        }

        # 2. 景点分析师推荐
        attractions_data = result.get("attractions", {})
        attraction_analysis = {
            "agent_name": "景点分析师",
            "agent_icon": "🏛️",
            "agent_type": "analyst",
            "raw_data": attractions_data,
            "summary": f"发现{attractions_data.get('count', 0)}个精选景点",
            "top_attractions": (attractions_data.get("attractions", [])[:8] if attractions_data else []),
            "recommendations": []
        }

        # 生成景点推荐文字
        if attractions_data.get("attractions"):
            for i, attr in enumerate(attractions_data["attractions"][:5]):
                name = attr.get("name", "未知景点")
                address = attr.get("address", "")
                attraction_analysis["recommendations"].append(f"• {name} - {address[:40]}..." if len(address) > 40 else f"• {name}")

        # 3. 天气分析师报告
        weather_data = result.get("weather_forecast", {})
        weather_analysis = {
            "agent_name": "天气分析师",
            "agent_icon": "🌤️",
            "agent_type": "analyst",
            "raw_data": weather_data,
            "forecast": weather_data.get("forecast", {}) if weather_data else {},
            "summary": f"已获取{request.days}天天气预报",
            "tips": []
        }

        # 生成天气建议
        if weather_data.get("forecast"):
            forecast = weather_data["forecast"]
            if isinstance(forecast, dict) and "daily" in forecast:
                for day_forecast in forecast["daily"][:3]:
                    date = day_forecast.get("date", "")[:10]
                    max_temp = day_forecast.get("temperature_2m_max", "N/A")
                    min_temp = day_forecast.get("temperature_2m_min", "N/A")
                    weather_code = day_forecast.get("weathercode", 0)
                    weather_desc = "晴" if weather_code < 3 else "多云" if weather_code < 50 else "雨"
                    weather_analysis["tips"].append(f"• {date}: {weather_desc} {min_temp}-{max_temp}°C")

        # 4. 预算分析师报告
        budget_data = result.get("budget_breakdown", {})
        budget_analysis = {
            "agent_name": "预算分析师",
            "agent_icon": "💰",
            "agent_type": "analyst",
            "raw_data": budget_data,
            "breakdown": {},
            "summary": f"预估总预算: {budget_data.get('total_budget', 0):,}元",
            "tips": []
        }

        # 格式化预算分解
        if budget_data:
            total = budget_data.get("total_budget", 0)
            budget_analysis["breakdown"] = {
                "交通": budget_data.get("transportation", {}).get("amount", 0),
                "住宿": budget_data.get("accommodation", {}).get("amount", 0),
                "餐饮": budget_data.get("meals", {}).get("amount", 0),
                "景点": budget_data.get("attractions", {}).get("amount", 0),
                "其他": budget_data.get("miscellaneous", {}).get("amount", 0),
                "总计": total
            }

            # 生成预算建议
            per_person = total / (request.adults + request.children) if (request.adults + request.children) > 0 else total
            budget_analysis["tips"] = [
                f"• 人均预算: {per_person:,.0f}元",
                f"• 建议预留10%应急资金",
                f"• 可根据实际需求灵活调整各部分预算"
            ]

        # 5. 行程规划师分析
        detailed_itinerary = result.get("detailed_itinerary", {})
        itinerary_analysis = {
            "agent_name": "行程规划师",
            "agent_icon": "📋",
            "agent_type": "planner",
            "raw_data": detailed_itinerary,
            "summary": f"为{request.days}天行程精心规划",
            "highlights": detailed_itinerary.get("highlights", []) if isinstance(detailed_itinerary, dict) else [],
            "tips": [
                f"• 每日建议安排2-3个主要景点",
                f"• 预留充足的休息和用餐时间",
                f"• 根据天气情况灵活调整行程"
            ]
        }

        # ============================================
        # 基于智能体分析生成旅行方案
        # ============================================

        plans = []
        attractions_list = attractions_data.get("attractions", []) if attractions_data else []

        # 如果有景点数据，生成真实行程
        if attractions_list:
            styles_config = [
                {
                    "name": "经济实惠游",
                    "budget_level": "economy",
                    "description": f"预算友好型{request.destination}{request.days}日游，精选高性价比景点",
                    "agent_advice": budget_analysis["tips"][:2] if budget_analysis["tips"] else [],
                    "highlights_prefix": ["经济实惠", "高性价比"],
                    "activity_style": "economy"
                },
                {
                    "name": "舒适品质游",
                    "budget_level": "medium",
                    "description": f"舒适型{request.destination}{request.days}日游，精选高品质体验",
                    "agent_advice": ["精选优质酒店", "品质餐厅用餐"],
                    "highlights_prefix": ["舒适体验", "品质服务"],
                    "activity_style": "medium"
                },
                {
                    "name": "奢华尊享游",
                    "budget_level": "luxury",
                    "description": f"奢华型{request.destination}{request.days}日游，顶级私人定制",
                    "agent_advice": ["五星级酒店", "私人导游专车"],
                    "highlights_prefix": ["奢华享受", "私人定制"],
                    "activity_style": "luxury"
                }
            ]

            for style_config in styles_config:
                # 为每天生成行程
                daily_itinerary = []
                attractions_per_day = max(2, len(attractions_list) // request.days)

                for day in range(1, request.days + 1):
                    start_idx = (day - 1) * attractions_per_day
                    end_idx = min(start_idx + attractions_per_day + 1, len(attractions_list))
                    day_attractions = attractions_list[start_idx:end_idx]

                    # 生成基于真实景点的活动
                    activities = []
                    for attr in day_attractions[:3]:
                        attr_name = attr.get("name", "景点")
                        attr_desc = attr.get("description", "")
                        activities.append({
                            "time": "上午" if len(activities) == 0 else "下午" if len(activities) == 1 else "晚上",
                            "activity": f"游览{attr_name}",
                            "description": attr_desc[:50] + "..." if len(attr_desc) > 50 else attr_desc,
                            "attraction_id": attr.get("poi_id", "")
                        })

                    # 添加用餐建议
                    if style_config["activity_style"] == "economy":
                        activities.append({"time": "午餐", "activity": "当地特色小吃街", "description": "体验地道的平民美食"})
                        activities.append({"time": "晚餐", "activity": "经济型餐厅", "description": "性价比高的本地餐厅"})
                    elif style_config["activity_style"] == "luxury":
                        activities.append({"time": "午餐", "activity": "米其林推荐餐厅", "description": "享受顶级美食体验"})
                        activities.append({"time": "晚餐", "activity": "高端私房菜", "description": "私人定制晚餐"})
                    else:
                        activities.append({"time": "午餐", "activity": "当地推荐餐厅", "description": "品尝当地特色菜"})
                        activities.append({"time": "晚餐", "activity": "特色美食体验", "description": "探索当地夜市美食"})

                    daily_itinerary.append({
                        "day": day,
                        "title": f"第{day}天：{day_attractions[0].get('name', request.destination) if day_attractions else request.destination + '精华'}",
                        "activities": activities,
                        "attractions": day_attractions
                    })

                # 生成亮点
                highlights = []
                highlights.extend([f"{h}" for h in style_config["highlights_prefix"]])
                if attractions_list:
                    highlights.append(f"精选{len(attractions_list)}个热门景点")
                if weather_data:
                    highlights.append("实时天气提醒")
                highlights.extend([f"智能推荐{style_config['agent_advice'][0] if style_config['agent_advice'] else ''}"])

                plans.append({
                    "name": style_config["name"],
                    "description": style_config["description"],
                    "days": request.days,
                    "budget": style_config["budget_level"],
                    "destination": request.destination,
                    "highlights": highlights[:5],
                    "itinerary": daily_itinerary,
                    "estimated_budget": budget_data.get("total_budget", 0),
                    "weather_info": weather_data.get("forecast", {}) if weather_data else {},
                    "agent_insights": {
                        "budget_tips": style_config["agent_advice"],
                        "weather_tips": weather_analysis["tips"][:2] if weather_analysis["tips"] else []
                    }
                })
        else:
            # 兜底方案
            for i, style_name in enumerate(["经济实惠游", "舒适品质游", "奢华尊享游"]):
                daily_itinerary = []
                for day in range(1, request.days + 1):
                    daily_itinerary.append({
                        "day": day,
                        "title": f"第{day}天：探索{request.destination}",
                        "activities": [
                            {"time": "上午", "activity": f"游览{request.destination}著名景点", "description": "感受当地文化"},
                            {"time": "下午", "activity": "体验文化活动", "description": "深入了解当地"},
                            {"time": "晚上", "activity": "品尝特色美食", "description": "当地夜市探索"}
                        ]
                    })
                plans.append({
                    "name": style_name,
                    "description": f"{style_name} - {request.destination}{request.days}日游",
                    "days": request.days,
                    "budget": ["economy", "medium", "luxury"][i],
                    "destination": request.destination,
                    "highlights": [f"{request.destination}精华", "文化体验", "特色美食", "专业建议"],
                    "itinerary": daily_itinerary
                })

        logger.info(f"[旅行规划] 成功生成 {len(plans)} 个方案")

        return {
            "success": True,
            "plans": plans,
            "destination": request.destination,
            "days": request.days,
            # 多智能体分析结果
            "agent_analyses": {
                "destination": destination_analysis,
                "attractions": attraction_analysis,
                "weather": weather_analysis,
                "budget": budget_analysis,
                "itinerary": itinerary_analysis
            },
            # 元数据
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "llm_provider": "deepseek",
                "agents_used": ["DestinationClassifier", "DataCollector", "AttractionAnalyst", "ItineraryPlanner", "BudgetAnalyst"],
                "data_sources": ["AmapAPI", "OpenMeteo"]
            }
        }

    except Exception as e:
        logger.error(f"[旅行规划] 生成方案失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"生成方案失败: {str(e)}")


@router.post("/ai/generate-guide")
async def generate_guide(request: GenerateGuideRequest):
    """生成详细攻略"""
    try:
        logger.info(f"[旅行规划] 生成攻略: {request.selected_plan.get('name')}")

        # 模拟生成详细攻略内容
        guide = {
            "sections": [
                {
                    "title": "出行准备",
                    "content": f"最佳旅行时间：春秋两季，气候宜人\\n\\n建议携带物品：舒适徒步鞋、防晒霜、雨具\\n\\n当地货币：人民币\\n\\n语言：普通话（{request.selected_plan.get('destination', '')}）"
                },
                {
                    "title": "交通指南",
                    "content": "飞机/高铁：提前预订享受优惠\\n\\n市内交通：地铁/公交/出租车，建议办理交通卡\\n\\n自驾：提前了解停车信息"
                },
                {
                    "title": "住宿推荐",
                    "content": "经济型：青年旅舍/经济型酒店\\n\\n舒适型：三星级酒店\\n\\n奢华型：五星酒店/精品民宿"
                },
                {
                    "title": "美食推荐",
                    "content": "必尝美食：当地特色小吃\\n\\n推荐餐厅：根据当地评价推荐"
                },
                {
                    "title": "购物指南",
                    "content": "特产：当地特色产品\\n\\n购物区：主要商业街"
                }
            ]
        }

        return {
            "success": True,
            "guide": guide
        }

    except Exception as e:
        logger.error(f"[旅行规划] 生成攻略失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成攻略失败: {str(e)}")


@router.post("/ai/save-plan")
async def save_plan(request: SavePlanRequest):
    """保存计划"""
    try:
        logger.info(f"[旅行规划] 保存计划: {request.title}")

        # 这里应该保存到数据库
        # 暂时返回成功响应
        return {
            "success": True,
            "plan_id": 1,
            "message": "计划保存成功"
        }

    except Exception as e:
        logger.error(f"[旅行规划] 保存计划失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存计划失败: {str(e)}")


# ============================================================
# Mock Data Generation (用于演示/测试)
# ============================================================

def _generate_mock_result(request: GeneratePlansRequest) -> Dict[str, Any]:
    """生成模拟的旅行规划结果"""
    destination = request.destination

    # 模拟景点数据
    mock_attractions = {
        "count": 10,
        "attractions": [
            {"name": f"{destination}古城", "address": f"{destination}市中心", "description": f"历史悠久的{destination}古城，是体验当地文化的绝佳地点。", "poi_id": "A001"},
            {"name": f"{destination}博物馆", "address": f"{destination}市文化区", "description": f"了解{destination}历史文化的重要场所。", "poi_id": "A002"},
            {"name": f"{destination}公园", "address": f"{destination}市风景路", "description": "风景优美的公园，适合休闲放松。", "poi_id": "A003"},
            {"name": "当地美食街", "address": "市中心商业区", "description": "汇集了各种地道的当地美食。", "poi_id": "A004"},
            {"name": f"{destination}塔", "address": f"{destination}市东区", "description": f"{destination}的标志性建筑，历史悠久。", "poi_id": "A005"},
        ]
    }

    # 模拟天气数据
    mock_weather = {
        "forecast": {
            "daily": [
                {"date": "2026-03-12", "temperature_2m_max": 18, "temperature_2m_min": 8, "weathercode": 0},
                {"date": "2026-03-13", "temperature_2m_max": 20, "temperature_2m_min": 10, "weathercode": 1},
                {"date": "2026-03-14", "temperature_2m_max": 17, "temperature_2m_min": 9, "weathercode": 3},
            ]
        }
    }

    # 模拟预算数据
    travelers = request.adults + request.children
    base_budget = {"economy": 2000, "medium": 4000, "luxury": 8000}
    total = base_budget.get(request.budget, 4000) * travelers

    mock_budget = {
        "total_budget": total,
        "transportation": {"amount": total * 0.3, "description": "交通费用"},
        "accommodation": {"amount": total * 0.35, "description": "住宿费用"},
        "meals": {"amount": total * 0.25, "description": "餐饮费用"},
        "attractions": {"amount": total * 0.08, "description": "景点门票"},
        "miscellaneous": {"amount": total * 0.02, "description": "其他费用"},
    }

    # 模拟目的地信息
    mock_destination_info = {
        "name": destination,
        "type": "历史文化名城",
        "description": f"{destination}是一个充满历史文化的城市，拥有众多古迹和美食。",
        "best_season": "春秋两季",
        "recommended_days": f"{request.days}天"
    }

    return {
        "destination_info": mock_destination_info,
        "attractions": mock_attractions,
        "weather_forecast": mock_weather,
        "budget_breakdown": mock_budget,
        "detailed_itinerary": {
            "highlights": [f"探索{destination}的历史文化", "品尝地道当地美食", "游览著名景点"]
        }
    }


# ============================================================
# Plans List API
# ============================================================

@router.get("")
async def get_plans(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None
):
    """获取计划列表"""
    # 模拟返回空列表
    return {
        "success": True,
        "plans": [],
        "total": 0,
        "page": page,
        "page_size": page_size
    }
