"""
TravelAgents-CN v1.0.0 Travel-Only FastAPI Backend
旅游专用后端入口 - 移除所有股票相关功能

Copyright (c) 2025 hsliuping. All rights reserved.
"""

# 加载环境变量
from dotenv import load_dotenv
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file = os.path.join(project_root, '.env')

if os.path.exists(env_file):
    load_dotenv(env_file, override=True)
else:
    print(f"[WARNING] .env file not found at: {env_file}")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import time
from datetime import datetime
from contextlib import asynccontextmanager
from pathlib import Path

# 核心配置（保持不变）
from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.logging_config import setup_logging

# 仅导入旅游相关路由
from app.routers import health
from app.routers import staged_planning as travel_staged_router
from app.routers import travel as travel_router
from app.routers import travel_plans as travel_plans_router
from app.routers import travel_images as travel_images_router
from app.routers import travel_guides as travel_guides_router
from app.routers import travel_cache as travel_cache_router
from app.routers import travel_intelligence as travel_intelligence_router
from app.routers import travel_messages as travel_messages_router
from app.routers import travel_notifications as travel_notifications_router
from app.routers import travel_operation_logs as travel_operation_logs_router
from app.routers import travel_queue as travel_queue_router
from app.routers import travel_reports as travel_reports_router
from app.routers import travel_tags as travel_tags_router
from app.routers import travel_tianapi as travel_tianapi_router

# 通用路由（认证、配置等）
from app.routers import config as config_router

logger = logging.getLogger(__name__)


def get_version() -> str:
    """从 VERSION 文件读取版本号"""
    try:
        version_file = Path(__file__).parent.parent / "VERSION"
        if version_file.exists():
            return version_file.read_text(encoding='utf-8').strip()
    except Exception:
        pass
    return "1.0.0-travel"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """旅游应用生命周期管理 - 简化版，仅初始化必要服务"""
    logger = logging.getLogger("app.travel")

    # 验证启动配置
    try:
        from app.core.startup_validator import validate_startup_config
        validate_startup_config()
    except Exception as e:
        logger.warning(f"配置验证失败（已跳过）: {e}")

    # 初始化数据库
    await init_db()

    # 初始化缓存系统（Redis/内存自动选择）
    try:
        from tradingagents.utils.cache_init import init_cache_system
        cache_status = init_cache_system()
        logger.info(f"缓存系统: {cache_status['message']}")
    except Exception as e:
        logger.warning(f"缓存系统初始化失败（已跳过）: {e}")

    # 初始化热门目的地图片缓存
    try:
        from tradingagents.services.destination_image_cache import (
            initialize_popular_destinations_cache,
            schedule_cache_refresh
        )
        logger.info("正在初始化热门目的地图片缓存...")
        cache_result = await initialize_popular_destinations_cache()
        logger.info(
            f"热门目的地缓存初始化完成: "
            f"成功{cache_result['success']}, 失败{cache_result['failed']}"
        )

        # 启动定期刷新任务
        schedule_cache_refresh()
        logger.info("热门目的地缓存定期刷新任务已启动")
    except Exception as e:
        logger.warning(f"热门目的地缓存初始化失败（已跳过）: {e}")

    # 配置桥接（用于TradingAgents核心库）
    try:
        from app.core.config_bridge import bridge_config_to_env
        bridge_config_to_env()
    except Exception as e:
        logger.warning(f"配置桥接失败（已跳过）: {e}")

    # 显示配置摘要
    logger.info("=" * 70)
    logger.info("TravelAgents-CN Travel-Only Backend")
    logger.info("=" * 70)
    logger.info(f"Version: {get_version()}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info("=" * 70)

    logger.info("✅ TravelAgents FastAPI backend started (Travel Mode)")

    yield

    # 关闭时清理
    await close_db()
    logger.info("TravelAgents backend stopped")


# 创建FastAPI应用
app = FastAPI(
    title="TravelAgents-CN API",
    description="智能旅游规划系统 API - 旅游专用版本",
    version=get_version(),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# ============================================================
# 中间件配置
# ============================================================

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # 从环境变量读取允许的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全中间件
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )


# ============================================================
# 请求处理中间件
# ============================================================

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """添加请求处理时间"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    # 记录请求
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")

    return response


# ============================================================
# 全局异常处理
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# ============================================================
# 路由注册 - 仅旅游相关
# ============================================================

# 健康检查
app.include_router(health.router, prefix="/api", tags=["Health"])

# 旅游核心API
app.include_router(travel_staged_router.router, prefix="/api/travel/staged", tags=["Travel-Staged"])
app.include_router(travel_router.router, prefix="/api/travel", tags=["Travel"])
app.include_router(travel_plans_router.router, prefix="/api/travel/plans", tags=["Travel-Plans"])
app.include_router(travel_images_router.router, prefix="/api/travel/images", tags=["Travel-Images"])
app.include_router(travel_guides_router.router, prefix="/api", tags=["Travel-Guides"])

# 旅游扩展API
app.include_router(travel_cache_router.router, prefix="/api/travel/cache", tags=["Travel-Cache"])
app.include_router(travel_intelligence_router.router, prefix="/api/travel/intelligence", tags=["Travel-Intelligence"])
app.include_router(travel_messages_router.router, prefix="/api/travel/messages", tags=["Travel-Messages"])
app.include_router(travel_notifications_router.router, prefix="/api/travel/notifications", tags=["Travel-Notifications"])
app.include_router(travel_operation_logs_router.router, prefix="/api/travel/operation-logs", tags=["Travel-Operation-Logs"])
app.include_router(travel_queue_router.router, prefix="/api/travel/queue", tags=["Travel-Queue"])
app.include_router(travel_reports_router.router, prefix="/api/travel/reports", tags=["Travel-Reports"])
app.include_router(travel_tags_router.router, prefix="/api/travel/tags", tags=["Travel-Tags"])

# 天行数据API
app.include_router(travel_tianapi_router.router)

# 通用API
app.include_router(config_router.router, prefix="/api/config", tags=["Config"])


# ============================================================
# 根路径
# ============================================================

@app.get("/")
async def root():
    """根路径 - API信息"""
    return {
        "name": "TravelAgents-CN API",
        "version": get_version(),
        "mode": "travel-only",
        "description": "智能旅游规划系统 API",
        "docs_url": "/docs",
        "health": "/health"
    }


# ============================================================
# 主程序入口
# ============================================================

if __name__ == "__main__":
    uvicorn.run(
        "app.travel_main:app",
        host=settings.HOST if hasattr(settings, 'HOST') else "127.0.0.1",
        port=settings.PORT if hasattr(settings, 'PORT') else 8005,
        reload=settings.DEBUG,
        reload_dirs=["app"],  # 只监控app目录，避免频繁重载
        workers=1,  # 限制worker数量，避免多进程问题
        log_level="info",
        # 改进重载机制
        use_colors=False,
        loop="asyncio"
    )
