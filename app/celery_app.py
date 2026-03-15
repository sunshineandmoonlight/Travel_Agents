"""
Celery异步任务队列应用配置

用于处理长时间运行的任务，如旅行攻略生成。
支持:
- 异步任务执行
- 任务状态追踪
- 任务结果存储
- 自动重试
"""

import os
import logging
from celery import Celery

logger = logging.getLogger(__name__)

# Redis配置
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = os.getenv("REDIS_PORT", "6379")
redis_password = os.getenv("REDIS_PASSWORD", "")
redis_db = os.getenv("REDIS_CELERY_DB", "2")  # 使用DB2，DB0给session，DB1给缓存

# 构建Redis URL
if redis_password:
    redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"
else:
    redis_url = f"redis://{redis_host}:{redis_port}/{redis_db}"

# 创建Celery应用
celery_app = Celery(
    "travelagents",
    broker=redis_url,
    backend=redis_url,
    include=[
        'app.tasks.travel_tasks',
        'app.tasks.guide_tasks',
    ]
)

# Celery配置
celery_app.conf.update(
    # 序列化配置
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    result_extended=True,

    # 时区配置
    timezone='Asia/Shanghai',
    enable_utc=True,

    # 任务配置
    task_track_started=True,
    task_time_limit=30 * 60,      # 硬超时：30分钟
    task_soft_time_limit=25 * 60,  # 软超时：25分钟
    task_acks_late=True,           # 任务执行后确认
    worker_prefetch_multiplier=1,  # 每次只预取一个任务

    # 结果配置
    result_expires=3600,           # 结果保留1小时
    result_backend_transport_options={
        'retry_policy': {
            'timeout': 5.0
        }
    },

    # 重试配置
    task_autoretry_for=(Exception,),  # 所有异常自动重试
    task_retry_kwargs={'max_retries': 3},
    task_retry_delay=60,               # 重试延迟60秒

    # Worker配置
    worker_max_tasks_per_child=100,  # Worker处理100个任务后重启
    worker_send_task_events=True,    # 发送任务事件

    # 路由配置（可选）
    task_routes={
        'app.tasks.travel_tasks.*': {'queue': 'travel'},
        'app.tasks.guide_tasks.*': {'queue': 'guide'},
    },

    # 任务优先级
    task_default_queue='default',
    task_default_priority=5,
)

# 日志配置
celery_app.conf.worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
celery_app.conf.worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'


def get_celery_status() -> dict:
    """
    获取Celery连接状态

    Returns:
        状态信息字典
    """
    status = {
        "configured": True,
        "broker_url": redis_url.replace(redis_password, "****") if redis_password else redis_url,
        "backend_url": redis_url.replace(redis_password, "****") if redis_password else redis_url,
        "connected": False,
        "message": ""
    }

    try:
        # 测试broker连接
        from kombu import Connection
        with Connection(celery_app.conf.broker_url) as conn:
            conn.connect()
            status["connected"] = True
            status["message"] = f"Celery已连接: {redis_host}:{redis_port}/DB{redis_db}"
            logger.info(f"✅ Celery连接成功: {redis_host}:{redis_port}/DB{redis_db}")
    except Exception as e:
        status["connected"] = False
        status["message"] = f"Celery连接失败: {e}"
        logger.warning(f"⚠️ Celery连接失败: {e}")

    return status


__all__ = [
    "celery_app",
    "get_celery_status",
]
