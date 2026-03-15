"""
组B: 风格方案智能体

包含4个智能体：
1. ImmersiveDesigner - 沉浸式方案设计师
2. ExplorationDesigner - 探索式方案设计师
3. RelaxationDesigner - 松弛式方案设计师
4. HiddenGemDesigner - 小众宝藏方案设计师

支持两种模式:
- 原有函数式接口（向后兼容）
- 通信式智能体包装类（新功能）
"""

from typing import Dict, Any, List
import logging
import asyncio

logger = logging.getLogger('travel_agents')

# 导入通信模块
from tradingagents.communication import (
    CommunicatingAgent,
    TravelAgentTypes,
    TravelCapabilities,
    TravelServices,
    AgentMessage,
    create_response
)

# 导入原有设计函数
from .immersive_designer import (
    design_immersive_style,
    immersive_designer_node,
    create_immersive_proposal
)

from .exploration_designer import (
    design_exploration_style,
    exploration_designer_node,
    create_exploration_proposal
)

from .relaxation_designer import (
    design_relaxation_style,
    relaxation_designer_node,
    create_relaxation_proposal
)

from .hidden_gem_designer import (
    design_hidden_gem_style,
    hidden_gem_designer_node,
    create_hidden_gem_proposal
)


# ========== 通信式智能体包装类 ==========

class ImmersiveDesignerAgent(CommunicatingAgent):
    """沉浸式方案设计师 - 通信版本"""

    def __init__(self, llm=None):
        super().__init__(
            agent_id="immersive_designer",
            agent_name="ImmersiveDesigner",
            agent_type=TravelAgentTypes.IMMERSIVE_DESIGNER,
            group="B"
        )
        self._llm = llm

    def get_capabilities(self) -> List[str]:
        return [TravelCapabilities.DESIGN_IMMERSIVE]

    def get_services(self) -> List[str]:
        return [TravelServices.DESIGN_STYLE]

    def handle_request(self, message: AgentMessage):
        action = message.content.get("action")
        if action == "design_proposal":
            destination = message.content.get("destination")
            dest_data = message.content.get("dest_data", {})
            user_portrait = message.content.get("user_portrait")
            days = message.content.get("days", 5)

            self.report_progress(25, "设计沉浸式方案...")
            proposal = design_immersive_style(destination, dest_data, user_portrait, days, self._llm)

            self.report_progress(100, "方案设计完成")
            self.publish_event("proposal_created", {
                "style": "immersive",
                "proposal": proposal
            })

            return create_response(message, {"success": True, "proposal": proposal})

        return super().handle_request(message)

    def create_proposal(self, destination: str, dest_data: Dict, user_portrait: Dict, days: int):
        """创建方案（便捷方法）"""
        return design_immersive_style(destination, dest_data, user_portrait, days, self._llm)


class ExplorationDesignerAgent(CommunicatingAgent):
    """探索式方案设计师 - 通信版本"""

    def __init__(self, llm=None):
        super().__init__(
            agent_id="exploration_designer",
            agent_name="ExplorationDesigner",
            agent_type=TravelAgentTypes.EXPLORATION_DESIGNER,
            group="B"
        )
        self._llm = llm

    def get_capabilities(self) -> List[str]:
        return [TravelCapabilities.DESIGN_EXPLORATION]

    def get_services(self) -> List[str]:
        return [TravelServices.DESIGN_STYLE]

    def create_proposal(self, destination: str, dest_data: Dict, user_portrait: Dict, days: int):
        """创建方案（便捷方法）"""
        return design_exploration_style(destination, dest_data, user_portrait, days, self._llm)


class RelaxationDesignerAgent(CommunicatingAgent):
    """松弛式方案设计师 - 通信版本"""

    def __init__(self, llm=None):
        super().__init__(
            agent_id="relaxation_designer",
            agent_name="RelaxationDesigner",
            agent_type=TravelAgentTypes.RELAXATION_DESIGNER,
            group="B"
        )
        self._llm = llm

    def get_capabilities(self) -> List[str]:
        return [TravelCapabilities.DESIGN_RELAXATION]

    def get_services(self) -> List[str]:
        return [TravelServices.DESIGN_STYLE]

    def create_proposal(self, destination: str, dest_data: Dict, user_portrait: Dict, days: int):
        """创建方案（便捷方法）"""
        return design_relaxation_style(destination, dest_data, user_portrait, days, self._llm)


class HiddenGemDesignerAgent(CommunicatingAgent):
    """小众宝藏方案设计师 - 通信版本"""

    def __init__(self, llm=None):
        super().__init__(
            agent_id="hidden_gem_designer",
            agent_name="HiddenGemDesigner",
            agent_type=TravelAgentTypes.HIDDEN_GEM_DESIGNER,
            group="B"
        )
        self._llm = llm

    def get_capabilities(self) -> List[str]:
        return [TravelCapabilities.DESIGN_HIDDEN_GEM]

    def get_services(self) -> List[str]:
        return [TravelServices.DESIGN_STYLE]

    def create_proposal(self, destination: str, dest_data: Dict, user_portrait: Dict, days: int):
        """创建方案（便捷方法）"""
        return design_hidden_gem_style(destination, dest_data, user_portrait, days, self._llm)


def generate_style_proposals(
    destination: str,
    dest_data: Dict[str, Any],
    user_portrait: Dict[str, Any],
    days: int,
    llm=None
) -> List[Dict[str, Any]]:
    """
    生成所有4种风格的旅行方案

    依次调用4个设计师智能体

    Args:
        destination: 目的地名称
        dest_data: 目的地数据
        user_portrait: 用户画像
        days: 旅行天数
        llm: LLM实例（可选）

    Returns:
        4种风格方案列表
    """
    logger.info(f"[组B智能体] 为{destination}生成4种风格方案")

    proposals = []

    # 1. 沉浸式
    proposals.append(design_immersive_style(destination, dest_data, user_portrait, days, llm))

    # 2. 探索式
    proposals.append(design_exploration_style(destination, dest_data, user_portrait, days, llm))

    # 3. 松弛式
    proposals.append(design_relaxation_style(destination, dest_data, user_portrait, days, llm))

    # 4. 小众宝藏
    proposals.append(design_hidden_gem_style(destination, dest_data, user_portrait, days, llm))

    logger.info(f"[组B智能体] 生成完成: {len(proposals)}个风格方案")

    return proposals


async def generate_style_proposals_parallel(
    destination: str,
    dest_data: Dict[str, Any],
    user_portrait: Dict[str, Any],
    days: int,
    llm=None
) -> List[Dict[str, Any]]:
    """
    🚀 并行生成所有4种风格的旅行方案

    4个风格设计师智能体同时工作，大幅提升速度

    Args:
        destination: 目的地名称
        dest_data: 目的地数据
        user_portrait: 用户画像
        days: 旅行天数
        llm: LLM实例（可选）

    Returns:
        4种风格方案列表
    """
    logger.info(f"[组B智能体] 🚀 并行生成4种风格方案: {destination}")

    # 定义并行任务
    async def run_immersive_task():
        """沉浸式设计师任务"""
        try:
            logger.info(f"[并行执行] ImmersiveDesigner 开始工作")
            # 在事件循环中运行同步函数
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                design_immersive_style,
                destination, dest_data, user_portrait, days, llm
            )
            logger.info(f"[并行执行] ImmersiveDesigner 完成")
            return result
        except Exception as e:
            logger.error(f"[并行执行] ImmersiveDesigner 失败: {e}")
            return None

    async def run_exploration_task():
        """探索式设计师任务"""
        try:
            logger.info(f"[并行执行] ExplorationDesigner 开始工作")
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                design_exploration_style,
                destination, dest_data, user_portrait, days, llm
            )
            logger.info(f"[并行执行] ExplorationDesigner 完成")
            return result
        except Exception as e:
            logger.error(f"[并行执行] ExplorationDesigner 失败: {e}")
            return None

    async def run_relaxation_task():
        """松弛式设计师任务"""
        try:
            logger.info(f"[并行执行] RelaxationDesigner 开始工作")
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                design_relaxation_style,
                destination, dest_data, user_portrait, days, llm
            )
            logger.info(f"[并行执行] RelaxationDesigner 完成")
            return result
        except Exception as e:
            logger.error(f"[并行执行] RelaxationDesigner 失败: {e}")
            return None

    async def run_hidden_gem_task():
        """小众宝藏设计师任务"""
        try:
            logger.info(f"[并行执行] HiddenGemDesigner 开始工作")
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                design_hidden_gem_style,
                destination, dest_data, user_portrait, days, llm
            )
            logger.info(f"[并行执行] HiddenGemDesigner 完成")
            return result
        except Exception as e:
            logger.error(f"[并行执行] HiddenGemDesigner 失败: {e}")
            return None

    # 🚀 并行执行4个风格设计师
    results = await asyncio.gather(
        run_immersive_task(),
        run_exploration_task(),
        run_relaxation_task(),
        run_hidden_gem_task(),
        return_exceptions=True
    )

    # 过滤掉失败的结果
    proposals = [r for r in results if r is not None and not isinstance(r, Exception)]

    logger.info(f"[组B智能体] ✅ 并行生成完成: {len(proposals)}/4 个风格方案成功")

    # 如果有失败的，用兜底方案补充
    if len(proposals) < 4:
        logger.warning(f"[组B智能体] 部分方案失败，使用串行兜底")
        # 获取失败的风格类型
        style_types = [p.get('style_type') for p in proposals if p]

        # 补充缺失的风格
        if 'immersive' not in style_types:
            proposals.append(design_immersive_style(destination, dest_data, user_portrait, days, llm))
        if 'exploration' not in style_types:
            proposals.append(design_exploration_style(destination, dest_data, user_portrait, days, llm))
        if 'relaxation' not in style_types:
            proposals.append(design_relaxation_style(destination, dest_data, user_portrait, days, llm))
        if 'hidden_gem' not in style_types:
            proposals.append(design_hidden_gem_style(destination, dest_data, user_portrait, days, llm))

    return proposals


__all__ = [
    # ImmersiveDesigner
    "design_immersive_style",
    "immersive_designer_node",
    "create_immersive_proposal",
    "ImmersiveDesignerAgent",  # 新增：通信式智能体类

    # ExplorationDesigner
    "design_exploration_style",
    "exploration_designer_node",
    "create_exploration_proposal",
    "ExplorationDesignerAgent",  # 新增：通信式智能体类

    # RelaxationDesigner
    "design_relaxation_style",
    "relaxation_designer_node",
    "create_relaxation_proposal",
    "RelaxationDesignerAgent",  # 新增：通信式智能体类

    # HiddenGemDesigner
    "design_hidden_gem_style",
    "hidden_gem_designer_node",
    "create_hidden_gem_proposal",
    "HiddenGemDesignerAgent",  # 新增：通信式智能体类

    # Combined
    "generate_style_proposals",
    "generate_style_proposals_parallel",  # 🚀 并行版本
]
