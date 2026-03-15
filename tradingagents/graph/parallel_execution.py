"""
并行执行优化模块

提供智能体并行执行的能力，显著提升性能
"""

import asyncio
from typing import Dict, Any, List, Callable, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger('travel_agents')

# ============================================================
# 导入智能体函数
# ============================================================

# Group B 设计函数
try:
    from tradingagents.agents.group_b import (
        design_immersive_style,
        design_exploration_style,
        design_relaxation_style,
        design_hidden_gem_style,
        generate_style_proposals_parallel  # 已有的并行实现
    )
    GROUP_B_AVAILABLE = True
except ImportError as e:
    logger.warning(f"[并行执行] Group B 智能体导入失败: {e}")
    GROUP_B_AVAILABLE = False

# Group C 函数
try:
    from tradingagents.agents.group_c.attraction_scheduler import schedule_attractions
    from tradingagents.agents.group_c.accommodation_advisor import recommend_accommodation
    from tradingagents.agents.group_c.transport_planner import plan_transport
    from tradingagents.agents.group_c.dining_recommender import recommend_dining
    GROUP_C_AVAILABLE = True
except ImportError as e:
    logger.warning(f"[并行执行] Group C 智能体导入失败: {e}")
    GROUP_C_AVAILABLE = False


# ============================================================
# 并行执行工具函数
# ============================================================

async def run_async(coro):
    """同步环境中运行异步函数"""
    return await coro


def execute_parallel(tasks: List[Callable]) -> List[Any]:
    """
    并行执行多个同步任务

    Args:
        tasks: 任务函数列表

    Returns:
        执行结果列表
    """
    try:
        # 尝试使用线程池并行执行
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = []
        with ThreadPoolExecutor(max_workers=min(len(tasks), 4)) as executor:
            future_to_task = {executor.submit(task): task for task in tasks}

            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"[并行执行] 任务失败: {e}")
                    results.append(None)

        return results

    except Exception as e:
        logger.warning(f"[并行执行] 线程池失败，回退到顺序执行: {e}")
        # 回退到顺序执行
        return [task() for task in tasks]


def execute_parallel_async(coros: List) -> List[Any]:
    """
    并行执行多个异步协程

    Args:
        coros: 协程列表

    Returns:
        执行结果列表
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果事件循环正在运行，创建新任务
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, asyncio.gather(*coros))
                return future.result()
        else:
            return asyncio.run(asyncio.gather(*coros))
    except Exception as e:
        logger.warning(f"[并行执行] 异步执行失败: {e}")
        # 回退：逐个执行
        results = []
        for coro in coros:
            try:
                results.append(asyncio.run(coro))
            except Exception as e:
                logger.error(f"[并行执行] 协程执行失败: {e}")
                results.append(None)
        return results


# ============================================================
# Group B: 风格设计并行执行
# ============================================================

class ParallelStyleDesigners:
    """并行执行4个风格设计师"""

    def __init__(self, llm):
        self.llm = llm

    def create_all_proposals(
        self,
        destination: str,
        dest_data: Dict[str, Any],
        user_portrait: Dict[str, Any],
        days: int
    ) -> List[Dict[str, Any]]:
        """
        并行生成4种风格方案

        优先使用已有的异步并行实现，失败时回退到线程池并行

        Returns:
            [沉浸式, 探索式, 松弛式, 小众式] 的方案列表
        """
        logger.info(f"[并行B] 开始并行生成4种风格方案: {destination}")

        try:
            # 尝试使用已有的异步并行实现
            import asyncio
            try:
                # 检查是否有事件循环在运行
                loop = asyncio.get_running_loop()
                # 如果有事件循环在运行，使用线程池运行异步函数
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        generate_style_proposals_parallel(
                            destination, dest_data, user_portrait, days, self.llm
                        )
                    )
                    proposals = future.result()
                logger.info(f"[并行B] ✅ 异步并行完成: {len(proposals)}个方案")
                return proposals
            except RuntimeError:
                # 没有运行的事件循环，直接运行
                proposals = asyncio.run(
                    generate_style_proposals_parallel(
                        destination, dest_data, user_portrait, days, self.llm
                    )
                )
                logger.info(f"[并行B] ✅ 异步并行完成: {len(proposals)}个方案")
                return proposals
        except Exception as e:
            logger.warning(f"[并行B] 异步并行失败，使用线程池: {e}")

        # 降级：使用线程池并行执行
        return self._thread_pool_parallel(destination, dest_data, user_portrait, days)

    def _thread_pool_parallel(
        self,
        destination: str,
        dest_data: Dict[str, Any],
        user_portrait: Dict[str, Any],
        days: int
    ) -> List[Dict[str, Any]]:
        """使用线程池并行执行"""
        if not GROUP_B_AVAILABLE:
            logger.error("[并行B] Group B 智能体不可用")
            return []

        # 定义4个设计师任务
        def create_immersive_proposal():
            try:
                return design_immersive_style(destination, dest_data, user_portrait, days, self.llm)
            except Exception as e:
                logger.error(f"[并行B] 沉浸式方案生成失败: {e}")
                return None

        def create_exploration_proposal():
            try:
                return design_exploration_style(destination, dest_data, user_portrait, days, self.llm)
            except Exception as e:
                logger.error(f"[并行B] 探索式方案生成失败: {e}")
                return None

        def create_relaxation_proposal():
            try:
                return design_relaxation_style(destination, dest_data, user_portrait, days, self.llm)
            except Exception as e:
                logger.error(f"[并行B] 松弛式方案生成失败: {e}")
                return None

        def create_hidden_gem_proposal():
            try:
                return design_hidden_gem_style(destination, dest_data, user_portrait, days, self.llm)
            except Exception as e:
                logger.error(f"[并行B] 小众式方案生成失败: {e}")
                return None

        # 并行执行4个任务
        tasks = [
            create_immersive_proposal,
            create_exploration_proposal,
            create_relaxation_proposal,
            create_hidden_gem_proposal
        ]

        proposals = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_task = {executor.submit(task): task for task in tasks}
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    if result:
                        proposals.append(result)
                except Exception as e:
                    logger.error(f"[并行B] 任务执行失败: {e}")

        logger.info(f"[并行B] 完成! 生成 {len(proposals)}/4 个风格方案")
        return proposals


# ============================================================
# Group C: 详细攻略并行执行
# ============================================================

class ParallelGroupC:
    """
    Group C 智能体的并行执行

    执行策略:
    - 第一阶段: C1(景点) + C4(住宿) 并行
    - 第二阶段: C2(交通) + C3(餐饮) 并行 (依赖C1)
    - 第三阶段: C5(攻略) 顺序执行 (依赖前面所有)
    """

    def __init__(self, llm):
        self.llm = llm

    def execute_stage1_parallel(
        self,
        destination: str,
        dest_data: Dict[str, Any],
        style_proposal: Dict[str, Any],
        days: int,
        start_date: str,
        user_portrait: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        第一阶段并行执行: C1(景点) + C4(住宿)

        Returns:
            (scheduled_attractions, accommodation_plan)
        """
        if not GROUP_C_AVAILABLE:
            logger.error("[并行C-阶段1] Group C 智能体不可用")
            return None, None

        budget_level = user_portrait.get("budget_level", "medium")
        travelers = user_portrait.get("total_travelers", 2)

        logger.info(f"[并行C-阶段1] C1(景点) + C4(住宿) 并行执行...")

        # C1: 景点排程任务
        def schedule_attractions_task():
            try:
                return schedule_attractions(
                    destination, dest_data, style_proposal, days, start_date, self.llm
                )
            except Exception as e:
                logger.error(f"[并行C-阶段1] C1失败: {e}")
                return None

        # C4: 住宿推荐任务
        def recommend_accommodation_task():
            try:
                return recommend_accommodation(
                    destination, days, budget_level, travelers, self.llm
                )
            except Exception as e:
                logger.error(f"[并行C-阶段1] C4失败: {e}")
                return None

        # 并行执行
        results = []
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_to_task = {
                executor.submit(schedule_attractions_task): "C1",
                executor.submit(recommend_accommodation_task): "C4"
            }
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"[并行C-阶段1] 任务失败: {e}")
                    results.append(None)

        scheduled_attractions = results[0]
        accommodation_plan = results[1]

        logger.info(f"[并行C-阶段1] 完成! C1={'✅' if scheduled_attractions else '❌'}, C4={'✅' if accommodation_plan else '❌'}")

        return scheduled_attractions, accommodation_plan

    def execute_stage2_parallel(
        self,
        destination: str,
        scheduled_attractions: List[Dict[str, Any]],
        budget_level: str
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        第二阶段并行执行: C2(交通) + C3(餐饮)

        Args:
            destination: 目的地
            scheduled_attractions: C1的结果
            budget_level: 预算等级

        Returns:
            (transport_plan, dining_plan)
        """
        if not GROUP_C_AVAILABLE:
            logger.error("[并行C-阶段2] Group C 智能体不可用")
            return None, None

        logger.info(f"[并行C-阶段2] C2(交通) + C3(餐饮) 并行执行...")

        # C2: 交通规划任务
        def plan_transport_task():
            try:
                return plan_transport(destination, scheduled_attractions, budget_level, self.llm)
            except Exception as e:
                logger.error(f"[并行C-阶段2] C2失败: {e}")
                return None

        # C3: 餐饮推荐任务
        def recommend_dining_task():
            try:
                return recommend_dining(destination, scheduled_attractions, budget_level, self.llm)
            except Exception as e:
                logger.error(f"[并行C-阶段2] C3失败: {e}")
                return None

        # 并行执行
        results = []
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_to_task = {
                executor.submit(plan_transport_task): "C2",
                executor.submit(recommend_dining_task): "C3"
            }
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"[并行C-阶段2] 任务失败: {e}")
                    results.append(None)

        transport_plan = results[0]
        dining_plan = results[1]

        logger.info(f"[并行C-阶段2] 完成! C2={'✅' if transport_plan else '❌'}, C3={'✅' if dining_plan else '❌'}")

        return transport_plan, dining_plan

    def execute_all(
        self,
        destination: str,
        dest_data: Dict[str, Any],
        style_proposal: Dict[str, Any],
        days: int,
        start_date: str,
        user_portrait: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        完整执行Group C的所有智能体（优化并行）

        Returns:
            包含所有C组结果的字典
        """
        budget_level = user_portrait.get("budget_level", "medium")
        travelers = user_portrait.get("total_travelers", 2)

        # 阶段1: C1 + C4 并行
        scheduled_attractions, accommodation_plan = self.execute_stage1_parallel(
            destination, dest_data, style_proposal, days, start_date, user_portrait
        )

        if not scheduled_attractions:
            logger.error("[并行C] C1失败，无法继续")
            return {"error": "景点排程失败"}

        # 阶段2: C2 + C3 并行
        transport_plan, dining_plan = self.execute_stage2_parallel(
            destination, scheduled_attractions, budget_level
        )

        # 阶段3: C5 攻略生成（顺序执行）
        logger.info(f"[并行C-阶段3] C5(攻略) 执行...")
        from tradingagents.agents.group_c import LLMGuideWriterAgent

        try:
            guide_writer = LLMGuideWriterAgent(llm=self.llm)
            guide_writer.initialize()

            user_requirements = {
                "user_portrait": user_portrait,
                "start_date": start_date
            }

            guide_content = guide_writer.write_guide(
                destination, style_proposal, scheduled_attractions,
                transport_plan if transport_plan else {},
                dining_plan if dining_plan else {},
                accommodation_plan if accommodation_plan else {},
                user_requirements
            )
            guide_writer.shutdown()
        except Exception as e:
            logger.error(f"[并行C-阶段3] C5失败: {e}")
            guide_content = None

        logger.info(f"[并行C] 全部完成!")

        return {
            "scheduled_attractions": scheduled_attractions,
            "accommodation_plan": accommodation_plan,
            "transport_plan": transport_plan,
            "dining_plan": dining_plan,
            "guide_content": guide_content
        }


# ============================================================
# 优化后的图节点
# ============================================================

def parallel_style_designer_node(state: Dict) -> Dict:
    """
    组B智能体节点：并行生成4种风格方案
    """
    from langchain_core.messages import AIMessage

    llm = state.get("_llm")
    selected_destination = state.get("selected_destination")
    user_portrait = state.get("user_portrait", {})
    requirements = state.get("user_requirements", {})
    days = requirements.get("days", 5)

    dest_data = {
        "tags": user_portrait.get("primary_interests", []),
        "highlights": [],
        "budget_level": {"medium": 500}
    }

    # 并行生成4种方案
    parallel_designers = ParallelStyleDesigners(llm)
    proposals = parallel_designers.create_all_proposals(
        selected_destination, dest_data, user_portrait, days
    )

    messages = state.get("messages", [])
    styles_str = ", ".join([p.get("style_name", "") for p in proposals])
    messages.append(AIMessage(
        content=f"风格方案设计完成(并行): {styles_str}",
        name="ParallelStyleDesigner"
    ))

    return {
        **state,
        "style_proposals": proposals,
        "current_stage": "style_design_completed",
        "messages": messages
    }


def parallel_guide_generator_node(state: Dict) -> Dict:
    """
    组C智能体节点：并行生成详细攻略
    """
    from langchain_core.messages import AIMessage

    llm = state.get("_llm")
    selected_destination = state.get("selected_destination")
    user_portrait = state.get("user_portrait", {})
    requirements = state.get("user_requirements", {})
    days = requirements.get("days", 5)
    start_date = requirements.get("start_date", "2024-04-01")

    style_proposals = state.get("style_proposals", [])
    selected_style = state.get("selected_style", "immersive")
    style_proposal = next((p for p in style_proposals if p.get("style_type") == selected_style), style_proposals[0] if style_proposals else {})

    dest_data = {
        "tags": user_portrait.get("primary_interests", []),
        "highlights": [],
        "budget_level": {"medium": 500}
    }

    # 并行执行Group C
    parallel_c = ParallelGroupC(llm)
    results = parallel_c.execute_all(
        selected_destination, dest_data, style_proposal, days, start_date, user_portrait
    )

    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"详细攻略生成完成(并行): {days}天行程",
        name="ParallelGuideGenerator"
    ))

    return {
        **state,
        **results,
        "current_stage": "guide_generated",
        "messages": messages
    }

