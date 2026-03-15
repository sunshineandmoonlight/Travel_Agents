"""
攻略生成异步任务

完整流程：需求分析 → 目的地推荐 → 风格方案 → 详细攻略
"""

import logging
from typing import Dict, Any
from datetime import datetime

from app.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.guide_tasks.generate_complete_travel_guide")
def generate_complete_guide_task(self, requirement_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    异步生成完整旅行攻略（端到端）

    包含所有阶段：
    1. 需求分析
    2. 目的地推荐
    3. 风格方案
    4. 详细攻略

    Args:
        requirement_data: 用户需求数据

    Returns:
        完整攻略结果
    """
    task_id = self.request.id
    logger.info(f"[任务 {task_id}] 开始生成完整旅行攻略")

    try:
        # ========== 阶段1: 需求分析 ==========
        self.update_state(state='PROGRESS', meta={
            'stage': 'requirement_analysis',
            'message': '正在分析旅行需求...',
            'progress': 5,
            'phase': 1
        })

        from tradingagents.agents.group_a.user_requirement_analyst import analyze_user_requirements
        user_portrait = analyze_user_requirements(requirement_data)

        # ========== 阶段2: 目的地推荐 ==========
        self.update_state(state='PROGRESS', meta={
            'stage': 'destination_matching',
            'message': '正在匹配目的地...',
            'progress': 15,
            'phase': 2
        })

        from tradingagents.agents.group_a.destination_matcher import match_destinations
        matched_destinations = match_destinations(user_portrait)

        from tradingagents.agents.group_a.ranking_scorer import score_and_rank_destinations
        final_destinations = score_and_rank_destinations(matched_destinations, user_portrait)

        # 默认选择第一个目的地
        selected_destination = final_destinations[0]['name']
        selected_dest_data = final_destinations[0]
        days = requirement_data.get('days', 3)

        # ========== 阶段3: 风格方案 ==========
        self.update_state(state='PROGRESS', meta={
            'stage': 'style_design',
            'message': '正在设计旅行方案...',
            'progress': 35,
            'phase': 3
        })

        from tradingagents.agents.group_b.immersive_designer import design_immersive_style
        from tradingagents.agents.group_b.exploration_designer import design_exploration_style
        from tradingagents.agents.group_b.relaxation_designer import design_relaxation_style
        from tradingagents.agents.group_b.hidden_gem_designer import design_hidden_gem_style

        # 获取LLM（如果有）
        llm = None
        try:
            from tradingagents.llm_adapters import create_llm_by_provider
            from app.core.config import settings
            llm = create_llm_by_provider(settings.LLM_PROVIDER, settings.QUICK_THINK_LLM)
        except:
            pass

        # 并发生成4种风格（简化）
        immersive = design_immersive_style(selected_destination, selected_dest_data, user_portrait, days, llm)
        exploration = design_exploration_style(selected_destination, selected_dest_data, user_portrait, days, llm)
        relaxation = design_relaxation_style(selected_destination, selected_dest_data, user_portrait, days, llm)
        hidden_gem = design_hidden_gem_style(selected_destination, selected_dest_data, user_portrait, days, llm)

        # 默认选择第一种风格
        selected_style = immersive['style_type']

        # ========== 阶段4: 详细攻略 ==========
        self.update_state(state='PROGRESS', meta={
            'stage': 'detailed_planning',
            'message': '正在规划详细行程...',
            'progress': 60,
            'phase': 4
        })

        from tradingagents.agents.group_c.attraction_scheduler import schedule_attractions
        from tradingagents.agents.group_c.dining_recommender import recommend_dining
        from tradingagents.agents.group_c.transport_planner import plan_transport
        from tradingagents.agents.group_c.accommodation_advisor import recommend_accommodation
        from tradingagents.agents.group_c.guide_formatter import format_detailed_guide

        attractions = schedule_attractions(selected_destination, days, user_portrait, selected_style)

        self.update_state(state='PROGRESS', meta={
            'stage': 'detailed_planning',
            'message': '正在推荐餐饮...',
            'progress': 70,
            'phase': 4
        })

        dining = recommend_dining(selected_destination, days, user_portrait)

        self.update_state(state='PROGRESS', meta={
            'stage': 'detailed_planning',
            'message': '正在规划交通...',
            'progress': 80,
            'phase': 4
        })

        transport = plan_transport(selected_destination, days, attractions)

        self.update_state(state='PROGRESS', meta={
            'stage': 'detailed_planning',
            'message': '正在推荐住宿...',
            'progress': 90,
            'phase': 4
        })

        accommodation = recommend_accommodation(selected_destination, days, user_portrait)

        # 格式化最终攻略
        self.update_state(state='PROGRESS', meta={
            'stage': 'formatting',
            'message': '正在生成攻略文档...',
            'progress': 95,
            'phase': 4
        })

        guide = format_detailed_guide(
            selected_destination, days, user_portrait, selected_style,
            attractions, dining, transport, accommodation
        )

        # 完成
        result = {
            'status': 'success',
            'user_portrait': user_portrait,
            'destinations': final_destinations[:4],
            'selected_destination': selected_destination,
            'styles': [immersive, exploration, relaxation, hidden_gem],
            'selected_style': selected_style,
            'guide': guide,
            'task_id': task_id,
            'completed_at': datetime.now().isoformat()
        }

        logger.info(f"[任务 {task_id}] 完整攻略生成成功")
        return result

    except Exception as e:
        logger.error(f"[任务 {task_id}] 生成失败: {e}", exc_info=True)
        self.update_state(state='FAILURE', meta={
            'error': str(e),
            'stage': 'error'
        })
        raise


__all__ = [
    "generate_complete_guide_task",
]
