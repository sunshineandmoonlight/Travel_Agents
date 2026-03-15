# 多智能体系统详解

## 什么是多智能体系统？

多智能体系统（Multi-Agent System）是由多个智能Agent组成的协作系统，每个Agent负责特定的任务，通过协作完成复杂的旅行规划。

## 系统架构

```
                    用户需求
                       ↓
              ┌─────────────────┐
              │  目的地分类器    │
              └────────┬─────────┘
                       ↓
              ┌─────────────────┐
              │   数据收集器     │
              └────────┬─────────┘
                       ↓
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
┌───────────┐  ┌───────────┐  ┌───────────┐
│景点分析师  │  │行程规划师  │  │预算分析师  │
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘
      └──────────────┼──────────────┘
                     ↓
              ┌─────────────────┐
              │   完整旅行攻略   │
              └─────────────────┘
```

## 各Agent详细介绍

### 1. 目的地分类器 (DestinationClassifier)

**职责**：识别目的地类型，决定使用哪些数据源

**工作流程**：
```python
输入: "杭州"
  ↓
判断: 国内城市 → 使用高德地图API
  ↓
输出: {
    "destination": "杭州",
    "type": "domestic",
    "region": "华东地区"
}
```

**关键能力**：
- 识别国内/国际目的地
- 自动选择合适的地图API
- 提供目的地基本信息

### 2. 数据收集器 (DataCollector)

**职责**：收集旅行规划所需的各种数据

**收集内容**：
- **景点数据**：名称、描述、评分、位置
- **天气数据**：当前天气、未来预报
- **交通数据**：高铁、飞机、自驾路线
- **住宿数据**：酒店、民宿信息

**数据源切换**：
```
国内目的地 → 高德地图API
国际目的地 → SerpAPI / Google Places
```

### 3. 景点分析师 (AttractionAnalyst)

**职责**：根据用户兴趣筛选和推荐景点

**分析维度**：
- 兴趣匹配度（自然、历史、美食等）
- 景点评分和口碑
- 游览时间估算
- 最佳游览时间建议

**示例分析报告**：
```markdown
# 景点分析报告

## 推荐景点：西湖风景区
- **匹配度**：95%
- **推荐理由**：符合自然兴趣偏好
- **建议游览时间**：4-6小时
- **最佳时间**：上午9点开始，避开人流高峰
```

### 4. 行程规划师 (ItineraryPlanner)

**职责**：合理安排每日行程

**规划原则**：
1. **时间合理**：不赶时间，也不浪费时间
2. **地理位置**：相近景点安排在同一天
3. **劳逸结合**：避免过度疲劳
4. **餐饮安排**：合理分配用餐时间
5. **弹性时间**：留出休息和意外时间

**每日行程结构**：
```
第X天：[主题名称]
- 上午 (09:00-12:00)：[活动]
- 午餐 (12:00-13:30)：[餐厅/建议]
- 下午 (14:00-17:00)：[活动]
- 晚餐 (18:00-20:00)：[餐厅/建议]
- 晚上 (20:00-22:00)：[活动]
```

### 5. 预算分析师 (BudgetAnalyst)

**职责**：计算旅行费用并提供省钱建议

**预算构成**：
```
总预算 = 交通 + 住宿 + 餐饮 + 景点 + 其他
```

**分析输出**：
- 费用明细表
- 日均费用
- 人均费用
- 省钱建议
- 预算调整方案

## Agent协作示例

让我们看看Agent们如何协作完成一个"杭州3日游"的规划：

```
[T=0ms] 用户输入: "杭州3天，喜欢自然，预算中等"

[T=15ms] 目的地分类器:
  → 识别为国内目的地
  → 选择高德地图API

[T=850ms] 数据收集器:
  → 找到15个景点
  → 获取7天天气预报
  → 收集交通信息

[T=3500ms] 景点分析师:
  → 筛选出8个符合"自然"兴趣的景点
  → 西湖、灵隐寺、千岛湖等...

[T=4200ms] 行程规划师:
  → 第1天：西湖经典游
  → 第2天：佛教文化与自然
  → 第3天：千岛湖游

[T=2800ms] 预算分析师:
  → 总预算：2,060元
  → 日均：687元/人

[T=10365ms] 完成规划，生成攻略！
```

## 技术实现

### LangGraph框架

系统使用LangGraph框架实现多智能体编排：

```python
from langgraph.graph import StateGraph

# 创建状态图
graph = StateGraph(AgentState)

# 添加节点（Agent）
graph.add_node("classifier", destination_classifier_node)
graph.add_node("collector", data_collector_node)
graph.add_node("attraction_analyst", attraction_analyst_node)
graph.add_node("planner", itinerary_planner_node)
graph.add_node("budget_analyst", budget_analyst_node)

# 定义执行流程
graph.add_edge("classifier", "collector")
graph.add_edge("collector", "attraction_analyst")
graph.add_edge("attraction_analyst", "planner")
graph.add_edge("planner", "budget_analyst")

# 编译图
travel_graph = graph.compile()
```

### 状态管理

每个Agent通过共享状态传递信息：

```python
class AgentState(TypedDict):
    # 输入
    destination: str
    days: int
    interest_type: str
    budget: str

    # 中间状态
    destination_type: str
    attractions: List[Dict]
    weather_data: Dict

    # 输出
    itinerary: Dict
    budget_breakdown: Dict
```

## 分析报告

每个Agent执行完成后都会生成详细的分析报告，包含：

1. **分析概述**
2. **详细结果**
3. **推荐理由**
4. **执行时间**

这些报告对用户透明，让AI决策过程可见。

## 扩展性

系统可以轻松添加新的Agent：

```python
# 添加美食推荐Agent
graph.add_node("food_analyst", food_analyst_node)
graph.add_edge("attraction_analyst", "food_analyst")

# 添加住宿推荐Agent
graph.add_node("accommodation_analyst", accommodation_analyst_node)
```

## 总结

多智能体系统是AI旅行规划的核心，它通过：
- **专业化分工**：每个Agent专注自己的领域
- **智能协作**：Agent之间共享信息和决策
- **透明决策**：生成详细的分析报告

为用户提供高质量、个性化的旅行规划服务。

## 相关阅读

- [景点分析师工作原理](../03-agent-system/attraction-analyst.md)
- [行程规划师详解](../03-agent-system/itinerary-planner.md)
- [查看实际分析报告](/travel/plan?id=example)

---

**预计阅读时间**：15分钟
**最后更新**：2026年3月
**难度等级**：中级
