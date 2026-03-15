"""
旅行规划异步任务

处理耗时的旅行规划操作，如：
- 目的地推荐
- 风格方案生成
- 详细攻略生成
"""

import logging
from typing import Dict, Any
from datetime import datetime

from app.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.travel_tasks.generate_destinations")
def generate_destinations_task(self, requirement_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    异步生成目的地推荐

    Args:
        requirement_data: 用户需求数据

    Returns:
        目的地推荐结果
    """
    task_id = self.request.id
    logger.info(f"[任务 {task_id}] 开始生成目的地推荐")

    try:
        # 更新任务状态
        self.update_state(state='PROGRESS', meta={
            'stage': 'analyzing',
            'message': '正在分析需求...',
            'progress': 10
        })

        # 导入并执行
        from tradingagents.agents.group_a.user_requirement_analyst import analyze_user_requirements
        from tradingagents.agents.group_a.destination_matcher import match_destinations
        from tradingagents.agents.group_a.ranking_scorer import score_and_rank_destinations

        # 分析需求
        user_portrait = analyze_user_requirements(requirement_data)
        self.update_state(state='PROGRESS', meta={
            'stage': 'matching',
            'message': '正在匹配目的地...',
            'progress': 30
        })

        # 匹配目的地
        matched_destinations = match_destinations(user_portrait)
        self.update_state(state='PROGRESS', meta={
            'stage': 'ranking',
            'message': '正在排序推荐...',
            'progress': 60
        })

        # 排序
        final_destinations = score_and_rank_destinations(matched_destinations, user_portrait)

        result = {
            'status': 'success',
            'destinations': final_destinations[:4],  # TOP 4
            'user_portrait': user_portrait,
            'task_id': task_id,
            'completed_at': datetime.now().isoformat()
        }

        logger.info(f"[任务 {task_id}] 目的地推荐生成完成")
        return result

    except Exception as e:
        logger.error(f"[任务 {task_id}] 生成失败: {e}")
        self.update_state(state='FAILURE', meta={
            'error': str(e),
            'stage': 'error'
        })
        raise


@celery_app.task(bind=True, name="app.tasks.travel_tasks.generate_style_proposals")
def generate_styles_task(self, destination: str, destination_data: Dict,
                        user_portrait: Dict, days: int) -> Dict[str, Any]:
    """
    异步生成风格方案

    Args:
        destination: 选中的目的地
        destination_data: 目的地数据
        user_portrait: 用户画像
        days: 天数

    Returns:
        风格方案结果
    """
    task_id = self.request.id
    logger.info(f"[任务 {task_id}] 开始生成风格方案: {destination}")

    try:
        self.update_state(state='PROGRESS', meta={
            'stage': 'designing',
            'message': '正在设计方案...',
            'progress': 20
        })

        from tradingagents.agents.group_b.immersive_designer import create_immersive_proposal
        from tradingagents.agents.group_b.exploration_designer import create_exploration_proposal
        from tradingagents.agents.group_b.relaxation_designer import create_relaxation_proposal
        from tradingagents.agents.group_b.hidden_gem_designer import create_hidden_gem_proposal

        # 生成4种风格方案
        self.update_state(state='PROGRESS', meta={
            'stage': 'immersive',
            'message': '正在生成沉浸式方案...',
            'progress': 30
        })
        immersive = create_immersive_proposal(destination, destination_data, user_portrait, days)

        self.update_state(state='PROGRESS', meta={
            'stage': 'exploration',
            'message': '正在生成探索式方案...',
            'progress': 50
        })
        exploration = create_exploration_proposal(destination, destination_data, user_portrait, days)

        self.update_state(state='PROGRESS', meta={
            'stage': 'relaxation',
            'message': '正在生成松弛式方案...',
            'progress': 70
        })
        relaxation = create_relaxation_proposal(destination, destination_data, user_portrait, days)

        self.update_state(state='PROGRESS', meta={
            'stage': 'hidden_gem',
            'message': '正在生成小众宝藏方案...',
            'progress': 90
        })
        hidden_gem = create_hidden_gem_proposal(destination, destination_data, user_portrait, days)

        result = {
            'status': 'success',
            'styles': [immersive, exploration, relaxation, hidden_gem],
            'destination': destination,
            'task_id': task_id,
            'completed_at': datetime.now().isoformat()
        }

        logger.info(f"[任务 {task_id}] 风格方案生成完成")
        return result

    except Exception as e:
        logger.error(f"[任务 {task_id}] 生成失败: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise


@celery_app.task(bind=True, name="app.tasks.travel_tasks.generate_full_guide")
def generate_full_guide_task(self, destination: str, days: int,
                            user_portrait: Dict, style_type: str) -> Dict[str, Any]:
    """
    异步生成完整攻略

    Args:
        destination: 目的地
        days: 天数
        user_portrait: 用户画像
        style_type: 风格类型

    Returns:
        完整攻略结果
    """
    task_id = self.request.id
    logger.info(f"[任务 {task_id}] 开始生成完整攻略: {destination} {days}天 {style_type}")

    try:
        from tradingagents.agents.group_c.attraction_scheduler import schedule_attractions
        from tradingagents.agents.group_c.dining_recommender import recommend_dining
        from tradingagents.agents.group_c.transport_planner import plan_transport
        from tradingagents.agents.group_c.accommodation_advisor import recommend_accommodation
        from tradingagents.agents.group_c.guide_formatter import format_detailed_guide

        # 1. 景点排程
        self.update_state(state='PROGRESS', meta={
            'stage': 'attractions',
            'message': '正在排程景点...',
            'progress': 20
        })
        attractions = schedule_attractions(destination, days, user_portrait, style_type)

        # 2. 餐饮推荐
        self.update_state(state='PROGRESS', meta={
            'stage': 'dining',
            'message': '正在推荐餐饮...',
            'progress': 40
        })
        dining = recommend_dining(destination, days, user_portrait)

        # 3. 交通规划
        self.update_state(state='PROGRESS', meta={
            'stage': 'transport',
            'message': '正在规划交通...',
            'progress': 60
        })
        transport = plan_transport(destination, days, attractions)

        # 4. 住宿推荐
        self.update_state(state='PROGRESS', meta={
            'stage': 'accommodation',
            'message': '正在推荐住宿...',
            'progress': 80
        })
        accommodation = recommend_accommodation(destination, days, user_portrait)

        # 5. 格式化攻略
        self.update_state(state='PROGRESS', meta={
            'stage': 'formatting',
            'message': '正在生成攻略...',
            'progress': 95
        })
        guide = format_detailed_guide(
            destination, days, user_portrait, style_type,
            attractions, dining, transport, accommodation
        )

        result = {
            'status': 'success',
            'guide': guide,
            'task_id': task_id,
            'completed_at': datetime.now().isoformat()
        }

        logger.info(f"[任务 {task_id}] 完整攻略生成完成")
        return result

    except Exception as e:
        logger.error(f"[任务 {task_id}] 生成失败: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise


__all__ = [
    "generate_destinations_task",
    "generate_styles_task",
    "generate_full_guide_task",
]
