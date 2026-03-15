"""
分阶段旅行规划 API

基于 v3.0 分阶段渐进式设计
参考文档: docs/travel_project/10_STAGED_SYSTEM_DESIGN.md
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

router = APIRouter(tags=["staged-planning"])


# ============================================================
# 测试端点（放在最前面用于调试）
# ============================================================

@router.get("/test2")
async def test2():
    return {"ok": True, "path": "/test2"}

@router.get("/a")
async def test_a():
    return {"ok": True, "path": "/a"}

@router.get("/teststreamendpoint")
async def test_stream_endpoint():
    """测试流式端点路由是否正常"""
    return {
        "success": True,
        "message": "Stream endpoint routing works!",
        "router": "staged-planning",
        "path": "/teststreamendpoint"
    }


@router.get("/test_stream_endpoint")
async def test_stream_endpoint_underscore():
    """测试流式端点路由是否正常（下划线版本）"""
    return {
        "success": True,
        "message": "Stream endpoint routing works with underscore!",
        "router": "staged-planning",
        "path": "/test_stream_endpoint"
    }


# ============================================================
# LLM Helper Functions
# ============================================================

def get_llm_instance():
    """
    获取LLM实例用于智能体调用

    Returns:
        LLM实例或None
    """
    try:
        # 直接使用环境变量创建LLM（更可靠）
        provider = os.getenv("LLM_PROVIDER", "openai").lower()

        logger.info(f"🔧 [LLM] 正在创建LLM实例...")
        logger.info(f"   Provider: {provider}")

        if provider == "siliconflow":
            from langchain_openai import ChatOpenAI

            model = os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-7B-Instruct")
            base_url = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
            api_key = os.getenv("SILICONFLOW_API_KEY", "")

            if not api_key or "your_" in api_key:
                logger.warning("[LLM] SILICONFLOW_API_KEY未配置或使用占位符")
                return None

            llm = ChatOpenAI(
                model=model,
                api_key=api_key,
                base_url=base_url,
                temperature=0.7,
                max_tokens=8000,  # 增加到8000以支持更详细的行程
                timeout=120  # 增加超时时间到2分钟
            )

        elif provider == "deepseek":
            from langchain_openai import ChatOpenAI

            model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
            api_key = os.getenv("DEEPSEEK_API_KEY", "")

            if not api_key or "your_" in api_key:
                logger.warning("[LLM] DEEPSEEK_API_KEY未配置或使用占位符")
                return None

            llm = ChatOpenAI(
                model=model,
                api_key=api_key,
                base_url=base_url,
                temperature=0.7,
                max_tokens=8000,  # 增加到8000以支持更详细的行程
                timeout=120  # 增加超时时间到2分钟
            )

        elif provider == "dashscope":
            from langchain_community.chat_models.tongyi import ChatTongyi

            model = os.getenv("DASHSCOPE_MODEL", "qwen-turbo")
            api_key = os.getenv("DASHSCOPE_API_KEY", "")

            if not api_key or "your_" in api_key:
                logger.warning("[LLM] DASHSCOPE_API_KEY未配置或使用占位符")
                return None

            llm = ChatTongyi(
                model=model,
                dashscope_api_key=api_key,
                temperature=0.7,
                max_tokens=2000
            )

        elif provider == "google":
            from langchain_google_genai import ChatGoogleGenerativeAI

            model = os.getenv("GOOGLE_MODEL", "gemini-pro")
            api_key = os.getenv("GOOGLE_API_KEY", "")

            if not api_key or "your_" in api_key:
                logger.warning("[LLM] GOOGLE_API_KEY未配置或使用占位符")
                return None

            llm = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=api_key,
                temperature=0.7,
                max_tokens=2000
            )

        else:
            # 默认使用OpenAI
            from langchain_openai import ChatOpenAI

            model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            base_url = os.getenv("OPENAI_BASE_URL", "")
            api_key = os.getenv("OPENAI_API_KEY", "")

            if not api_key or "your_" in api_key:
                logger.warning("[LLM] OPENAI_API_KEY未配置或使用占位符")
                return None

            llm = ChatOpenAI(
                model=model,
                api_key=api_key,
                base_url=base_url if base_url else None,
                temperature=0.7,
                max_tokens=2000,
                timeout=60
            )

        logger.info(f"✅ [LLM] LLM实例创建成功!")
        logger.info(f"   Provider: {provider}")
        logger.info(f"   Model: {getattr(llm, 'model_name', getattr(llm, 'model', 'unknown'))}")
        logger.info(f"   智能体将使用LLM进行智能分析和生成")
        return llm

    except Exception as e:
        logger.error(f"❌ [LLM] LLM实例创建失败: {e}")
        import traceback
        logger.error(f"   详细错误: {traceback.format_exc()}")
        logger.warning(f"⚠️ [规则引擎] 系统将使用规则引擎运行，智能体功能受限")
        logger.warning(f"⚠️ [配置提示] 请在.env文件中配置有效的LLM API Key:")
        logger.warning(f"   - SILICONFLOW_API_KEY (硅基流动+千问2.5 - 推荐)")
        logger.warning(f"   - DEEPSEEK_API_KEY (DeepSeek)")
        logger.warning(f"   - OPENAI_API_KEY (OpenAI GPT)")
        logger.warning(f"   - GOOGLE_API_KEY (Google Gemini)")
        logger.warning(f"   - DASHSCOPE_API_KEY (阿里云通义千问)")
        return None


# ============================================================
# Request Models
# ============================================================

class TravelRequirementForm(BaseModel):
    """旅行需求表单"""
    travel_scope: str  # domestic / international
    start_date: str
    days: int
    adults: int
    children: int
    budget: str  # economy / medium / luxury
    interests: List[str]
    special_requests: str = ""


# ============================================================
# 阶段2: 提交需求表单
# ============================================================

@router.post("/submit-requirements")
async def submit_requirements(request: TravelRequirementForm):
    """
    提交旅行需求表单

    阶段2 API - 收集用户需求
    """
    try:
        logger.info(f"[分阶段规划] 提交需求: {request.travel_scope}, {request.days}天")

        # 生成会话ID
        session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # TODO: 存储到Redis/数据库

        return {
            "success": True,
            "session_id": session_id,
            "message": "需求已提交，请选择目的地范围"
        }
    except Exception as e:
        logger.error(f"[分阶段规划] 提交需求失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 阶段3: 获取推荐地区 (SSE流式版本)
# ============================================================

@router.get("/get-destinations-stream-test")
async def test_destinations_stream_endpoint():
    """测试流式端点是否注册"""
    return {
        "success": True,
        "message": "Streaming endpoint is registered!",
        "endpoint": "/get-destinations-stream"
    }


@router.post("/get-destinations-stream")
async def get_destinations_stream(request: TravelRequirementForm):
    """
    获取推荐地区 (SSE流式版本)

    实时显示组A智能体的工作进度：
    1. UserRequirementAnalyst - 分析需求
    2. DestinationMatcher - 匹配目的地
    3. RankingScorer - 排序推荐
    """
    from fastapi.responses import StreamingResponse
    import asyncio
    import json

    async def event_generator():
        try:
            logger.info(f"[分阶段规划] 流式获取推荐地区: {request.travel_scope}")

            # 获取LLM实例
            llm = get_llm_instance()
            llm_status = "enabled" if llm else "disabled"

            # 发送开始事件
            yield f"data: {json.dumps({'type': 'start', 'scope': request.travel_scope, 'llm_enabled': llm_status}, ensure_ascii=False)}\n\n"

            # 步骤1: 需求分析
            yield f"data: {json.dumps({'type': 'progress', 'step': '正在分析您的旅行需求...', 'agent': 'UserRequirementAnalyst', 'progress': 10}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.3)

            # 步骤2: 匹配目的地
            yield f"data: {json.dumps({'type': 'progress', 'step': '正在匹配适合的目的地...', 'agent': 'DestinationMatcher', 'progress': 30}, ensure_ascii=False)}\n\n"

            from tradingagents.agents.group_a import recommend_destinations
            requirements = request.dict()

            # 调用组A智能体
            result = recommend_destinations(requirements, llm=llm)

            # 发送用户画像结果
            yield f"data: {json.dumps({\"type\": \"step_result\", \"step\": \"用户需求分析完成\", \"agent\": \"UserRequirementAnalyst\", \"data\": {
                \"description\": result['user_portrait'].get('description', ''),
                \"travel_type\": result['user_portrait'].get('travel_type', ''),
                \"pace_preference\": result['user_portrait'].get('pace_preference', ''),
                \"budget_level\": result['user_portrait'].get('budget_level', ''),
                \"interests\": requirements.get('interests', []),
                \"llm_description\": result['user_portrait'].get('llm_description', '')
            }, \"progress\": 50}, ensure_ascii=False)}\n\n"

            # 步骤3: 排序推荐
            yield f"data: {json.dumps({'type': 'progress', 'step': '正在综合评分和排序...', 'agent': 'RankingScorer', 'progress': 70}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.3)

            # 发送目的地匹配结果
            yield f"data: {json.dumps({'type': 'step_result', 'step': '目的地匹配完成', 'agent': 'DestinationMatcher', 'data': {
                'matched_count': len(result['destinations']),
                'top_destinations': [
                    {'name': d.get('destination', ''), 'score': d.get('match_score', 0)}
                    for d in result['destinations'][:5]
                ],
                'llm_description': result.get('matching_llm_description', '')
            }, 'progress': 85}, ensure_ascii=False)}\n\n"

            # 最终排序结果
            yield f"data: {json.dumps({'type': 'step_result', 'step': '推荐排序完成', 'agent': 'RankingScorer', 'data': {
                'total_count': len(result['destinations']),
                'recommended_destinations': result['destinations'],
                'llm_description': result.get('ranking_llm_description', '')
            }, 'progress': 95}, ensure_ascii=False)}\n\n"

            # 完成
            yield f"data: {json.dumps({'type': 'complete', 'progress': 100, 'destinations': result['destinations'], 'user_portrait': {
                'description': result['user_portrait']['description'],
                'travel_type': result['user_portrait']['travel_type'],
                'pace_preference': result['user_portrait']['pace_preference'],
                'budget_level': result['user_portrait']['budget_level']
            }}, ensure_ascii=False)}\n\n"

            logger.info(f"[分阶段规划] 推荐完成: {len(result['destinations'])}个目的地")

        except Exception as e:
            logger.error(f"[分阶段规划] 流式获取推荐地区失败: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ============================================================
# 阶段3: 获取推荐地区 (非流式版本)
# ============================================================

@router.post("/get-destinations")
async def get_destinations(req: Request):
    """
    获取推荐地区（简化版）
    """
    try:
        # 从Request获取JSON数据
        import json
        body = await req.body()
        request_data = json.loads(body)

        # 简化版：直接返回模拟数据
        logger.info(f"[分阶段规划] 获取推荐地区: {request_data.get('travel_scope', 'domestic')}")

        return {
            "destinations": [
                {
                    "destination": "北京",
                    "match_score": 95,
                    "recommendation_reason": "文化古都，适合文化旅游爱好者",
                    "estimated_budget": {
                        "total": 5000,
                        "per_person": 2500,
                        "currency": "CNY"
                    },
                    "best_season": "春秋季(3-5月,9-11月)",
                    "suitable_for": ["文化爱好者", "历史迷", "家庭出游"],
                    "highlights": ["故宫博物院", "万里长城", "天坛公园", "颐和园"],
                    "tags": ["历史", "文化", "美食"]
                },
                {
                    "destination": "西安",
                    "match_score": 90,
                    "recommendation_reason": "十三朝古都，历史文化深厚",
                    "estimated_budget": {
                        "total": 4500,
                        "per_person": 2250,
                        "currency": "CNY"
                    },
                    "best_season": "春秋季",
                    "suitable_for": ["文化爱好者", "历史迷"],
                    "highlights": ["兵马俑", "大雁塔", "古城墙", "回民街"],
                    "tags": ["历史", "文化", "美食"]
                },
                {
                    "destination": "南京",
                    "match_score": 85,
                    "recommendation_reason": "六朝古都，文化底蕴深厚",
                    "estimated_budget": {
                        "total": 4200,
                        "per_person": 2100,
                        "currency": "CNY"
                    },
                    "best_season": "春季",
                    "suitable_for": ["文化爱好者", "历史学习者"],
                    "highlights": ["中山陵", "夫子庙", "明孝陵", "秦淮河"],
                    "tags": ["历史", "文化", "教育"]
                }
            ],
            "user_portrait": {
                "description": "您是一位热爱文化旅游的旅行者，对历史文化有着浓厚的兴趣",
                "travel_type": "文化探索型",
                "pace_preference": "适中节奏",
                "budget_level": request_data.get("budget", "medium"),
                "interests": request_data.get("interests", [])
            },
            "agent_analysis": {
                "agent_name": "组A智能体",
                "agents": ["UserRequirementAnalyst", "DestinationMatcher", "RankingScorer"],
                "description": "分析需求、匹配目的地、综合评分推荐",
                "llm_enabled": True
            }
        }

    except Exception as e:
        logger.error(f"[分阶段规划] 获取推荐地区失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 阶段4: 获取风格方案 (SSE流式版本)
# ============================================================

class GetStylesRequest(BaseModel):
    """获取风格方案请求"""
    destination: str
    user_requirements: Dict[str, Any]  # 包含用户需求信息


@router.post("/get-styles-stream")
async def get_styles_stream(request: GetStylesRequest):
    """
    获取风格方案 (SSE流式版本)

    实时显示组B智能体的工作进度：
    1. ImmersiveDesigner - 沉浸式方案
    2. ExplorationDesigner - 探索式方案
    3. RelaxationDesigner - 松弛式方案
    4. HiddenGemDesigner - 小众宝藏方案
    """
    from fastapi.responses import StreamingResponse
    import asyncio
    import json

    async def event_generator():
        try:
            logger.info(f"[分阶段规划] 流式获取风格方案: {request.destination}")

            # 获取LLM实例
            llm = get_llm_instance()

            # 发送开始事件
            yield f"data: {json.dumps({'type': 'start', 'destination': request.destination}, ensure_ascii=False)}\n\n"

            # 获取目的地数据
            travel_scope = request.user_requirements.get("travel_scope", "domestic")
            from tradingagents.agents.group_a import DOMESTIC_DESTINATIONS_DB, INTERNATIONAL_DESTINATIONS_DB
            from tradingagents.utils.destination_utils import normalize_destination_name

            if travel_scope == "domestic":
                dest_db = DOMESTIC_DESTINATIONS_DB
            else:
                dest_db = INTERNATIONAL_DESTINATIONS_DB

            # 标准化目的地名称（处理英文名称）
            destination_cn = normalize_destination_name(request.destination)
            dest_data = dest_db.get(destination_cn, {})
            if not dest_data:
                yield f"data: {json.dumps({'type': 'error', 'message': f'目的地 {request.destination} 未找到'}, ensure_ascii=False)}\n\n"
                return

            user_portrait = request.user_requirements.get("user_portrait", {})
            days = request.user_requirements.get("days", 5)

            # 🚀 并行执行4个风格设计师
            yield f"data: {json.dumps({'type': 'progress', 'step': '4个风格设计师正在并行工作...', 'agent': '组B智能体', 'progress': 10}, ensure_ascii=False)}\n\n"

            from tradingagents.agents.group_b import generate_style_proposals_parallel

            all_styles = await generate_style_proposals_parallel(
                destination_cn,
                dest_data,
                user_portrait,
                days,
                llm=llm
            )

            # 发送每个风格的完成结果
            for idx, style in enumerate(all_styles):
                progress = 20 + (idx + 1) * 15
                style_name = style.get('style_name', '')
                style_type = style.get('style_type', '').capitalize()
                yield f"data: {json.dumps({'type': 'step_result', 'step': f'{style_name}方案完成', 'agent': f'{style_type}Designer', 'data': {
                    'style_name': style.get('style_name'),
                    'style_type': style.get('style_type'),
                    'description': style.get('style_description'),
                    'daily_pace': style.get('daily_pace'),
                    'intensity': style.get('intensity_level'),
                    'preview_count': len(style.get('preview_itinerary', [])),
                    'llm_description': style.get('llm_description', '')
                }, 'progress': progress, 'llm_description': style.get('llm_description', '')}, ensure_ascii=False)}\n\n"

            # 完成
            yield f"data: {json.dumps({'type': 'complete', 'progress': 100, 'styles': all_styles, 'destination_info': {
                'destination': request.destination,
                'highlights': dest_data.get('highlights', [])[:5],
                'best_season': dest_data.get('best_season', ''),
                'tags': dest_data.get('tags', [])[:5]
            }}, ensure_ascii=False)}\n\n"

            logger.info(f"[分阶段规划] 风格方案生成完成: {len(all_styles)}个方案")

        except Exception as e:
            logger.error(f"[分阶段规划] 流式获取风格方案失败: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ============================================================
# 阶段4: 获取风格方案 (非流式版本)
# ============================================================

@router.post("/get-styles")
async def get_styles(req: Request):
    """
    获取风格方案（简化版）
    """
    try:
        # 从Request获取JSON数据
        import json
        body = await req.body()
        request_data = json.loads(body)

        # 简化版：直接返回模拟数据
        logger.info(f"[分阶段规划] 获取风格方案: {request_data.get('destination', '北京')}")

        return {
            "styles": [
                {
                    "style_name": "深度文化游",
                    "style_icon": "🏛️",
                    "style_type": "immersive",
                    "style_description": "深入体验当地文化历史，参观博物馆和历史古迹",
                    "daily_pace": "适中",
                    "intensity_level": 3,
                    "preview_itinerary": [
                        {"day": 1, "title": "文化探索", "attractions": ["博物馆", "古建筑", "文化街区"]},
                        {"day": 2, "title": "历史足迹", "attractions": ["历史遗迹", "文化公园", "传统工艺"]}
                    ],
                    "estimated_cost": 3000,
                    "best_for": "文化爱好者、历史学习者",
                    "highlights": ["专业讲解", "深度体验", "文化沉浸"]
                },
                {
                    "style_name": "轻松休闲游",
                    "style_icon": "🌸",
                    "style_type": "relax",
                    "style_description": "悠闲自在的旅行方式，注重舒适度和体验感",
                    "daily_pace": "慢节奏",
                    "intensity_level": 2,
                    "preview_itinerary": [
                        {"day": 1, "title": "轻松漫步", "attractions": ["公园", "咖啡厅", "购物中心"]},
                        {"day": 2, "title": "休闲时光", "attractions": ["SPA", "美食街", "夜景"]}
                    ],
                    "estimated_cost": 3500,
                    "best_for": "都市白领、休闲度假",
                    "highlights": ["舒适度高", "自由度高", "轻松自在"]
                },
                {
                    "style_name": "探索发现游",
                    "style_icon": "🧭",
                    "style_type": "exploration",
                    "style_description": "探索小众景点和隐秘角落，发现不一样的城市",
                    "daily_pace": "较快",
                    "intensity_level": 4,
                    "preview_itinerary": [
                        {"day": 1, "title": "小众景点", "attractions": ["隐藏景点", "本地市场", "艺术区"]},
                        {"day": 2, "title": "城市探索", "attractions": ["老街巷", "创意园区", "独立书店"]}
                    ],
                    "estimated_cost": 2800,
                    "best_for": "背包客、探险爱好者",
                    "highlights": ["独特体验", "摄影圣地", "本地文化"]
                },
                {
                    "style_name": "经典必游",
                    "style_icon": "⭐",
                    "style_type": "classic",
                    "style_description": "打卡所有必游景点，不留遗憾",
                    "daily_pace": "紧凑",
                    "intensity_level": 5,
                    "preview_itinerary": [
                        {"day": 1, "title": "必游景点", "attractions": ["著名景点1", "著名景点2", "著名景点3"]},
                        {"day": 2, "title": "地标打卡", "attractions": ["地标建筑", "观景台", "纪念地"]}
                    ],
                    "estimated_cost": 4000,
                    "best_for": "首次到访者、打卡达人",
                    "highlights": ["全面覆盖", "经典路线", "不留遗憾"]
                }
            ],
            "destination_info": {
                "destination": request_data.get("destination", "北京"),
                "highlights": ["文化", "历史", "美食"],
                "best_season": "春秋季",
                "tags": ["历史", "文化", "美食"]
            }
        }

    except Exception as e:
        logger.error(f"[分阶段规划] 获取风格方案失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

        return response

    except Exception as e:
        logger.error(f"[分阶段规划] 获取风格方案失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 阶段5: 生成详细攻略
# ============================================================

class GenerateGuideRequest(BaseModel):
    """生成详细攻略请求"""
    destination: str
    style_type: str  # immersive, exploration, relaxation, hidden_gem
    user_requirements: Dict[str, Any]  # 包含用户需求信息


@router.post("/generate-guide")
async def generate_guide(request: GenerateGuideRequest):
    """
    生成详细攻略

    阶段5 API - 调用组C智能体：
    1. AttractionScheduler - 景点排程师
    2. TransportPlanner - 交通规划师
    3. DiningRecommender - 餐饮推荐师
    4. AccommodationAdvisor - 住宿顾问
    5. GuideFormatter - 攻略格式化师
    """
    try:
        logger.info(f"[分阶段规划] 生成详细攻略: {request.destination}, 风格: {request.style_type}")

        # 获取LLM实例
        llm = get_llm_instance()
        if llm:
            logger.info("[分阶段规划] 使用LLM增强智能体输出")
        else:
            logger.warning("[分阶段规划] 未配置LLM，使用规则引擎")

        # 获取目的地数据
        travel_scope = request.user_requirements.get("travel_scope", "domestic")
        from tradingagents.agents.group_a import DOMESTIC_DESTINATIONS_DB, INTERNATIONAL_DESTINATIONS_DB
        from tradingagents.utils.destination_utils import normalize_destination_name

        if travel_scope == "domestic":
            dest_db = DOMESTIC_DESTINATIONS_DB
        else:
            dest_db = INTERNATIONAL_DESTINATIONS_DB

        # 标准化目的地名称（处理英文名称）
        destination_cn = normalize_destination_name(request.destination)

        dest_data = dest_db.get(destination_cn, {})
        if not dest_data:
            raise HTTPException(status_code=404, detail=f"目的地 {request.destination} 未找到")

        # 获取用户信息
        user_portrait = request.user_requirements.get("user_portrait", {})
        days = request.user_requirements.get("days", 5)
        start_date = request.user_requirements.get("start_date", datetime.now().strftime("%Y-%m-%d"))

        # 首先生成风格方案以获取选定风格的详细行程
        from tradingagents.agents.group_b import generate_style_proposals

        all_styles = generate_style_proposals(
            request.destination,
            dest_data,
            user_portrait,
            days,
            llm=llm
        )

        # 找到选定的风格
        selected_style = None
        for style in all_styles:
            if style.get("style_type") == request.style_type:
                selected_style = style
                break

        if not selected_style:
            # 如果没找到，使用第一个
            selected_style = all_styles[0]

        # 调用组C智能体生成详细攻略（使用工具增强版）
        import importlib
        import tradingagents.services.tool_enhanced_guide_generator as teg_module
        importlib.reload(teg_module)  # 强制重新加载模块
        from tradingagents.services.tool_enhanced_guide_generator import create_tool_enhanced_guide_generator

        # 使用工具增强版生成器
        generator = create_tool_enhanced_guide_generator(llm)
        logger.info(f"[分阶段规划] 工具增强版生成器已加载（模块版本: {id(teg_module)}）")

        # 准备基础攻略数据
        daily_itin = selected_style.get("daily_itinerary", selected_style.get("preview_itinerary", []))
        logger.info(f"[分阶段规划] selected_style keys: {list(selected_style.keys())}")
        logger.info(f"[分阶段规划] daily_itinerary数量: {len(daily_itin)}")
        if daily_itin:
            logger.info(f"[分阶段规划] 第一天keys: {list(daily_itin[0].keys())}")
            logger.info(f"[分阶段规划] 第一天activities数量: {len(daily_itin[0].get('activities', []))}")

        # 预处理：手动将activities转换为schedule，确保数据不丢失
        time_mapping = {
            "上午": "morning",
            "中午": "lunch",
            "下午": "afternoon",
            "晚上": "evening"
        }
        period_fallback = ["morning", "lunch", "afternoon", "evening"]
        time_ranges = {
            "morning": "09:00-12:00",
            "lunch": "12:00-13:30",
            "afternoon": "14:00-17:00",
            "dinner": "18:00-20:00",
            "evening": "20:00-21:30"
        }

        # 为每一天添加schedule字段（从activities转换）
        for day_data in daily_itin:
            if 'activities' in day_data and day_data['activities']:
                schedule = []
                for idx, activity in enumerate(day_data['activities']):
                    time_cn = activity.get('time', '')
                    period = time_mapping.get(time_cn, '')

                    if not period and idx < len(period_fallback):
                        period = period_fallback[idx]

                    if period:
                        schedule.append({
                            "period": period,
                            "time_range": time_ranges.get(period, ""),
                            "activity": activity.get('activity', ''),
                            "location": activity.get('attraction_id', activity.get('activity', '')),
                            "description": activity.get('description', ''),
                            "expanded": False
                        })
                day_data['schedule'] = schedule
                logger.info(f"[分阶段规划] 第{day_data.get('day')}天预填充了{len(schedule)}个schedule项")

        basic_guide_data = {
            "destination": request.destination,
            "total_days": days,
            "start_date": start_date,
            "daily_itineraries": daily_itin
        }

        # 生成详细攻略（调用真实API工具）
        logger.info(f"[分阶段规划] 调用generator前 basic_guide_data['daily_itineraries'] 数量: {len(basic_guide_data['daily_itineraries'])}")
        if basic_guide_data['daily_itineraries']:
            logger.info(f"[分阶段规划] 第一天数据: {list(basic_guide_data['daily_itineraries'][0].keys())}")
            logger.info(f"[分阶段规划] 第一天activities数量: {len(basic_guide_data['daily_itineraries'][0].get('activities', []))}")

        detailed_guide = generator.generate_detailed_guide(basic_guide_data)

        # Fallback: 如果schedule为空，手动从activities提取并填充
        if detailed_guide['daily_itineraries'] and detailed_guide['daily_itineraries'][0]['schedule'] == []:
            logger.info(f"[分阶段规划] 检测到空schedule，手动提取activities数据")

            # 时间映射
            time_mapping = {
                "上午": "morning",
                "中午": "lunch",
                "下午": "afternoon",
                "晚上": "evening"
            }
            period_fallback = ["morning", "lunch", "afternoon", "evening"]
            time_ranges = {
                "morning": "09:00-12:00",
                "lunch": "12:00-13:30",
                "afternoon": "14:00-17:00",
                "dinner": "18:00-20:00",
                "evening": "20:00-21:30"
            }

            for day_data in detailed_guide['daily_itineraries']:
                if 'activities' in day_data and day_data['activities']:
                    schedule = []
                    for idx, activity in enumerate(day_data['activities']):
                        time_cn = activity.get('time', '')
                        period = time_mapping.get(time_cn, '')

                        # Fallback到索引
                        if not period and idx < len(period_fallback):
                            period = period_fallback[idx]

                        if period:
                            schedule_item = {
                                "period": period,
                                "time_range": time_ranges.get(period, ""),
                                "activity": activity.get('activity', ''),
                                "location": activity.get('attraction_id', activity.get('activity', '')),
                                "description": activity.get('description', ''),
                                "expanded": False
                            }
                            schedule.append(schedule_item)

                    day_data['schedule'] = schedule
                    logger.info(f"[分阶段规划] 第{day_data.get('day')}天手动填充了{len(schedule)}个schedule项")

        logger.info(f"[分阶段规划] 最终detailed_guide第一天schedule数量: {len(detailed_guide['daily_itineraries'][0]['schedule'])}")

        # 最终兜底：如果schedule仍然为空，直接从selected_style的activities填充
        if detailed_guide['daily_itineraries'] and detailed_guide['daily_itineraries'][0]['schedule'] == []:
            logger.warning("[分阶段规划] 最终兜底：schedule为空，从selected_style填充")
            time_mapping = {"上午": "morning", "中午": "lunch", "下午": "afternoon", "晚上": "evening"}
            period_fallback = ["morning", "lunch", "afternoon", "evening"]
            time_ranges = {"morning": "09:00-12:00", "lunch": "12:00-13:30", "afternoon": "14:00-17:00", "dinner": "18:00-20:00", "evening": "20:00-21:30"}

            for day_idx, detailed_day in enumerate(detailed_guide['daily_itineraries']):
                if day_idx < len(daily_itin) and 'activities' in daily_itin[day_idx] and daily_itin[day_idx]['activities']:
                    schedule = []
                    for act_idx, activity in enumerate(daily_itin[day_idx]['activities']):
                        time_cn = activity.get('time', '')
                        period = time_mapping.get(time_cn, '')
                        if not period and act_idx < len(period_fallback):
                            period = period_fallback[act_idx]
                        if period:
                            schedule.append({
                                "period": period,
                                "time_range": time_ranges.get(period, ""),
                                "activity": activity.get('activity', ''),
                                "location": activity.get('attraction_id', activity.get('activity', '')),
                                "description": activity.get('description', ''),
                                "expanded": False,
                                "type": "attraction" if period in ["morning", "afternoon", "evening"] else "dining"
                            })
                    detailed_day['schedule'] = schedule
                    logger.info(f"[分阶段规划] 最终兜底第{day_idx+1}天填充了{len(schedule)}个schedule项")

        # 构建响应
        response = {
            "success": True,
            "guide": detailed_guide,
            "agent_analysis": {
                "agent_name": "组C智能体",
                "agents": [
                    "AttractionScheduler",
                    "TransportPlanner",
                    "DiningRecommender",
                    "AccommodationAdvisor",
                    "GuideFormatter"
                ],
                "description": "生成包含景点、交通、餐饮、住宿的完整详细攻略",
                "llm_enabled": llm is not None
            }
        }

        logger.info(f"[分阶段规划] 详细攻略生成完成: {days}天完整行程")

        return response

    except Exception as e:
        logger.error(f"[分阶段规划] 生成详细攻略失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 测试端点
# ============================================================

@router.get("/destinations-simple")
async def get_destinations_simple():
    """获取推荐目的地（超简化版，不需要参数）"""
    return {
        "destinations": [
            {
                "destination": "北京",
                "match_score": 95,
                "recommendation_reason": "文化古都，适合文化旅游爱好者",
                "estimated_budget": {
                    "total": 5000,
                    "per_person": 2500,
                    "currency": "CNY"
                },
                "best_season": "春秋季(3-5月,9-11月)",
                "suitable_for": ["文化爱好者", "历史迷", "家庭出游"],
                "highlights": ["故宫博物院", "万里长城", "天坛公园", "颐和园"],
                "tags": ["历史", "文化", "美食"]
            },
            {
                "destination": "西安",
                "match_score": 90,
                "recommendation_reason": "十三朝古都，历史文化深厚",
                "estimated_budget": {
                    "total": 4500,
                    "per_person": 2250,
                    "currency": "CNY"
                },
                "best_season": "春秋季",
                "suitable_for": ["文化爱好者", "历史迷"],
                "highlights": ["兵马俑", "大雁塔", "古城墙", "回民街"],
                "tags": ["历史", "文化", "美食"]
            },
            {
                "destination": "南京",
                "match_score": 85,
                "recommendation_reason": "六朝古都，文化底蕴深厚",
                "estimated_budget": {
                    "total": 4200,
                    "per_person": 2100,
                    "currency": "CNY"
                },
                "best_season": "春季",
                "suitable_for": ["文化爱好者", "历史学习者"],
                "highlights": ["中山陵", "夫子庙", "明孝陵", "秦淮河"],
                "tags": ["历史", "文化", "教育"]
            }
        ],
        "user_portrait": {
            "description": "您是一位热爱文化旅游的旅行者",
            "travel_type": "文化探索型",
            "pace_preference": "适中节奏",
            "budget_level": "medium",
            "interests": ["文化", "历史"]
        }
    }


@router.get("/styles-simple")
async def get_styles_simple():
    """获取风格方案（超简化版，不需要参数）"""
    return {
        "styles": [
            {
                "style_name": "深度文化游",
                "style_icon": "🏛️",
                "style_type": "immersive",
                "style_description": "深入体验当地文化历史",
                "daily_pace": "适中",
                "intensity_level": 3,
                "preview_itinerary": [
                    {"day": 1, "title": "文化探索", "attractions": ["博物馆", "古建筑"]},
                    {"day": 2, "title": "历史足迹", "attractions": ["历史遗迹", "文化公园"]}
                ],
                "estimated_cost": 3000,
                "best_for": "文化爱好者",
                "highlights": ["专业讲解", "深度体验"]
            },
            {
                "style_name": "轻松休闲游",
                "style_icon": "🌸",
                "style_type": "relax",
                "style_description": "悠闲自在的旅行方式",
                "daily_pace": "慢节奏",
                "intensity_level": 2,
                "preview_itinerary": [
                    {"day": 1, "title": "轻松漫步", "attractions": ["公园", "咖啡厅"]},
                    {"day": 2, "title": "休闲时光", "attractions": ["SPA", "美食街"]}
                ],
                "estimated_cost": 3500,
                "best_for": "都市白领",
                "highlights": ["舒适度高", "自由度高"]
            },
            {
                "style_name": "探索发现游",
                "style_icon": "🧭",
                "style_type": "exploration",
                "style_description": "探索小众景点",
                "daily_pace": "较快",
                "intensity_level": 4,
                "preview_itinerary": [
                    {"day": 1, "title": "小众景点", "attractions": ["隐藏景点", "本地市场"]},
                    {"day": 2, "title": "城市探索", "attractions": ["老街巷", "创意园区"]}
                ],
                "estimated_cost": 2800,
                "best_for": "背包客",
                "highlights": ["独特体验", "摄影圣地"]
            },
            {
                "style_name": "经典必游",
                "style_icon": "⭐",
                "style_type": "classic",
                "style_description": "打卡所有必游景点",
                "daily_pace": "紧凑",
                "intensity_level": 5,
                "preview_itinerary": [
                    {"day": 1, "title": "必游景点", "attractions": ["著名景点1", "著名景点2"]},
                    {"day": 2, "title": "地标打卡", "attractions": ["地标建筑", "观景台"]}
                ],
                "estimated_cost": 4000,
                "best_for": "首次到访者",
                "highlights": ["全面覆盖", "经典路线"]
            }
        ],
        "destination_info": {
            "destination": "北京",
            "highlights": ["文化", "历史"],
            "best_season": "春秋季",
            "tags": ["历史", "文化"]
        }
    }


@router.get("/test")
async def test_staged_api():
    """测试API是否可用"""
    return {
        "success": True,
        "message": "Staged Planning API is working!",
        "version": "v3.0",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/get-destinations-stream")
async def get_destinations_stream_simple(request: TravelRequirementForm):
    """流式获取推荐目的地（简化版）"""
    from fastapi.responses import StreamingResponse
    import json

    async def generate():
        yield f"data: {json.dumps({'type': 'start', 'message': '开始处理...'}, ensure_ascii=False)}\n\n"
        await __import__('asyncio').sleep(0.5)
        yield f"data: {json.dumps({'type': 'progress', 'step': '分析需求中...', 'progress': 30}, ensure_ascii=False)}\n\n"
        await __import__('asyncio').sleep(0.5)
        yield f"data: {json.dumps({'type': 'progress', 'step': '匹配目的地...', 'progress': 60}, ensure_ascii=False)}\n\n"
        await __import__('asyncio').sleep(0.5)
        yield f"data: {json.dumps({'type': 'complete', 'progress': 100, 'destinations': [], 'user_portrait': {'description': '测试用户画像'}}, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# ============================================================
# 阶段5: 流式生成详细攻略 (SSE)
# ============================================================

@router.post("/generate-guide-stream")
async def generate_guide_stream(request: GenerateGuideRequest):
    """
    流式生成详细攻略 (SSE)

    阶段5 流式API - 实时显示每个智能体的工作进度
    """
    from fastapi.responses import StreamingResponse
    import asyncio
    import json

    async def event_generator():
        try:
            logger.info(f"[分阶段规划] 流式生成详细攻略: {request.destination}")

            # 获取LLM实例
            llm = get_llm_instance()
            llm_status = "enabled" if llm else "disabled"

            # 发送开始事件
            yield f"data: {json.dumps({'type': 'start', 'destination': request.destination, 'llm_enabled': llm_status}, ensure_ascii=False)}\n\n"

            # 获取目的地数据
            travel_scope = request.user_requirements.get("travel_scope", "domestic")
            from tradingagents.agents.group_a import DOMESTIC_DESTINATIONS_DB, INTERNATIONAL_DESTINATIONS_DB
            from tradingagents.utils.destination_utils import normalize_destination_name

            if travel_scope == "domestic":
                dest_db = DOMESTIC_DESTINATIONS_DB
            else:
                dest_db = INTERNATIONAL_DESTINATIONS_DB

            # 标准化目的地名称（处理英文名称）
            destination_cn = normalize_destination_name(request.destination)

            dest_data = dest_db.get(destination_cn, {})
            if not dest_data:
                yield f"data: {json.dumps({'type': 'error', 'message': f'目的地 {request.destination} 未找到'}, ensure_ascii=False)}\n\n"
                return

            # 获取用户信息
            user_portrait = request.user_requirements.get("user_portrait", {})
            days = request.user_requirements.get("days", 5)
            start_date = request.user_requirements.get("start_date", datetime.now().strftime("%Y-%m-%d"))

            # 步骤1: 生成风格方案
            yield f"data: {json.dumps({'type': 'progress', 'step': '智能体并行工作中...', 'agent': 'Group B', 'progress': 10}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.2)

            # 🚀 使用并行版本：4个风格设计师同时工作
            from tradingagents.agents.group_b import generate_style_proposals_parallel
            all_styles = await generate_style_proposals_parallel(
                destination_cn,  # 使用中文名称
                dest_data,
                user_portrait,
                days,
                llm=llm
            )

            # 找到选定的风格
            selected_style = None
            for style in all_styles:
                if style.get("style_type") == request.style_type:
                    selected_style = style
                    break

            if not selected_style:
                selected_style = all_styles[0]

            # 发送详细的风格方案数据
            yield f"data: {json.dumps({'type': 'step_result', 'step': '风格方案生成', 'agent': '组B智能体', 'data': {
                'style_count': len(all_styles),
                'selected': request.style_type,
                'style_name': selected_style.get('style_name', ''),
                'style_description': selected_style.get('style_description', ''),
                'data_source': selected_style.get('data_source', 'unknown'),
                'all_styles': [
                    {
                        'name': s.get('style_name'),
                        'type': s.get('style_type'),
                        'description': s.get('style_description'),
                        'intensity': s.get('intensity_level'),
                        'pace': s.get('daily_pace')
                    } for s in all_styles
                ]
            }, 'progress': 20}, ensure_ascii=False)}\n\n"

            # 步骤2: 景点排程
            yield f"data: {json.dumps({'type': 'progress', 'step': '景点排程中', 'agent': 'AttractionScheduler', 'progress': 30}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.3)

            from tradingagents.agents.group_c import schedule_attractions

            logger.info(f"[分阶段规划] 开始景点排程，目的地: {destination_cn}, 天数: {days}")

            schedule_result = schedule_attractions(
                destination_cn,  # 使用中文名称
                dest_data,
                selected_style,
                days,
                start_date,
                llm
            )

            logger.info(f"[分阶段规划] schedule_result 类型: {type(schedule_result)}, 内容类型: {type(schedule_result) if not hasattr(schedule_result, '__class__') else schedule_result.__class__.__name__}")

            # 确保 schedule_result 是标准字典
            # 某些 LangChain 或其他框架可能返回特殊的字典子类
            try:
                # 将结果转换为标准字典
                if hasattr(schedule_result, 'dict'):
                    # 如果是 Pydantic 模型或其他有 .dict() 方法的对象
                    schedule_dict = schedule_result.dict()
                elif hasattr(schedule_result, '__dict__'):
                    # 如果是普通对象
                    schedule_dict = schedule_result.__dict__
                elif isinstance(schedule_result, dict):
                    # 如果是字典，确保是标准 dict
                    schedule_dict = dict(schedule_result)
                else:
                    # 尝试直接转换
                    schedule_dict = dict(schedule_result)

                scheduled_attractions = schedule_dict.get("scheduled_attractions", [])
                llm_description = schedule_dict.get("llm_description", "")

                logger.info(f"[分阶段规划] 成功提取 scheduled_attractions: {len(scheduled_attractions)} 天")

            except Exception as e:
                logger.error(f"[分阶段规划] 处理 schedule_result 失败: {e}, 类型: {type(schedule_result)}")
                scheduled_attractions = []
                llm_description = ""

            # 确保 scheduled_attractions 是列表类型
            if scheduled_attractions is None:
                scheduled_attractions = []
            elif not isinstance(scheduled_attractions, list):
                # 如果是其他类型，尝试转换为列表或使用空列表
                try:
                    scheduled_attractions = list(scheduled_attractions)
                except (TypeError, ValueError):
                    scheduled_attractions = []

            # 发送详细的景点排程数据
            daily_schedule_summary = []
            # 只发送前3天的详情
            for day_schedule in scheduled_attractions[:3]:
                day_num = day_schedule.get('day', 0)
                schedule_items = day_schedule.get('schedule', [])
                attractions = [item.get('activity', '') for item in schedule_items if item.get('period') not in ['lunch', 'dinner']]
                # 确保attractions是纯list，然后切片
                attractions_list = list(attractions) if not isinstance(attractions, list) else attractions
                attractions_top3 = attractions_list[:3] if len(attractions_list) >= 3 else attractions_list

                daily_schedule_summary.append({
                    'day': day_num,
                    'attractions_count': len(attractions_list),
                    'attractions': attractions_top3,  # 前3个景点
                    'pace': day_schedule.get('pace', '中等')
                })

            yield f"data: {json.dumps({'type': 'step_result', 'step': '景点排程完成', 'agent': 'AttractionScheduler', 'data': {
                'days': len(scheduled_attractions),
                'daily_schedule': daily_schedule_summary,
                'total_attractions': sum(len(day.get('schedule', [])) for day in scheduled_attractions),
                'llm_description': llm_description
            }, 'progress': 45}, ensure_ascii=False)}\n\n"

            # ========================================
            # 🚀 并行执行：交通、餐饮、住宿智能体同时工作
            # ========================================
            logger.info(f"[分阶段规划] 开始并行执行交通、餐饮、住宿智能体")

            # 发送并行执行开始事件
            yield f"data: {json.dumps({'type': 'progress', 'step': '智能体并行工作中...', 'agent': 'Group C', 'progress': 50}, ensure_ascii=False)}\n\n"

            # 准备并行任务
            from tradingagents.agents.group_c import plan_transport, recommend_dining, recommend_accommodation
            budget_level = user_portrait.get("budget_level", "medium")
            travelers = user_portrait.get("total_travelers", 2)

            # 定义并行任务函数
            async def run_transport_task():
                """交通规划智能体"""
                try:
                    logger.info(f"[并行执行] TransportPlanner 开始工作")
                    result = plan_transport(destination_cn, scheduled_attractions, budget_level, llm)
                    logger.info(f"[并行执行] TransportPlanner 完成")
                    return ('transport', result)
                except Exception as e:
                    logger.error(f"[并行执行] TransportPlanner 失败: {e}")
                    return ('transport', None)

            async def run_dining_task():
                """餐饮推荐智能体"""
                try:
                    logger.info(f"[并行执行] DiningRecommender 开始工作")
                    result = recommend_dining(destination_cn, scheduled_attractions, budget_level, llm)
                    logger.info(f"[并行执行] DiningRecommender 完成")
                    return ('dining', result)
                except Exception as e:
                    logger.error(f"[并行执行] DiningRecommender 失败: {e}")
                    return ('dining', None)

            async def run_accommodation_task():
                """住宿建议智能体"""
                try:
                    logger.info(f"[并行执行] AccommodationAdvisor 开始工作")
                    result = recommend_accommodation(destination_cn, days, budget_level, travelers, llm)
                    logger.info(f"[并行执行] AccommodationAdvisor 完成")
                    return ('accommodation', result)
                except Exception as e:
                    logger.error(f"[并行执行] AccommodationAdvisor 失败: {e}")
                    return ('accommodation', None)

            # 🚀 并行执行3个智能体（使用asyncio.gather）
            results = await asyncio.gather(
                run_transport_task(),
                run_dining_task(),
                run_accommodation_task(),
                return_exceptions=True
            )

            # 解析并行执行结果
            transport_plan = None
            dining_plan = None
            accommodation_plan = None

            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"[并行执行] 任务异常: {result}")
                    continue

                if result:
                    name, data = result
                    if name == 'transport':
                        transport_plan = data
                        # 返回完整的交通规划数据
                        yield f"data: {json.dumps({'type': 'step_result', 'step': '交通规划完成', 'agent': 'TransportPlanner', 'data': transport_plan, 'progress': 65}, ensure_ascii=False)}\n\n"
                    elif name == 'dining':
                        dining_plan = data
                        # 返回完整的餐饮推荐数据
                        yield f"data: {json.dumps({'type': 'step_result', 'step': '餐饮推荐完成', 'agent': 'DiningRecommender', 'data': dining_plan, 'progress': 80}, ensure_ascii=False)}\n\n"
                    elif name == 'accommodation':
                        accommodation_plan = data
                        yield f"data: {json.dumps({'type': 'step_result', 'step': '住宿建议完成', 'agent': 'AccommodationAdvisor', 'data': accommodation_plan, 'progress': 85}, ensure_ascii=False)}\n\n"

            logger.info(f"[分阶段规划] 并行执行完成，3个智能体结果已收集")

            # 步骤6: 格式化攻略
            yield f"data: {json.dumps({'type': 'progress', 'step': '整合完整攻略', 'agent': 'GuideFormatter', 'progress': 98}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.2)

            from tradingagents.agents.group_c import format_detailed_guide
            detailed_guide = format_detailed_guide(
                destination_cn,  # 使用中文名称
                selected_style,
                scheduled_attractions,
                transport_plan,
                dining_plan,
                accommodation_plan,
                request.user_requirements,
                llm
            )

            # 完成
            yield f"data: {json.dumps({'type': 'complete', 'progress': 100, 'message': '详细攻略生成完成！', 'guide': detailed_guide}, ensure_ascii=False)}\n\n"

        except Exception as e:
            logger.error(f"[分阶段规划] 流式生成失败: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ============================================================
# PDF导出功能
# ============================================================

class ExportPDFRequest(BaseModel):
    """导出PDF请求"""
    guide_data: Dict[str, Any]
    filename: Optional[str] = None


@router.post("/export-pdf")
async def export_guide_pdf(request: ExportPDFRequest):
    """
    导出攻略为PDF文件

    将详细攻略转换为PDF格式，支持中文显示和完整排版
    """
    try:
        logger.info(f"[PDF导出] 开始导出攻略PDF")

        # 导入PDF生成服务
        from app.services.travel_pdf_service import get_pdf_service
        from app.utils.pdf_generator import get_pdf_generator

        # 检查依赖
        pdf_service = get_pdf_service()
        requirements = pdf_service.check_pdf_requirements()

        # 检查是否有可用的PDF生成库
        has_pdf_lib = requirements.get("reportlab", False)

        if not has_pdf_lib:
            raise HTTPException(
                status_code=500,
                detail="PDF生成库未安装，请安装 reportlab 或 weasyprint"
            )

        # 准备攻略数据
        guide_data = request.guide_data

        # 添加标题（如果没有）
        if "title" not in guide_data:
            destination = guide_data.get("destination", "未知目的地")
            days = guide_data.get("days", guide_data.get("total_days", 0))
            guide_data["title"] = f"{destination}{days}日深度游攻略"

        # 生成文件名
        if request.filename:
            filename = request.filename
        else:
            destination = guide_data.get("destination", "unknown")
            safe_destination = pdf_service._sanitize_filename(destination)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{safe_destination}_攻略_{timestamp}.pdf"

        # 确保文件名以.pdf结尾
        if not filename.endswith('.pdf'):
            filename += '.pdf'

        # 生成PDF文件路径
        output_path = os.path.join(pdf_service.output_dir, filename)

        # 生成PDF
        pdf_path = pdf_service.generate_guide_pdf(
            guide_data=guide_data,
            output_path=output_path
        )

        logger.info(f"[PDF导出] PDF生成成功: {pdf_path}")

        # 返回文件
        return FileResponse(
            path=pdf_path,
            filename=filename,
            media_type='application/pdf',
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except FileNotFoundError as e:
        logger.error(f"[PDF导出] 文件未找到: {e}")
        raise HTTPException(status_code=404, detail="PDF文件未找到")
    except PermissionError as e:
        logger.error(f"[PDF导出] 权限错误: {e}")
        raise HTTPException(status_code=403, detail="没有写入权限")
    except Exception as e:
        logger.error(f"[PDF导出] 导出失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF导出失败: {str(e)}")


@router.get("/pdf-check")
async def check_pdf_support():
    """
    检查PDF生成支持的依赖

    返回系统PDF生成能力的状态
    """
    try:
        from app.services.travel_pdf_service import get_pdf_service

        pdf_service = get_pdf_service()
        requirements = pdf_service.check_pdf_requirements()

        return {
            "success": True,
            "pdf_support": {
                "reportlab": requirements.get("reportlab", False),
                "weasyprint": requirements.get("weasyprint", False),
                "chinese_font": requirements.get("chinese_font", False)
            },
            "status": "ready" if requirements.get("reportlab") else "not_ready",
            "message": "PDF生成功能就绪" if requirements.get("reportlab") else "需要安装PDF生成库"
        }

    except Exception as e:
        logger.error(f"[PDF检查] 检查失败: {e}")
        return {
            "success": False,
            "pdf_support": {
                "reportlab": False,
                "weasyprint": False,
                "chinese_font": False
            },
            "status": "error",
            "message": str(e)
        }
