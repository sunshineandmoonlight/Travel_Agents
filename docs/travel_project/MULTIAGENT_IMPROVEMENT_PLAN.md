# TravelAgents-CN 多智能体系统改进计划

## 📋 改进概览

| 改进项 | 优先级 | 复杂度 | 预估工作量 | 影响 |
|--------|--------|--------|------------|------|
| 1. 消息传递协作 | 高 | 高 | 2-3周 | 核心架构升级 |
| 2. Group B API加强 | 中 | 中 | 1周 | 提升数据质量 |
| 3. 智能体通信机制 | 高 | 中 | 1-2周 | 增强协作能力 |

---

## 改进计划 1: 从函数式调用改造为基于消息传递的协作

### 1.1 当前状态分析

**现状**:
```python
# 当前实现: 函数式调用，串行执行
def recommend_destinations(requirements, llm):
    # Agent A1
    user_portrait = create_user_portrait(requirements, llm)

    # Agent A2 (依赖A1的结果)
    matching_result = match_destinations(user_portrait, travel_scope, llm)

    # Agent A3 (依赖A2的结果)
    ranking_result = rank_and_select_top(
        matching_result.get("candidates", []),
        user_portrait,
        top_n=4,
        llm=llm
    )
    return ranking_result
```

**问题**:
- ❌ 智能体之间直接函数调用，耦合度高
- ❌ 状态通过参数传递，难以追踪
- ❌ 无法并行执行独立任务
- ❌ 难以实现智能体之间的协商和辩论
- ❌ 不符合真正的多智能体系统理念

### 1.2 目标状态

**基于消息传递的多智能体系统**:
```python
# 目标: 智能体通过消息通信，异步协作
class AgentMessage:
    sender: str
    receiver: str
    content: Any
    message_type: str  # request, response, notification
    timestamp: datetime

class MessageBus:
    def publish(self, message: AgentMessage):
        """发布消息到总线"""

    def subscribe(self, agent_id: str, handler):
        """订阅消息"""

# 智能体不再直接调用，而是发送消息
await message_bus.publish(AgentMessage(
    sender="UserRequirementAnalyst",
    receiver="DestinationMatcher",
    content={"user_portrait": user_portrait},
    message_type="request"
))
```

### 1.3 实现方案

#### 方案A: 基于LangGraph的消息流 (推荐)

**优势**: 兼容现有代码，渐进式升级

```python
# tradingagents/agents/messaging/graph_message_router.py

from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator

class AgentState(TypedDict):
    """智能体共享状态"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_agent: str
    user_requirements: dict
    user_portrait: dict
    matched_destinations: list
    ranked_destinations: list
    final_proposals: dict

def user_requirement_analyst_node(state: AgentState) -> AgentState:
    """需求分析智能体节点"""
    # 执行分析
    user_portrait = create_user_portrait(state["user_requirements"], llm)

    # 发布消息
    state["messages"].append(AIMessage(
        content=f"需求分析完成: {user_portrait['travel_type']}",
        name="UserRequirementAnalyst",
        additional_kwargs={"user_portrait": user_portrait}
    ))

    state["user_portrait"] = user_portrait
    state["current_agent"] = "UserRequirementAnalyst"
    return state

def destination_matcher_node(state: AgentState) -> AgentState:
    """目的地匹配智能体节点"""
    # 从状态中获取数据，而不是从参数
    user_portrait = state["user_portrait"]

    # 执行匹配
    matching_result = match_destinations(
        user_portrait,
        state["user_requirements"]["travel_scope"],
        llm
    )

    # 发布消息
    state["messages"].append(AIMessage(
        content=f"匹配到 {len(matching_result['candidates'])} 个目的地",
        name="DestinationMatcher",
        additional_kwargs={"candidates": matching_result["candidates"]}
    ))

    state["matched_destinations"] = matching_result["candidates"]
    state["current_agent"] = "DestinationMatcher"
    return state

def ranking_scorer_node(state: AgentState) -> AgentState:
    """排序评分智能体节点"""
    candidates = state["matched_destinations"]
    user_portrait = state["user_portrait"]

    # 执行排序
    ranking_result = rank_and_select_top(candidates, user_portrait, 4, llm)

    # 发布消息
    state["messages"].append(AIMessage(
        content="排序完成，TOP 4推荐已生成",
        name="RankingScorer",
        additional_kwargs={"destinations": ranking_result["destination_cards"]}
    ))

    state["ranked_destinations"] = ranking_result["destination_cards"]
    state["current_agent"] = "RankingScorer"
    return state

def should_continue_matching(state: AgentState) -> str:
    """条件边: 决定下一步"""
    if state.get("matched_destinations"):
        return "to_ranking"
    return "to_matching"

# 构建消息流图
def create_message_flow_graph():
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("user_requirement_analyst", user_requirement_analyst_node)
    workflow.add_node("destination_matcher", destination_matcher_node)
    workflow.add_node("ranking_scorer", ranking_scorer_node)

    # 设置入口
    workflow.set_entry_point("user_requirement_analyst")

    # 添加条件边
    workflow.add_conditional_edges(
        "user_requirement_analyst",
        should_continue_matching,
        {
            "to_matching": "destination_matcher",
        }
    )

    workflow.add_conditional_edges(
        "destination_matcher",
        should_continue_matching,
        {
            "to_ranking": "ranking_scorer",
        }
    )

    workflow.add_edge("ranking_scorer", END)

    return workflow.compile()
```

#### 方案B: 基于消息总线的异步通信

**优势**: 真正的解耦，支持分布式部署

```python
# tradingagents/agents/messaging/message_bus.py

import asyncio
from typing import Dict, Callable, List, Any
from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass
class AgentMessage:
    id: str
    sender: str
    receiver: str  # "broadcast" for broadcast
    content: Any
    message_type: str  # request, response, notification, error
    timestamp: datetime
    correlation_id: str = None  # 用于关联请求和响应
    reply_to: str = None  # 响应时指定原始消息ID

    @classmethod
    def create_request(cls, sender: str, receiver: str, content: Any):
        return cls(
            id=str(uuid.uuid4()),
            sender=sender,
            receiver=receiver,
            content=content,
            message_type="request",
            timestamp=datetime.now(),
            correlation_id=str(uuid.uuid4())
        )

class MessageBus:
    """异步消息总线"""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._message_queue = asyncio.Queue()
        self._running = False

    def subscribe(self, agent_id: str, handler: Callable):
        """订阅消息"""
        if agent_id not in self._subscribers:
            self._subscribers[agent_id] = []
        self._subscribers[agent_id].append(handler)

    async def publish(self, message: AgentMessage):
        """发布消息"""
        await self._message_queue.put(message)

    async def start(self):
        """启动消息总线"""
        self._running = True
        asyncio.create_task(self._process_messages())

    async def _process_messages(self):
        """处理消息队列"""
        while self._running:
            message = await self._message_queue.get()

            # 广播消息
            if message.receiver == "broadcast":
                for agent_id, handlers in self._subscribers.items():
                    if agent_id != message.sender:  # 不发送给自己
                        for handler in handlers:
                            await handler(message)

            # 点对点消息
            elif message.receiver in self._subscribers:
                for handler in self._subscribers[message.receiver]:
                    await handler(message)

# 全局消息总线
message_bus = MessageBus()

# 智能体基类
class MessageBasedAgent:
    def __init__(self, agent_id: str, llm=None):
        self.agent_id = agent_id
        self.llm = llm
        self._pending_requests: Dict[str, Any] = {}  # correlation_id -> Future

    async def start(self):
        """启动智能体"""
        message_bus.subscribe(self.agent_id, self._handle_message)

    async def send_request(self, receiver: str, content: Any, timeout=30) -> Any:
        """发送请求并等待响应"""
        message = AgentMessage.create_request(self.agent_id, receiver, content)

        # 创建Future等待响应
        future = asyncio.Future()
        self._pending_requests[message.correlation_id] = future

        await message_bus.publish(message)

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            del self._pending_requests[message.correlation_id]
            raise TimeoutError(f"请求 {receiver} 超时")

    async def send_response(self, original_message: AgentMessage, content: Any):
        """发送响应"""
        response = AgentMessage(
            id=str(uuid.uuid4()),
            sender=self.agent_id,
            receiver=original_message.sender,
            content=content,
            message_type="response",
            timestamp=datetime.now(),
            correlation_id=original_message.correlation_id,
            reply_to=original_message.id
        )
        await message_bus.publish(response)

    async def _handle_message(self, message: AgentMessage):
        """处理接收到的消息"""
        if message.message_type == "response":
            # 处理响应
            if message.correlation_id in self._pending_requests:
                future = self._pending_requests[message.correlation_id]
                future.set_result(message.content)
                del self._pending_requests[message.correlation_id]

        elif message.message_type == "request":
            # 处理请求
            try:
                result = await self._process_request(message)
                await self.send_response(message, result)
            except Exception as e:
                await self.send_error_response(message, str(e))

    async def _process_request(self, message: AgentMessage) -> Any:
        """子类实现具体的请求处理逻辑"""
        raise NotImplementedError

    async def send_error_response(self, original_message: AgentMessage, error: str):
        """发送错误响应"""
        error_message = AgentMessage(
            id=str(uuid.uuid4()),
            sender=self.agent_id,
            receiver=original_message.sender,
            content={"error": error},
            message_type="error",
            timestamp=datetime.now(),
            correlation_id=original_message.correlation_id,
            reply_to=original_message.id
        )
        await message_bus.publish(error_message)

# 具体智能体实现
class UserRequirementAnalystAgent(MessageBasedAgent):
    def __init__(self, llm=None):
        super().__init__("UserRequirementAnalyst", llm)

    async def _process_request(self, message: AgentMessage) -> Any:
        """处理需求分析请求"""
        requirements = message.content.get("requirements")

        # 执行分析
        user_portrait = create_user_portrait(requirements, self.llm)

        # 广播分析结果
        broadcast = AgentMessage(
            id=str(uuid.uuid4()),
            sender=self.agent_id,
            receiver="broadcast",
            content={
                "type": "user_portrait_completed",
                "user_portrait": user_portrait
            },
            message_type="notification",
            timestamp=datetime.now()
        )
        await message_bus.publish(broadcast)

        return {
            "status": "success",
            "user_portrait": user_portrait
        }

class DestinationMatcherAgent(MessageBasedAgent):
    def __init__(self, llm=None):
        super().__init__("DestinationMatcher", llm)
        self._latest_user_portrait = None

    async def _process_request(self, message: AgentMessage) -> Any:
        """处理目的地匹配请求"""
        if message.content.get("type") == "user_portrait_completed":
            # 接收到用户画像完成通知
            self._latest_user_portrait = message.content.get("user_portrait")

            # 自动开始匹配
            travel_scope = message.content.get("travel_scope", "domestic")
            matching_result = match_destinations(
                self._latest_user_portrait,
                travel_scope,
                self.llm
            )

            # 广播匹配结果
            broadcast = AgentMessage(
                id=str(uuid.uuid4()),
                sender=self.agent_id,
                receiver="broadcast",
                content={
                    "type": "matching_completed",
                    "candidates": matching_result["candidates"]
                },
                message_type="notification",
                timestamp=datetime.now()
            )
            await message_bus.publish(broadcast)

            return {"status": "acknowledged"}

        elif message.content.get("type") == "get_candidates":
            # 返回候选列表
            return {
                "candidates": self._latest_candidates,
                "llm_description": self._latest_llm_description
            }
```

### 1.4 迁移步骤

**阶段1: 准备阶段 (1周)**
```bash
# 1. 创建消息基础设施
mkdir -p tradingagents/agents/messaging
touch tradingagents/agents/messaging/__init__.py
touch tradingagents/agents/messaging/message_bus.py
touch tradingagents/agents/messaging/graph_message_router.py

# 2. 编写单元测试
touch tests/unit/test_message_bus.py
touch tests/unit/test_message_based_agent.py
```

**阶段2: 双模式运行 (1周)**
```python
# 保留原有函数式接口
def recommend_destinations(requirements, llm):
    """兼容模式: 函数式调用"""
    # ... 原有代码 ...

async def recommend_destinations_async(requirements, llm):
    """新模式: 消息传递"""
    # 创建智能体实例
    analyst = UserRequirementAnalystAgent(llm)
    matcher = DestinationMatcherAgent(llm)
    scorer = RankingScorerAgent(llm)

    # 启动消息总线
    await message_bus.start()
    await analyst.start()
    await matcher.start()
    await scorer.start()

    # 发送请求
    result = await analyst.send_request(
        "UserRequirementAnalyst",
        {"requirements": requirements}
    )

    # 等待完成
    await asyncio.sleep(1)  # 让其他智能体处理

    # 获取最终结果
    final_result = await scorer.send_request(
        "RankingScorer",
        {"type": "get_final_result"}
    )

    return final_result
```

**阶段3: 完全迁移 (1周)**
```python
# 更新API路由
@router.post("/get-destinations-stream")
async def get_destinations_stream(request: TravelRequirementForm):
    """使用消息传递模式"""
    from tradingagents.agents.messaging.message_bus import message_bus
    from tradingagents.agents.messaging.group_a_agents import (
        UserRequirementAnalystAgent,
        DestinationMatcherAgent,
        RankingScorerAgent
    )

    async def event_generator():
        # 启动消息总线
        await message_bus.start()

        # 创建智能体
        analyst = UserRequirementAnalystAgent(llm)
        matcher = DestinationMatcherAgent(llm)
        scorer = RankingScorerAgent(llm)

        await analyst.start()
        await matcher.start()
        await scorer.start()

        # 发送初始请求
        await analyst.send_request(
            "UserRequirementAnalyst",
            {"requirements": request.dict()}
        )

        # 监听进度消息
        async def progress_handler(message: AgentMessage):
            if message.message_type == "notification":
                yield f"data: {json.dumps(message.content)}\n\n"

        # ... 处理流式输出 ...

    return StreamingResponse(event_generator())
```

---

## 改进计划 2: Group B API工具调用加强

### 2.1 当前状态分析

**现状**:
```python
# Group B Designers 当前的API使用情况检查:
immersive_designer:    高德API: No,  SerpAPI: No,  LLM: No
exploration_designer:  高德API: No,  SerpAPI: No,  LLM: No
relaxation_designer:   高德API: No,  SerpAPI: No,  LLM: No
hidden_gem_designer:   高德API: No,  SerpAPI: No,  LLM: No
```

**问题**:
- ❌ Group B主要使用静态数据，没有实时API调用
- ❌ 缺少真实的景点搜索和筛选
- ❌ 没有使用LLM生成方案描述
- ❌ 风格差异主要体现在数据层面，而非真实的智能设计

### 2.2 目标状态

**增强后的Group B**:
```python
# 每个Designer应该:
1. 使用SerpAPI搜索实时景点数据
2. 使用OpenTripMap获取景点详情
3. 使用LLM生成个性化的方案描述
4. 根据风格特点筛选和排序景点
```

### 2.3 实现方案

#### 步骤1: 创建统一的API工具基类

```python
# tradingagents/agents/group_b/api_tools/base_api_tool.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger('travel_agents')

class BaseAPITool(ABC):
    """API工具基类"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self._cache = {}  # 简单缓存

    @abstractmethod
    async def search_attractions(
        self,
        destination: str,
        keywords: str,
        days: int,
        style: str
    ) -> List[Dict[str, Any]]:
        """搜索景点"""
        pass

    @abstractmethod
    async def get_attraction_details(self, attraction_id: str) -> Dict[str, Any]:
        """获取景点详情"""
        pass

    def _get_cache_key(self, method: str, **kwargs) -> str:
        """生成缓存键"""
        params = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return f"{method}:{params}"

    async def _cached_call(self, key: str, func):
        """带缓存的调用"""
        if key in self._cache:
            logger.info(f"[缓存命中] {key}")
            return self._cache[key]

        result = await func()
        self._cache[key] = result
        return result
```

#### 步骤2: 实现SerpAPI工具

```python
# tradingagents/agents/group_b/api_tools/serpapi_tool.py

import httpx
from typing import List, Dict, Any
from .base_api_tool import BaseAPITool

class SerpAPITool(BaseAPITool):
    """SerpAPI景点搜索工具"""

    def __init__(self, api_key: str = None):
        super().__init__(api_key)
        self.base_url = "https://serpapi.com/search"

    async def search_attractions(
        self,
        destination: str,
        keywords: str,
        days: int,
        style: str
    ) -> List[Dict[str, Any]]:
        """使用SerpAPI搜索景点"""

        # 根据风格调整搜索关键词
        style_keywords = self._get_style_keywords(style)
        search_query = f"{destination} {keywords} {style_keywords} 景点 旅游"

        cache_key = self._get_cache_key(
            "search",
            destination=destination,
            keywords=search_query
        )

        async def _search():
            params = {
                "engine": "google_local",
                "q": search_query,
                "type": "search",
                "api_key": self.api_key,
                "num": 20  # 获取更多结果
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()

            # 解析结果
            attractions = []
            if "local_results" in data:
                for place in data["local_results"][:15]:  # 取前15个
                    attraction = {
                        "name": place.get("title", ""),
                        "address": place.get("address", ""),
                        "rating": place.get("rating", 0),
                        "reviews": place.get("reviews", 0),
                        "phone": place.get("phone", ""),
                        "website": place.get("website", ""),
                        "description": place.get("description", ""),
                        "coordinates": {
                            "lat": place.get("gps_coordinates", {}).get("latitude"),
                            "lng": place.get("gps_coordinates", {}).get("longitude")
                        },
                        "photos": place.get("photos", []),
                        "types": place.get("type", "").split(", "),
                        "price_level": place.get("price_level", ""),
                        "source": "serpapi"
                    }
                    attractions.append(attraction)

            logger.info(f"[SerpAPI] 搜索到 {len(attractions)} 个景点")
            return attractions

        return await self._cached_call(cache_key, _search)

    async def get_attraction_details(self, attraction_id: str) -> Dict[str, Any]:
        """获取景点详情 (SerpAPI不直接支持，返回基本信息)"""
        # SerpAPI的详细信息需要通过place_id获取
        return {}

    def _get_style_keywords(self, style: str) -> str:
        """根据风格返回搜索关键词"""
        style_map = {
            "immersive": "博物馆 文化 深度",
            "exploration": "打卡 热门 景点",
            "relaxation": "公园 休闲 轻松",
            "hidden_gem": "小众 冷门 私藏"
        }
        return style_map.get(style, "")
```

#### 步骤3: 实现OpenTripMap工具

```python
# tradingagents/agents/group_b/api_tools/opentripmap_tool.py

import httpx
from typing import List, Dict, Any
from .base_api_tool import BaseAPITool

class OpenTripMapTool(BaseAPITool):
    """OpenTripMap景点工具"""

    def __init__(self, api_key: str = None):
        super().__init__(api_key)
        self.base_url = "https://api.opentripmap.com/0.1/en"

    async def search_attractions(
        self,
        destination: str,
        keywords: str,
        days: int,
        style: str
    ) -> List[Dict[str, Any]]:
        """搜索OpenTripMap景点"""

        # 首先获取目的地的坐标
        coords = await self._get_destination_coords(destination)
        if not coords:
            return []

        cache_key = self._get_cache_key(
            "search",
            destination=destination,
            keywords=keywords,
            style=style
        )

        async def _search():
            # 根据风格选择景点类型
            kinds = self._get_style_kinds(style)

            # 半径范围 (km)
            radius = min(50, days * 10)  # 根据天数调整搜索范围

            params = {
                "apikey": self.api_key,
                "lon": coords["lng"],
                "lat": coords["lat"],
                "radius": radius * 1000,  # 转换为米
                "kinds": kinds,
                "format": "json",
                "limit": 30
            }

            url = f"{self.base_url}/places/radius"
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

            # 解析结果
            attractions = []
            for place in data.get("features", [])[:20]:
                attraction = {
                    "name": place.get("properties", {}).get("name", ""),
                    "xid": place.get("properties", {}).get("xid", ""),  # OpenTripMap ID
                    "kinds": place.get("properties", {}).get("kinds", ""),
                    "address": self._get_address(place),
                    "coordinates": {
                        "lat": place.get("geometry", {}).get("coordinates", [])[1],
                        "lng": place.get("geometry", {}).get("coordinates", [])[0]
                    },
                    "wikidata": place.get("properties", {}).get("wikidata", ""),
                    "source": "opentripmap"
                }
                attractions.append(attraction)

            logger.info(f"[OpenTripMap] 搜索到 {len(attractions)} 个景点")
            return attractions

        return await self._cached_call(cache_key, _search)

    async def get_attraction_details(self, attraction_id: str) -> Dict[str, Any]:
        """获取景点详情"""
        cache_key = self._get_cache_key("details", xid=attraction_id)

        async def _get_details():
            url = f"{self.base_url}/places/xid/{attraction_id}"
            params = {
                "apikey": self.api_key
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

            return {
                "name": data.get("name", ""),
                "address": data.get("address", ""),
                "description": data.get("wikipedia_extracts", {}).get("text", ""),
                "image": data.get("preview", {}).get("source", ""),
                "rating": data.get("rate", 0),
                "url": data.get("otm", ""),
                "wikipedia": data.get("wikipedia", ""),
                "source": "opentripmap"
            }

        return await self._cached_call(cache_key, _get_details)

    async def _get_destination_coords(self, destination: str) -> Optional[Dict]:
        """获取目的地坐标"""
        url = f"{self.base_url}/places/geoname"
        params = {
            "apikey": self.api_key,
            "name": destination
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if data.get("features"):
                    coords = data["features"][0]["geometry"]["coordinates"]
                    return {"lat": coords[1], "lng": coords[0]}
            except Exception as e:
                logger.warning(f"[OpenTripMap] 获取坐标失败: {e}")

        return None

    def _get_style_kinds(self, style: str) -> str:
        """根据风格返回景点类型"""
        # OpenTripMap的kinds参数
        kind_map = {
            "immersive": "museums,cultural,churches,historic",
            "exploration": "tourist_facilities,view_points,nature",
            "relaxation": "parks,beaches,gardens",
            "hidden_gem": "other,interesting_places"
        }
        return kind_map.get(style, "")

    def _get_address(self, place: Dict) -> str:
        """从place对象中获取地址"""
        return place.get("properties", {}).get("address", {}).get("road", "")
```

#### 步骤4: 更新Group B智能体

```python
# tradingagents/agents/group_b/immersive_designer_enhanced.py

from typing import Dict, Any, List
from ..api_tools.serpapi_tool import SerpAPITool
from ..api_tools.opentripmap_tool import OpenTripMapTool
import logging

logger = logging.getLogger('travel_agents')

def design_immersive_style(
    destination: str,
    dest_data: Dict[str, Any],
    user_portrait: Dict[str, Any],
    days: int,
    llm=None
) -> Dict[str, Any]:
    """设计沉浸式旅行方案 (增强版)"""

    logger.info(f"[沉浸式设计师] 开始设计 {destination} 的沉浸式方案")

    # 1. 使用API工具搜索景点
    attractions = []

    # 优先使用SerpAPI
    serpapi_tool = SerpAPITool(api_key=os.getenv("SERPAPI_KEY"))
    if serpapi_tool.api_key:
        try:
            import asyncio
            serp_results = asyncio.run(serpapi_tool.search_attractions(
                destination=destination,
                keywords="博物馆 文化 历史",
                days=days,
                style="immersive"
            ))
            attractions.extend(serp_results)
            logger.info(f"[沉浸式设计师] SerpAPI搜索到 {len(serp_results)} 个景点")
        except Exception as e:
            logger.warning(f"[沉浸式设计师] SerpAPI搜索失败: {e}")

    # 补充OpenTripMap数据
    opentripmap_tool = OpenTripMapTool(api_key=os.getenv("OPENTRIPMAP_API_KEY"))
    if opentripmap_tool.api_key:
        try:
            otm_results = asyncio.run(opentripmap_tool.search_attractions(
                destination=destination,
                keywords="cultural",
                days=days,
                style="immersive"
            ))
            attractions.extend(otm_results)
            logger.info(f"[沉浸式设计师] OpenTripMap搜索到 {len(otm_results)} 个景点")
        except Exception as e:
            logger.warning(f"[沉浸式设计师] OpenTripMap搜索失败: {e}")

    # 2. 根据风格筛选景点
    filtered_attractions = _filter_cultural_attractions(attractions)

    # 3. 分配到每日行程 (少而精)
    daily_itinerary = []
    attractions_per_day = 2  # 沉浸式每天2-3个景点

    for day in range(days):
        day_attractions = filtered_attractions[
            day * attractions_per_day:(day + 1) * attractions_per_day
        ]

        daily_itinerary.append({
            "day": day + 1,
            "date": _get_date(user_portrait.get("start_date"), day),
            "attractions": [
                {
                    "name": attr.get("name", ""),
                    "address": attr.get("address", ""),
                    "description": attr.get("description", ""),
                    "suggested_duration": "3-4小时",  # 沉浸式需要更多时间
                    "best_time_to_visit": "上午9点-12点",
                    "source": attr.get("source", "database")
                }
                for attr in day_attractions
            ],
            "pace": "slow"  # 慢节奏
        })

    # 4. 使用LLM生成方案描述
    llm_description = _generate_immersive_description(
        destination,
        daily_itinerary,
        user_portrait,
        llm
    )

    # 5. 计算预算
    estimated_budget = _calculate_budget(destination, user_portrait, days)

    return {
        "style_type": "immersive",
        "style_name": "沉浸式",
        "style_description": "深度体验，慢节奏感受，每日2-3个景点",
        "daily_itinerary": daily_itinerary,
        "total_attractions": len(filtered_attractions),
        "llm_description": llm_description,
        "estimated_budget": estimated_budget,
        "api_sources_used": [
            src for src in set(a.get("source", "") for a in filtered_attractions)
        ],
        "agent_info": {
            "name_cn": "沉浸式设计师",
            "name_en": "ImmersiveDesigner",
            "icon": "🎭",
            "group": "B"
        }
    }

def _generate_immersive_description(
    destination: str,
    daily_itinerary: List[Dict],
    user_portrait: Dict[str, Any],
    llm=None
) -> str:
    """使用LLM生成沉浸式方案描述"""
    if llm:
        try:
            total_attractions = sum(len(day["attractions"]) for day in daily_itinerary)
            top_attractions = [a["name"] for day in daily_itinerary for a in day["attractions"][:3]]

            prompt = f"""请为以下沉浸式旅行方案生成一段吸引人的描述（约150-200字）：

目的地：{destination}
旅行天数：{len(daily_itinerary)}天
景点总数：{total_attractions}个（少而精）
核心景点：{', '.join(top_attractions)}

方案特点：
- 深度体验，每个景点停留3-4小时
- 慢节奏，拒绝走马观花
- 专注于文化、历史、艺术的沉浸式感受

请生成一段能吸引喜欢深度体验的旅行者的描述，突出这种旅行方式的独特魅力。

直接输出描述文字，不要标题。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            description = response.content.strip()
            logger.info(f"[沉浸式设计师] LLM生成描述成功: {len(description)}字")
            return description

        except Exception as e:
            logger.warning(f"[沉浸式设计师] LLM生成描述失败: {e}")

    # 默认描述
    return f"""这是一场深度文化之旅，在{destination}的{len(daily_itinerary)}天里，您将以沉浸式的方式体验这座城市的灵魂。不同于走马观花的打卡式旅行，我们精心挑选了最具代表性的文化景点，每天只安排2-3个深度游览点，让您有充足时间去感受历史的厚重与艺术的精妙。"""
```

### 2.4 实现时间表

| 任务 | 工作量 | 负责人 | 依赖 |
|------|--------|--------|------|
| 创建API工具基类 | 0.5天 | - | - |
| 实现SerpAPI工具 | 1天 | - | 基类 |
| 实现OpenTripMap工具 | 1天 | - | 基类 |
| 更新ImmersiveDesigner | 1天 | - | API工具 |
| 更新ExplorationDesigner | 1天 | - | API工具 |
| 更新RelaxationDesigner | 1天 | - | API工具 |
| 更新HiddenGemDesigner | 1天 | - | API工具 |
| 测试和调试 | 1天 | - | 全部 |
| **总计** | **7.5天** | | |

---

## 改进计划 3: 增加智能体之间的通信机制

### 3.1 当前状态分析

**现状**:
```python
# 当前: 智能体之间无直接通信
# Group A的结果通过返回值传递给API
# API再调用Group B，传入Group A的结果
# Group B的结果再传给Group C

# 数据流:
用户 → API → Group A → API → Group B → API → Group C → API → 用户
```

**问题**:
- ❌ Group B无法直接向Group A请求更多信息
- ❌ Group C无法与Group B协商调整方案
- ❌ 智能体之间没有反馈循环
- ❌ 缺少协商、辩论、投票等协作机制

### 3.2 目标状态

**智能体通信机制**:
```python
# 目标: 智能体之间可以直接通信

# 1. 智能体可以主动发送消息
await agent.send_message(to="OtherAgent", content={...})

# 2. 智能体可以订阅特定主题的消息
agent.subscribe("destination_selection", handler)

# 3. 智能体可以发起协商/投票
result = await agent.negotiate(
    participants=["AgentA", "AgentB", "AgentC"],
    topic="选择最佳方案",
    proposal=proposal
)

# 4. 智能体可以请求其他智能体的服务
info = await agent.request_service(
    from="DestinationMatcher",
    service="get_attraction_details",
    params={"attraction_id": "123"}
)
```

### 3.3 实现方案

#### 方案1: 基于主题的发布订阅机制

```python
# tradingagents/agents/communication/pubsub.py

from typing import Dict, List, Callable, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
import asyncio

@dataclass
class Message:
    id: str
    topic: str
    sender: str
    content: Any
    timestamp: datetime
    reply_to: str = None

class PubSub:
    """发布订阅系统"""

    def __init__(self):
        self._subscribers: Dict[str, Set[Callable]] = {}
        self._message_history: List[Message] = []
        self._message_queue = asyncio.Queue()

    def subscribe(self, topic: str, handler: Callable):
        """订阅主题"""
        if topic not in self._subscribers:
            self._subscribers[topic] = set()
        self._subscribers[topic].add(handler)

    def unsubscribe(self, topic: str, handler: Callable):
        """取消订阅"""
        if topic in self._subscribers:
            self._subscribers[topic].discard(handler)

    async def publish(self, topic: str, sender: str, content: Any, reply_to: str = None):
        """发布消息到主题"""
        message = Message(
            id=str(uuid.uuid4()),
            topic=topic,
            sender=sender,
            content=content,
            timestamp=datetime.now(),
            reply_to=reply_to
        )

        self._message_history.append(message)
        await self._message_queue.put(message)

        # 立即通知订阅者
        if topic in self._subscribers:
            tasks = [handler(message) for handler in self._subscribers[topic]]
            await asyncio.gather(*tasks, return_exceptions=True)

    async def get_messages_by_topic(self, topic: str, limit: int = 10):
        """获取主题的历史消息"""
        topic_messages = [m for m in self._message_history if m.topic == topic]
        return topic_messages[-limit:]

# 全局发布订阅实例
pubsub = PubSub()

# 主题定义
class Topics:
    # 用户相关
    USER_REQUIREMENTS = "user.requirements"
    USER_PORTRAIT_READY = "user.portrait.ready"

    # 目的地相关
    DESTINATION_MATCHING = "destination.matching"
    DESTINATION_SELECTED = "destination.selected"
    ATTRACTION_SEARCH = "attraction.search"
    ATTRACTION_FOUND = "attraction.found"

    # 方案相关
    STYLE_PROPOSAL_READY = "style.proposal.ready"
    PROPOSAL_COMPARISON = "proposal.comparison"

    # 协作相关
    NEGOTIATION_REQUEST = "negotiation.request"
    NEGOTIATION_RESPONSE = "negotiation.response"
    VOTING_REQUEST = "voting.request"
    VOTING_RESULT = "voting.result"

    # 反馈相关
    FEEDBACK_REQUEST = "feedback.request"
    FEEDBACK_RESPONSE = "feedback.response"
    IMPROVEMENT_SUGGESTION = "improvement.suggestion"
```

#### 方案2: 智能体服务注册与发现

```python
# tradingagents/agents/communication/service_registry.py

from typing import Dict, Callable, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger('travel_agents')

@dataclass
class ServiceInfo:
    agent_id: str
    service_name: str
    description: str
    handler: Callable
    schema: Dict  # 参数schema

class ServiceRegistry:
    """智能体服务注册中心"""

    def __init__(self):
        self._services: Dict[str, Dict[str, ServiceInfo]] = {}
        # 结构: {agent_id: {service_name: ServiceInfo}}

    def register_service(
        self,
        agent_id: str,
        service_name: str,
        description: str,
        handler: Callable,
        schema: Dict = None
    ):
        """注册服务"""
        if agent_id not in self._services:
            self._services[agent_id] = {}

        self._services[agent_id][service_name] = ServiceInfo(
            agent_id=agent_id,
            service_name=service_name,
            description=description,
            handler=handler,
            schema=schema or {}
        )

        logger.info(f"[服务注册] {agent_id} 注册服务: {service_name}")

    def unregister_service(self, agent_id: str, service_name: str):
        """注销服务"""
        if agent_id in self._services and service_name in self._services[agent_id]:
            del self._services[agent_id][service_name]
            logger.info(f"[服务注销] {agent_id} 注销服务: {service_name}")

    async def call_service(
        self,
        agent_id: str,
        service_name: str,
        params: Dict = None
    ) -> Any:
        """调用服务"""
        if agent_id not in self._services:
            raise ValueError(f"智能体不存在: {agent_id}")

        if service_name not in self._services[agent_id]:
            raise ValueError(f"服务不存在: {agent_id}.{service_name}")

        service_info = self._services[agent_id][service_name]

        logger.info(f"[服务调用] {agent_id}.{service_name}({params})")

        try:
            result = await service_info.handler(params or {})
            return result
        except Exception as e:
            logger.error(f"[服务调用失败] {e}")
            raise

    def list_services(self, agent_id: str = None) -> Dict:
        """列出服务"""
        if agent_id:
            return {
                name: {
                    "description": info.description,
                    "schema": info.schema
                }
                for name, info in self._services[agent_id].items()
            }
        return {
            agent_id: {
                name: {
                    "description": info.description,
                    "schema": info.schema
                }
                for name, info in services.items()
            }
            for agent_id, services in self._services.items()
        }

# 全局服务注册中心
service_registry = ServiceRegistry()
```

#### 方案3: 协商和投票机制

```python
# tradingagents/agents/communication/negotiation.py

from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging

logger = logging.getLogger('travel_agents')

class NegotiationStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AGREED = "agreed"
    REJECTED = "rejected"
    TIMEOUT = "timeout"

@dataclass
class Proposal:
    id: str
    proposer: str
    topic: str
    content: Any
    rationale: str  # 提议理由
    expires_at: datetime = None

@dataclass
class NegotiationRound:
    proposal: Proposal
    participants: List[str]
    responses: Dict[str, Any]  # agent_id -> response
    status: NegotiationStatus
    started_at: datetime
    concluded_at: datetime = None

class NegotiationManager:
    """协商管理器"""

    def __init__(self, pubsub, service_registry):
        self.pubsub = pubsub
        self.service_registry = service_registry
        self._active_negotiations: Dict[str, NegotiationRound] = {}

    async def initiate_negotiation(
        self,
        proposer: str,
        topic: str,
        content: Any,
        participants: List[str],
        rationale: str = "",
        timeout: int = 60
    ) -> str:
        """发起协商"""
        proposal_id = str(uuid.uuid4())

        proposal = Proposal(
            id=proposal_id,
            proposer=proposer,
            topic=topic,
            content=content,
            rationale=rationale,
            expires_at=datetime.now() + timedelta(seconds=timeout)
        )

        round = NegotiationRound(
            proposal=proposal,
            participants=participants,
            responses={},
            status=NegotiationStatus.PENDING,
            started_at=datetime.now()
        )

        self._active_negotiations[proposal_id] = round

        # 发布协商请求
        await self.pubsub.publish(
            Topics.NEGOTIATION_REQUEST,
            proposer,
            {
                "proposal_id": proposal_id,
                "topic": topic,
                "content": content,
                "rationale": rationale,
                "participants": participants
            }
        )

        logger.info(f"[协商] {proposer} 发起协商 {topic}: {proposal_id}")

        # 等待响应
        try:
            await asyncio.wait_for(
                self._wait_for_responses(proposal_id, participants),
                timeout=timeout
            )
            round.status = NegotiationStatus.AGREED
        except asyncio.TimeoutError:
            round.status = NegotiationStatus.TIMEOUT
            logger.warning(f"[协商] {proposal_id} 超时")
        finally:
            round.concluded_at = datetime.now()

        return proposal_id

    async def respond_to_negotiation(
        self,
        proposal_id: str,
        responder: str,
        response: Any
    ):
        """响应协商"""
        if proposal_id not in self._active_negotiations:
            logger.warning(f"[协商] 未知协商ID: {proposal_id}")
            return

        round = self._active_negotiations[proposal_id]
        round.responses[responder] = response

        logger.info(f"[协商] {responder} 响应 {proposal_id}")

        # 发布响应
        await self.pubsub.publish(
            Topics.NEGOTIATION_RESPONSE,
            responder,
            {
                "proposal_id": proposal_id,
                "responder": responder,
                "response": response
            }
        )

    async def _wait_for_responses(self, proposal_id: str, participants: List[str]):
        """等待所有参与者响应"""
        while True:
            round = self._active_negotiations.get(proposal_id)
            if not round:
                raise ValueError(f"协商不存在: {proposal_id}")

            # 检查是否所有参与者都响应了
            responded = set(round.responses.keys())
            participants_set = set(participants)

            if responded >= participants_set:
                break

            await asyncio.sleep(0.5)

class VotingManager:
    """投票管理器"""

    def __init__(self, pubsub):
        self.pubsub = pubsub
        self._active_votes: Dict[str, Dict] = {}

    async def initiate_vote(
        self,
        initiator: str,
        topic: str,
        options: List[Any],
        participants: List[str],
        timeout: int = 30
    ) -> str:
        """发起投票"""
        vote_id = str(uuid.uuid4())

        vote_data = {
            "vote_id": vote_id,
            "initiator": initiator,
            "topic": topic,
            "options": options,
            "participants": participants,
            "votes": {},
            "status": "active",
            "started_at": datetime.now().isoformat()
        }

        self._active_votes[vote_id] = vote_data

        # 发布投票请求
        await self.pubsub.publish(
            Topics.VOTING_REQUEST,
            initiator,
            vote_data
        )

        logger.info(f"[投票] {initiator} 发起投票 {topic}: {vote_id}")

        # 等待投票结果
        try:
            await asyncio.wait_for(
                self._wait_for_votes(vote_id, participants),
                timeout=timeout
            )
            result = self._tally_votes(vote_id)
            vote_data["status"] = "completed"
            vote_data["result"] = result

            # 发布结果
            await self.pubsub.publish(
                Topics.VOTING_RESULT,
                "voting_manager",
                {
                    "vote_id": vote_id,
                    "result": result
                }
            )

            return result

        except asyncio.TimeoutError:
            vote_data["status"] = "timeout"
            logger.warning(f"[投票] {vote_id} 超时")
            return None

    async def cast_vote(self, vote_id: str, voter: str, choice: Any):
        """投票"""
        if vote_id not in self._active_votes:
            return

        vote_data = self._active_votes[vote_id]
        vote_data["votes"][voter] = choice

        logger.info(f"[投票] {voter} 对 {vote_id} 投票: {choice}")

    async def _wait_for_votes(self, vote_id: str, participants: List[str]):
        """等待所有参与者投票"""
        while True:
            vote_data = self._active_votes.get(vote_id)
            if not vote_data:
                raise ValueError(f"投票不存在: {vote_id}")

            voted = set(vote_data["votes"].keys())
            participants_set = set(participants)

            if voted >= participants_set:
                break

            await asyncio.sleep(0.5)

    def _tally_votes(self, vote_id: str) -> Dict:
        """统计投票结果"""
        vote_data = self._active_votes[vote_id]
        votes = list(vote_data["votes"].values())

        from collections import Counter
        counter = Counter(votes)

        return {
            "winner": counter.most_common(1)[0][0],
            "counts": dict(counter),
            "total_votes": len(votes)
        }
```

#### 方案4: 智能体通信能力集成

```python
# tradingagents/agents/communication/communicative_agent.py

class CommunicativeAgent:
    """具有通信能力的智能体基类"""

    def __init__(self, agent_id: str, llm=None):
        self.agent_id = agent_id
        self.llm = llm

        # 订阅主题
        pubsub.subscribe(f"agent.{self.agent_id}", self._handle_direct_message)
        pubsub.subscribe("broadcast", self._handle_broadcast)

        # 注册服务
        self._register_services()

    def _register_services(self):
        """子类实现服务注册"""
        pass

    async def _handle_direct_message(self, message: Message):
        """处理直接消息"""
        if message.topic == f"agent.{self.agent_id}":
            # 处理发送给这个智能体的消息
            await self.process_message(message.content)

    async def _handle_broadcast(self, message: Message):
        """处理广播消息"""
        if message.sender != self.agent_id:  # 不处理自己发送的消息
            await self.process_broadcast(message.topic, message.content)

    async def process_message(self, content: Any):
        """处理消息 - 子类实现"""
        pass

    async def process_broadcast(self, topic: str, content: Any):
        """处理广播 - 子类实现"""
        pass

    async def send_message(self, to: str, content: Any):
        """发送消息给其他智能体"""
        await pubsub.publish(f"agent.{to}", self.agent_id, content)

    async def broadcast(self, topic: str, content: Any):
        """广播消息"""
        await pubsub.publish(topic, self.agent_id, content)

    async def request_service(
        self,
        from_agent: str,
        service: str,
        params: Dict = None
    ) -> Any:
        """请求其他智能体的服务"""
        return await service_registry.call_service(from_agent, service, params)

    async def participate_in_negotiation(
        self,
        proposal_id: str,
        response: Any
    ):
        """参与协商"""
        await negotiation_manager.respond_to_negotiation(
            proposal_id,
            self.agent_id,
            response
        )

    async def cast_vote(self, vote_id: str, choice: Any):
        """投票"""
        await voting_manager.cast_vote(vote_id, self.agent_id, choice)
```

### 3.4 实际应用示例

**示例1: Group C向Group B请求更多信息**

```python
# tradingagents/agents/group_c/transport_planner_enhanced.py

class TransportPlannerAgent(CommunicativeAgent):
    """交通规划智能体 (增强版)"""

    def __init__(self, llm=None):
        super().__init__("TransportPlanner", llm)

    async def plan_transport(
        self,
        destination: str,
        scheduled_attractions: List[Dict],
        budget_level: str
    ) -> Dict[str, Any]:
        """规划交通路线"""

        # 发现某些景点坐标缺失
        missing_coords = [
            a for a in scheduled_attractions
            if not a.get("coordinates")
        ]

        if missing_coords:
            # 向ExplorationDesigner请求坐标信息
            logger.info(f"[交通规划师] 发现 {len(missing_coords)} 个景点缺少坐标，请求补充")

            for attraction in missing_coords:
                try:
                    coords = await self.request_service(
                        from_agent="ExplorationDesigner",
                        service="get_attraction_coordinates",
                        params={"attraction_name": attraction["name"]}
                    )

                    if coords:
                        attraction["coordinates"] = coords

                except Exception as e:
                    logger.warning(f"[交通规划师] 获取坐标失败: {e}")

        # 继续规划...
```

**示例2: 智能体协商调整方案**

```python
# tradingagents/agents/group_c/coordinator.py

class StyleNegotiator(CommunicativeAgent):
    """风格协商智能体"""

    async def negotiate_style_adjustment(
        self,
        destination: str,
        proposals: Dict[str, Dict],
        user_preferences: Dict
    ):
        """协商风格方案调整"""

        # 发起协商
        proposal_id = await negotiation_manager.initiate_negotiation(
            proposer=self.agent_id,
            topic="style_proposal_adjustment",
            content={
                "destination": destination,
                "proposals": proposals,
                "user_preferences": user_preferences
            },
            participants=["ImmersiveDesigner", "ExplorationDesigner", "RelaxationDesigner"],
            rationale="用户反馈希望平衡深度体验和景点数量，请各位设计师调整方案"
        )

        # 等待响应
        await asyncio.sleep(5)  # 给其他智能体时间响应

        # 获取调整后的方案
        adjusted_proposals = {}
        for designer_id in ["ImmersiveDesigner", "ExplorationDesigner", "RelaxationDesigner"]:
            try:
                adjusted = await self.request_service(
                    from_agent=designer_id,
                    service="get_adjusted_proposal",
                    params={"original_proposal": proposals[designer_id]}
                )
                adjusted_proposals[designer_id] = adjusted
            except Exception as e:
                logger.warning(f"[协商] 获取 {designer_id} 调整方案失败: {e}")

        return adjusted_proposals
```

### 3.5 实现时间表

| 任务 | 工作量 | 依赖 |
|------|--------|------|
| 实现PubSub系统 | 1天 | - |
| 实现ServiceRegistry | 1天 | - |
| 实现NegotiationManager | 2天 | PubSub |
| 实现VotingManager | 1天 | PubSub |
| 创建CommunicativeAgent基类 | 1天 | 上述全部 |
| 更新Group A智能体 | 1天 | 基类 |
| 更新Group B智能体 | 2天 | 基类 |
| 更新Group C智能体 | 2天 | 基类 |
| 测试和调试 | 2天 | 全部 |
| **总计** | **13天** | |

---

## 总体实施路线图

### 阶段划分

```
阶段1: 基础设施准备 (1-2周)
├── 实现消息总线/发布订阅系统
├── 实现服务注册中心
├── 创建通信智能体基类
└── 编写单元测试

阶段2: Group B API加强 (1周)
├── 实现API工具基类
├── 实现SerpAPI工具
├── 实现OpenTripMap工具
└── 更新所有Designer智能体

阶段3: 消息传递协作 (2-3周)
├── 更新Group A为消息模式
├── 更新Group B为消息模式
├── 更新Group C为消息模式
└── 实现协商和投票机制

阶段4: 测试和优化 (1周)
├── 端到端测试
├── 性能优化
└── 文档编写

总计: 5-7周
```

### 优先级建议

**高优先级 (立即开始)**:
1. ✅ Group B API加强 - 影响数据质量，1周可完成
2. ✅ 消息总线基础架构 - 为后续改造做准备

**中优先级 (阶段2开始)**:
1. ⚠️ 简单的通信机制 (PubSub) - 1-2周
2. ⚠️ 服务注册和调用 - 1周

**低优先级 (可选)**:
1. 📋 完整的协商/投票机制 - 根据需求决定
2. 📋 分布式部署支持 - 长期规划

---

## 总结

这三个改进计划将显著提升系统的多智能体特性：

1. **消息传递协作**: 使系统更符合真正的多智能体理念
2. **API工具加强**: 提升数据质量和方案真实性
3. **通信机制**: 增强智能体之间的协作能力

建议按优先级逐步实施，先完成Group B API加强（1周），再根据需求决定是否进行大规模架构改造。
