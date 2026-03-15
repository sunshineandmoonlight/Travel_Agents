"""
服务注册中心

提供智能体注册、发现和能力查询功能。
"""

from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import asyncio


logger = logging.getLogger('travel_agents.communication')


@dataclass
class AgentInfo:
    """智能体信息类"""

    agent_id: str                     # 智能体ID
    agent_name: str                   # 智能体名称
    agent_type: str                   # 智能体类型
    group: str                        # 所属组别 (A, B, C)

    # 能力信息
    capabilities: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)

    # 状态信息
    status: str = "idle"              # idle, busy, error, offline
    last_heartbeat: datetime = field(default_factory=datetime.now)

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)

    # 注册时间
    registered_at: datetime = field(default_factory=datetime.now)

    def is_alive(self, timeout: float = 30.0) -> bool:
        """检查智能体是否存活（基于心跳时间）"""
        return (datetime.now() - self.last_heartbeat).total_seconds() < timeout

    def is_available(self) -> bool:
        """检查智能体是否可用（存活且状态为idle）"""
        return self.is_alive() and self.status == "idle"


@dataclass
class ServiceInfo:
    """服务信息类"""

    service_id: str                   # 服务ID
    service_name: str                 # 服务名称
    service_type: str                 # 服务类型
    agent_id: str                     # 提供者智能体ID

    # 服务能力
    description: str = ""             # 服务描述
    input_schema: Optional[Dict] = None   # 输入模式
    output_schema: Optional[Dict] = None  # 输出模式

    # 状态
    status: str = "available"         # available, unavailable

    # 注册时间
    registered_at: datetime = field(default_factory=datetime.now)


class ServiceRegistry:
    """
    服务注册中心

    管理智能体注册、发现和能力查询。
    """

    def __init__(self, heartbeat_timeout: float = 30.0):
        # agent_id -> AgentInfo
        self._agents: Dict[str, AgentInfo] = {}

        # service_id -> ServiceInfo
        self._services: Dict[str, ServiceInfo] = {}

        # service_name -> service_ids
        self._service_index: Dict[str, Set[str]] = {}

        # agent_id -> service_ids
        self._agent_services: Dict[str, Set[str]] = {}

        # 心跳超时时间
        self._heartbeat_timeout = heartbeat_timeout

        # 统计信息
        self._stats = {
            "registered": 0,
            "unregistered": 0,
            "discoveries": 0,
            "heartbeats": 0
        }

    def register_agent(
        self,
        agent_id: str,
        agent_name: str,
        agent_type: str,
        group: str,
        capabilities: Optional[List[str]] = None,
        services: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        注册智能体

        Args:
            agent_id: 智能体ID
            agent_name: 智能体名称
            agent_type: 智能体类型
            group: 所属组别
            capabilities: 能力列表
            services: 提供的服务列表
            metadata: 元数据

        Returns:
            是否成功
        """
        agent_info = AgentInfo(
            agent_id=agent_id,
            agent_name=agent_name,
            agent_type=agent_type,
            group=group,
            capabilities=capabilities or [],
            services=services or [],
            metadata=metadata or {}
        )

        self._agents[agent_id] = agent_info
        self._stats["registered"] += 1

        logger.info(f"[ServiceRegistry] 智能体注册: {agent_id} ({agent_name}) - Group {group}")
        return True

    def unregister_agent(self, agent_id: str) -> bool:
        """
        注销智能体

        Args:
            agent_id: 智能体ID

        Returns:
            是否成功
        """
        if agent_id not in self._agents:
            return False

        # 删除智能体提供的服务
        service_ids = self._agent_services.get(agent_id, set()).copy()
        for service_id in service_ids:
            self.unregister_service(service_id)

        # 删除智能体
        del self._agents[agent_id]
        self._agent_services.pop(agent_id, None)

        self._stats["unregistered"] += 1
        logger.info(f"[ServiceRegistry] 智能体注销: {agent_id}")
        return True

    def register_service(
        self,
        agent_id: str,
        service_name: str,
        service_type: str,
        description: str = "",
        input_schema: Optional[Dict] = None,
        output_schema: Optional[Dict] = None
    ) -> str:
        """
        注册服务

        Args:
            agent_id: 提供者智能体ID
            service_name: 服务名称
            service_type: 服务类型
            description: 服务描述
            input_schema: 输入模式
            output_schema: 输出模式

        Returns:
            服务ID
        """
        import uuid
        service_id = f"svc_{agent_id}_{service_name}_{uuid.uuid4().hex[:8]}"

        service_info = ServiceInfo(
            service_id=service_id,
            service_name=service_name,
            service_type=service_type,
            agent_id=agent_id,
            description=description,
            input_schema=input_schema,
            output_schema=output_schema
        )

        self._services[service_id] = service_info

        # 更新索引
        if service_name not in self._service_index:
            self._service_index[service_name] = set()
        self._service_index[service_name].add(service_id)

        if agent_id not in self._agent_services:
            self._agent_services[agent_id] = set()
        self._agent_services[agent_id].add(service_id)

        # 更新智能体信息
        if agent_id in self._agents:
            if service_name not in self._agents[agent_id].services:
                self._agents[agent_id].services.append(service_name)

        logger.info(f"[ServiceRegistry] 服务注册: {service_name} by {agent_id}")
        return service_id

    def unregister_service(self, service_id: str) -> bool:
        """
        注销服务

        Args:
            service_id: 服务ID

        Returns:
            是否成功
        """
        if service_id not in self._services:
            return False

        service_info = self._services[service_id]

        # 从索引中删除
        if service_info.service_name in self._service_index:
            self._service_index[service_info.service_name].discard(service_id)

        if service_info.agent_id in self._agent_services:
            self._agent_services[service_info.agent_id].discard(service_id)

        # 删除服务
        del self._services[service_id]

        logger.info(f"[ServiceRegistry] 服务注销: {service_id}")
        return True

    def heartbeat(self, agent_id: str, status: str = "idle") -> bool:
        """
        智能体心跳

        Args:
            agent_id: 智能体ID
            status: 当前状态

        Returns:
            是否成功
        """
        if agent_id not in self._agents:
            return False

        self._agents[agent_id].last_heartbeat = datetime.now()
        self._agents[agent_id].status = status
        self._stats["heartbeats"] += 1

        return True

    def discover_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """
        发现智能体

        Args:
            agent_id: 智能体ID

        Returns:
            智能体信息（不存在返回None）
        """
        self._stats["discoveries"] += 1
        return self._agents.get(agent_id)

    def discover_agents_by_type(self, agent_type: str) -> List[AgentInfo]:
        """
        按类型发现智能体

        Args:
            agent_type: 智能体类型

        Returns:
            智能体信息列表
        """
        self._stats["discoveries"] += 1
        return [
            agent for agent in self._agents.values()
            if agent.agent_type == agent_type and agent.is_available()
        ]

    def discover_agents_by_group(self, group: str) -> List[AgentInfo]:
        """
        按组别发现智能体

        Args:
            group: 组别 (A, B, C)

        Returns:
            智能体信息列表
        """
        self._stats["discoveries"] += 1
        return [
            agent for agent in self._agents.values()
            if agent.group == group and agent.is_available()
        ]

    def discover_agents_by_capability(self, capability: str) -> List[AgentInfo]:
        """
        按能力发现智能体

        Args:
            capability: 能力名称

        Returns:
            智能体信息列表
        """
        self._stats["discoveries"] += 1
        return [
            agent for agent in self._agents.values()
            if capability in agent.capabilities and agent.is_available()
        ]

    def discover_service(self, service_name: str) -> List[ServiceInfo]:
        """
        发现服务

        Args:
            service_name: 服务名称

        Returns:
            服务信息列表
        """
        service_ids = self._service_index.get(service_name, set())
        return [
            self._services[sid]
            for sid in service_ids
            if sid in self._services and self._services[sid].status == "available"
        ]

    def get_agent_services(self, agent_id: str) -> List[ServiceInfo]:
        """
        获取智能体提供的服务

        Args:
            agent_id: 智能体ID

        Returns:
            服务信息列表
        """
        service_ids = self._agent_services.get(agent_id, set())
        return [self._services[sid] for sid in service_ids if sid in self._services]

    def get_all_agents(self) -> List[AgentInfo]:
        """获取所有智能体"""
        return list(self._agents.values())

    def get_available_agents(self) -> List[AgentInfo]:
        """获取所有可用的智能体"""
        return [agent for agent in self._agents.values() if agent.is_available()]

    def cleanup_stale_agents(self) -> int:
        """
        清理过期智能体

        Returns:
            清理的智能体数量
        """
        stale_agents = [
            agent_id for agent_id, agent in self._agents.items()
            if not agent.is_alive(self._heartbeat_timeout)
        ]

        for agent_id in stale_agents:
            self.unregister_agent(agent_id)
            logger.info(f"[ServiceRegistry] 清理过期智能体: {agent_id}")

        return len(stale_agents)

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        available_count = len(self.get_available_agents())
        stale_count = len(self._agents) - available_count

        return {
            **self._stats,
            "agents": {
                "total": len(self._agents),
                "available": available_count,
                "stale": stale_count
            },
            "services": {
                "total": len(self._services),
                "available": sum(1 for s in self._services.values() if s.status == "available")
            }
        }


# 全局ServiceRegistry实例
_registry_instance: Optional[ServiceRegistry] = None


def get_service_registry() -> ServiceRegistry:
    """获取全局ServiceRegistry实例"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ServiceRegistry()
    return _registry_instance


# 旅行系统智能体类型常量
class TravelAgentTypes:
    """旅行系统智能体类型常量"""

    # Group A - 分析组
    USER_REQUIREMENT_ANALYST = "user_requirement_analyst"
    DESTINATION_MATCHER = "destination_matcher"
    RANKING_SCORER = "ranking_scorer"

    # Group B - 设计组
    IMMERSIVE_DESIGNER = "immersive_designer"
    EXPLORATION_DESIGNER = "exploration_designer"
    RELAXATION_DESIGNER = "relaxation_designer"
    HIDDEN_GEM_DESIGNER = "hidden_gem_designer"

    # Group C - 规划组
    ATTRACTION_SCHEDULER = "attraction_scheduler"
    ACCOMMODATION_ADVISOR = "accommodation_advisor"
    DINING_RECOMMENDER = "dining_recommender"
    TRANSPORT_PLANNER = "transport_planner"
    GUIDE_FORMATTER = "guide_formatter"
    LLM_GUIDE_WRITER = "llm_guide_writer"


# 旅行系统能力常量
class TravelCapabilities:
    """旅行系统能力常量"""

    # 分析能力
    ANALYZE_REQUIREMENTS = "analyze_requirements"
    MATCH_DESTINATION = "match_destination"
    RANK_DESTINATIONS = "rank_destinations"

    # 设计能力
    DESIGN_IMMERSIVE = "design_immersive"
    DESIGN_EXPLORATION = "design_exploration"
    DESIGN_RELAXATION = "design_relaxation"
    DESIGN_HIDDEN_GEM = "design_hidden_gem"

    # 规划能力
    PLAN_ATTRACTION = "plan_attraction"
    ADVISE_ACCOMMODATION = "advise_accommodation"
    RECOMMEND_DINING = "recommend_dining"
    PLAN_TRANSPORT = "plan_transport"
    FORMAT_GUIDE = "format_guide"
    WRITE_GUIDE = "write_guide"


# 旅行系统服务常量
class TravelServices:
    """旅行系统服务常量"""

    # 分析服务
    ANALYZE_USER_REQUIREMENTS = "analyze_user_requirements"
    FIND_DESTINATIONS = "find_destinations"
    RANK_DESTINATIONS = "rank_destinations"

    # 设计服务
    DESIGN_STYLE = "design_style"
    CREATE_PROPOSAL = "create_proposal"

    # 规划服务
    PLAN_ITINERARY = "plan_itinerary"
    RECOMMEND_ATTRACTIONS = "recommend_attractions"
    RECOMMEND_RESTAURANTS = "recommend_restaurants"
    RECOMMEND_HOTELS = "recommend_hotels"
    PLAN_TRANSPORT = "plan_transport"

    # 生成服务
    GENERATE_GUIDE = "generate_guide"
    FORMAT_GUIDE = "format_guide"
