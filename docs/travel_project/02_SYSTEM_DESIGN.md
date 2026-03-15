# TravelAgents-CN 系统设计文档

## 📋 文档信息

| 项目 | 信息 |
|------|------|
| 项目名称 | TravelAgents-CN 智能旅行规划系统 |
| 版本 | v1.0 |
| 创建日期 | 2025-03-10 |
| 文档类型 | 系统设计说明书 |
| 依赖文档 | 01_REQUIREMENTS_ANALYSIS.md |

---

## 1. 系统架构概览

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                           用户界面层                               │
│                      (FastAPI + Vue前端)                          │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                         多Agent编排层                              │
│                          (LangGraph)                              │
├─────────────────────────────────────────────────────────────────┤
│  用户分析Agent → 地区推荐Agent → 方案生成Agent → 行程规划Agent      │
│       ↓              ↓              ↓              ↓              │
│  实用信息Agent → 评估对比Agent → 最终输出Agent                      │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                          工具层                                   │
├─────────────────────────────────────────────────────────────────┤
│  SerpAPI | Open-Meteo | Exchange API | 演示数据库                │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                        LLM层                                      │
│                      (SiliconFlow API)                           │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 核心设计原则

| 原则 | 说明 |
|------|------|
| **渐进式** | 从简单开始，逐步增加复杂度 |
| **可降级** | 实时API失败时使用演示数据 |
| **可扩展** | 易于添加新国家和功能 |
| **可维护** | 清晰的代码结构和文档 |

---

## 2. Agent架构设计

### 2.1 Agent列表与职责

```
┌─────────────────────────────────────────────────────────────────┐
│                    旅行规划多Agent系统                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Agent 1: 用户需求分析器 (UserAnalyzer)                          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  职责：理解用户需求，构建用户旅行画像                               │
│  输入：原始用户输入                                                │
│  输出：结构化用户需求 + 用户旅行画像                                │
│  工具：无                                                         │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│  Agent 2: 目的地区发现器 (RegionDiscoverer)                      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  职责：发现目的地国家的主要旅游地区                                 │
│  输入：国家 + 用户偏好                                             │
│  输出：推荐地区列表（3-5个）                                       │
│  工具：地区数据库                                                 │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│  Agent 3: 方案生成器 (ProposalGenerator)                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  职责：生成2-3个不同风格的旅行方案                                 │
│  输入：用户选择的地区 + 用户需求                                   │
│  输出：方案A、方案B、方案C                                        │
│  工具：景点数据库、SerpAPI                                       │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│  Agent 4: 行程规划师 (ItineraryPlanner)                          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  职责：为选定方案生成详细行程                                      │
│  输入：选定的方案 + 用户需求                                       │
│  输出：每日详细行程（景点+交通+住宿+餐饮）                          │
│  工具：景点数据库、SerpAPI、天气API                              │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│  Agent 5: 预算分析师 (BudgetAnalyst)                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  职责：计算旅行费用，提供预算分析                                  │
│  输入：行程 + 用户预算                                             │
│  输出：费用明细 + 预算建议                                         │
│  工具：汇率API、价格数据库                                        │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│  Agent 6: 实用信息整合器 (InfoAggregator)                        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  职责：整合天气、签证、安全等实用信息                              │
│  输入：目的地 + 日期                                               │
│  输出：实用信息汇总                                               │
│  工具：天气API、签证数据库                                        │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│  Agent 7: 方案评估器 (ProposalEvaluator)                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  职责：多维度评估和对比方案                                        │
│  输入：所有方案                                                   │
│  输出：评估对比表                                                 │
│  工具：无                                                         │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│  Agent 8: 最终输出格式化器 (OutputFormatter)                      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  职责：格式化最终输出                                             │
│  输入：行程 + 预算 + 实用信息 + 评估                               │
│  输出：格式化的完整旅行方案                                        │
│  工具：无                                                         │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 State数据结构

```python
from typing import TypedDict, List, Dict, Optional
from langchain_core.messages import BaseMessage

class TravelPlanningState(TypedDict):
    """旅行规划系统的主State"""

    # ==================== 用户输入 ====================
    user_input: str                    # 原始用户输入
    destination: str                   # 目的地国家
    start_date: str                    # 出发日期 YYYY-MM-DD
    end_date: str                      # 返回日期 YYYY-MM-DD
    days: int                          # 总天数
    budget: float                      # 预算（人民币）
    travelers: int                     # 旅行人数
    interests: List[str]               # 兴趣列表
    special_requirements: str          # 特殊需求

    # ==================== Agent 1输出：用户分析 ====================
    user_profile: Dict                 # 用户旅行画像
    # {
    #     "travel_style": "cultural",
    #     "primary_interest": "temples",
    #     "pace_preference": "moderate",
    #     "budget_level": "medium"
    # }

    # ==================== Agent 2输出：地区推荐 ====================
    available_regions: List[Dict]      # 可用地区列表
    # [
    #     {
    #         "id": "kansai",
    #         "name": "关西地区",
    #         "cities": ["Kyoto", "Osaka", "Nara"],
    #         "highlights": ["寺庙", "美食"],
    #         "match_score": 0.95,
    #         "match_reason": "非常适合您的寺庙文化兴趣"
    #     },
    #     ...
    # ]

    selected_regions: List[str]        # 用户选择的地区ID

    # ==================== Agent 3输出：方案生成 ====================
    proposals: List[Dict]              # 生成的方案列表
    # [
    #     {
    #         "id": "proposal_a",
    #         "name": "深度文化体验之旅",
    #         "type": "deep_dive",
    #         "description": "专注深度体验日本传统文化",
    #         "regions": ["kansai"],
    #         "highlights": [...],
    #         "estimated_days": {...},
    #         "estimated_budget": 12000
    #     },
    #     ...
    # ]

    selected_proposal: Optional[Dict]  # 用户选择的方案

    # ==================== Agent 4输出：详细行程 ====================
    detailed_itinerary: Optional[Dict] # 详细行程
    # {
    #     "proposal_id": "proposal_a",
    #     "daily_schedule": [
    #         {
    #             "day": 1,
    #             "location": "Kyoto",
    #             "date": "2024-12-15",
    #             "morning": {...},
    #             "afternoon": {...},
    #             "evening": {...},
    #             "accommodation": {...},
    #             "transportation": {...}
    #         },
    #         ...
    #     ],
    #     "intercity_transport": [...],
    #     "total_estimate": {...}
    # }

    # ==================== Agent 5输出：预算分析 ====================
    budget_analysis: Optional[Dict]    # 预算分析
    # {
    #     "total_estimate": 12000,
    #     "breakdown": {
    #         "flights": 3000,
    #         "accommodation": 4000,
    #         "food": 2000,
    #         "transportation": 1000,
    #         "attractions": 1000,
    #         "shopping": 1000
    #     },
    #     "budget_status": "within_budget",
    #     "tips": [...]
    # }

    # ==================== Agent 6输出：实用信息 ====================
    practical_info: Optional[Dict]     # 实用信息
    # {
    #     "weather": {...},
    #     "visa": {...},
    #     "safety": {...},
    #     "emergency_contacts": {...},
    #     "tips": [...]
    # }

    # ==================== Agent 7输出：方案评估 ====================
    proposal_evaluation: Optional[Dict] # 方案评估
    # {
    #     "comparison_table": {...},
    #     "scores": {...},
    #     "recommendation": {...}
    # }

    # ==================== Agent 8输出：最终结果 ====================
    final_output: Optional[str]        # 最终格式化输出

    # ==================== 系统字段 ====================
    current_step: str                  # 当前步骤
    next_step: str                     # 下一步
    error: Optional[str]               # 错误信息
    messages: List[BaseMessage]        # 消息历史
```

---

## 3. 工作流设计

### 3.1 主工作流

```python
from langgraph.graph import StateGraph, END

def create_travel_planning_graph():
    """创建旅行规划主图"""
    workflow = StateGraph(TravelPlanningState)

    # ========== 添加节点 ==========
    workflow.add_node("user_analyzer", user_analyzer_node)
    workflow.add_node("region_discoverer", region_discoverer_node)
    workflow.add_node("proposal_generator", proposal_generator_node)
    workflow.add_node("itinerary_planner", itinerary_planner_node)
    workflow.add_node("budget_analyst", budget_analyst_node)
    workflow.add_node("info_aggregator", info_aggregator_node)
    workflow.add_node("proposal_evaluator", proposal_evaluator_node)
    workflow.add_node("output_formatter", output_formatter_node)

    # ========== 设置入口 ==========
    workflow.set_entry_point("user_analyzer")

    # ========== 添加边 ==========
    # 线性流程
    workflow.add_edge("user_analyzer", "region_discoverer")
    workflow.add_edge("region_discoverer", "proposal_generator")
    workflow.add_edge("proposal_generator", "itinerary_planner")
    workflow.add_edge("itinerary_planner", "budget_analyst")
    workflow.add_edge("budget_analyst", "info_aggregator")
    workflow.add_edge("info_aggregator", "proposal_evaluator")
    workflow.add_edge("proposal_evaluator", "output_formatter")
    workflow.add_edge("output_formatter", END)

    return workflow.compile()
```

### 3.2 工作流图示

```
用户输入
    ↓
┌─────────────────┐
│  user_analyzer  │ → 分析用户需求，构建画像
└─────────────────┘
    ↓
┌─────────────────────┐
│ region_discoverer   │ → 发现推荐地区
└─────────────────────┘
    ↓
┌─────────────────────┐
│ proposal_generator  │ → 生成多个方案
└─────────────────────┘
    ↓
┌─────────────────────┐
│ itinerary_planner   │ → 生成详细行程
└─────────────────────┘
    ↓
┌─────────────────────┐
│  budget_analyst     │ → 预算分析
└─────────────────────┘
    ↓
┌─────────────────────┐
│  info_aggregator    │ → 实用信息整合
└─────────────────────┘
    ↓
┌─────────────────────┐
│ proposal_evaluator  │ → 方案评估对比
└─────────────────────┘
    ↓
┌─────────────────────┐
│ output_formatter    │ → 格式化输出
└─────────────────────┘
    ↓
  最终输出
```

---

## 4. 数据库设计

### 4.1 地区数据库

```python
# travelagents/data/regions_database.py

DESTINATION_REGIONS_DB = {
    "Japan": {
        "regions": [
            {
                "id": "kanto",
                "name": "关东地区",
                "name_en": "Kanto Region",
                "main_cities": [
                    {
                        "id": "tokyo",
                        "name": "东京",
                        "name_en": "Tokyo",
                        "highlight": True
                    },
                    {
                        "id": "kamakura",
                        "name": "镰仓",
                        "name_en": "Kamakura",
                        "highlight": False
                    }
                ],
                "highlights": ["现代都市", "迪士尼", "浅草寺", "秋叶原"],
                "best_for": ["shopping", "modern_culture", "anime", "food"],
                "interest_match": {
                    "temples": 0.6,
                    "food": 0.9,
                    "shopping": 1.0,
                    "modern_culture": 1.0,
                    "nature": 0.4,
                    "history": 0.6
                },
                "seasonality": {
                    "spring": {"score": 8, "reason": "樱花季"},
                    "summer": {"score": 7, "reason": "祭典多"},
                    "autumn": {"score": 8, "reason": "红叶"},
                    "winter": {"score": 7, "reason": "圣诞灯饰"}
                }
            },
            {
                "id": "kansai",
                "name": "关西地区",
                "name_en": "Kansai Region",
                "main_cities": [
                    {"id": "kyoto", "name": "京都", "highlight": True},
                    {"id": "osaka", "name": "大阪", "highlight": True},
                    {"id": "nara", "name": "奈良", "highlight": True}
                ],
                "highlights": ["古寺", "和服", "怀石料理", "奈良鹿"],
                "best_for": ["history", "temples", "traditional_culture", "food"],
                "interest_match": {
                    "temples": 1.0,
                    "food": 0.9,
                    "shopping": 0.6,
                    "modern_culture": 0.4,
                    "nature": 0.7,
                    "history": 1.0
                },
                "seasonality": {
                    "spring": {"score": 10, "reason": "樱花+古寺绝美"},
                    "summer": {"score": 6, "reason": "较热"},
                    "autumn": {"score": 9, "reason": "红叶古寺"},
                    "winter": {"score": 6, "reason": "较冷"}
                }
            },
            {
                "id": "hokkaido",
                "name": "北海道",
                "name_en": "Hokkaido",
                "main_cities": [
                    {"id": "sapporo", "name": "札幌", "highlight": True},
                    {"id": "otaru", "name": "小樽", "highlight": False},
                    {"id": "hakodate", "name": "函馆", "highlight": False}
                ],
                "highlights": ["温泉", "雪祭", "海鲜", "薰衣草"],
                "best_for": ["nature", "onsen", "food", "skiing"],
                "interest_match": {
                    "temples": 0.3,
                    "food": 0.9,
                    "shopping": 0.5,
                    "modern_culture": 0.4,
                    "nature": 1.0,
                    "history": 0.4
                },
                "seasonality": {
                    "spring": {"score": 6, "reason": "融雪期"},
                    "summer": {"score": 9, "reason": "薰衣草、避暑"},
                    "autumn": {"score": 8, "reason": "红叶"},
                    "winter": {"score": 10, "reason": "雪祭、滑雪"}
                }
            }
        ]
    },
    "Thailand": {
        "regions": [
            {
                "id": "bangkok",
                "name": "曼谷及周边",
                "name_en": "Bangkok Area",
                "main_cities": [
                    {"id": "bangkok", "name": "曼谷", "highlight": True},
                    {"id": "ayutthaya", "name": "大城", "highlight": False}
                ],
                "highlights": ["大皇宫", "水上市场", "街头美食", "购物"],
                "best_for": ["temples", "food", "shopping", "urban"],
                "interest_match": {
                    "temples": 0.9,
                    "food": 1.0,
                    "shopping": 0.9,
                    "nature": 0.3,
                    "history": 0.8
                },
                "seasonality": {
                    "winter": {"score": 10, "reason": "最佳季节"},
                    "summer": {"score": 5, "reason": "太热"},
                    "rainy": {"score": 4, "reason": "多雨"}
                }
            },
            {
                "id": "northern_thailand",
                "name": "北部泰国",
                "name_en": "Northern Thailand",
                "main_cities": [
                    {"id": "chiang_mai", "name": "清迈", "highlight": True},
                    {"id": "chiang_rai", "name": "清莱", "highlight": False},
                    {"id": "pai", "name": "拜县", "highlight": False}
                ],
                "highlights": ["寺庙", "山脉", "夜市", "大象"],
                "best_for": ["temples", "nature", "culture", "relaxation"],
                "interest_match": {
                    "temples": 0.9,
                    "food": 0.7,
                    "nature": 1.0,
                    "history": 0.7
                },
                "seasonality": {
                    "winter": {"score": 9, "reason": "凉爽舒适"},
                    "summer": {"score": 6, "reason": "有点热"},
                    "rainy": {"score": 5, "reason": "多雨"}
                }
            },
            {
                "id": "southern_thailand",
                "name": "南部泰国（海岛）",
                "name_en": "Southern Thailand",
                "main_cities": [
                    {"id": "phuket", "name": "普吉岛", "highlight": True},
                    {"id": "krabi", "name": "甲米", "highlight": True},
                    {"id": "koh_samui", "name": "苏梅岛", "highlight": True}
                ],
                "highlights": ["海滩", "潜水", "跳岛游", "日落"],
                "best_for": ["beach", "diving", "relaxation", "nature"],
                "interest_match": {
                    "food": 0.6,
                    "nature": 1.0,
                    "temples": 0.2
                },
                "seasonality": {
                    "winter": {"score": 10, "reason": "最佳季节"},
                    "summer": {"score": 7, "reason": "可以但热"},
                    "rainy": {"score": 3, "reason": "雨季不适合海岛"}
                }
            }
        ]
    }
    # ... 更多国家
}
```

### 4.2 景点数据库结构

```python
# travelagents/data/attractions_database.py

ATTRACTIONS_DB = {
    "kyoto": {
        "temples": [
            {
                "id": "kinkakuji",
                "name": "金阁寺",
                "name_en": "Kinkaku-ji",
                "description": "日本最著名的寺庙之一，覆盖金箔的楼阁倒映在湖面上",
                "rating": 4.5,
                "visit_duration": "1-1.5小时",
                "admission": 400,
                "best_time": "早晨开门时",
                "tips": "人很多，建议早去",
                "interest_tags": ["temples", "history", "architecture"]
            },
            {
                "id": "kiyomizudera",
                "name": "清水寺",
                "name_en": "Kiyomizu-dera",
                "description": "世界遗产，以木制舞台和樱花/红叶闻名",
                "rating": 4.7,
                "visit_duration": "2小时",
                "admission": 400,
                "best_time": "樱花季或红叶季",
                "tips": "可以和二年坂三年坂一起游览",
                "interest_tags": ["temples", "history", "views"]
            }
        ],
        "food": [
            {
                "id": "nishiki_market",
                "name": "锦市场",
                "name_en": "Nishiki Market",
                "description": "京都的厨房，400年历史的食品市场",
                "rating": 4.3,
                "visit_duration": "1-2小时",
                "admission": 0,
                "must_try": ["豆腐料理", "和果子", "抹茶"],
                "interest_tags": ["food", "shopping", "culture"]
            }
        ]
    }
}
```

---

## 5. API接口设计

### 5.1 后端API

```python
# app/routers/travel.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/travel", tags=["travel"])

class TravelRequest(BaseModel):
    """旅行规划请求"""
    destination: str
    start_date: str
    end_date: str
    budget: float
    travelers: int
    interests: List[str]
    special_requirements: Optional[str] = None

class TravelResponse(BaseModel):
    """旅行规划响应"""
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None

@router.post("/plan", response_model=TravelResponse)
async def plan_travel(request: TravelRequest):
    """
    生成旅行规划

    流程：
    1. 接收用户需求
    2. 调用多Agent系统
    3. 返回规划结果
    """
    try:
        result = await travel_service.plan_trip(
            destination=request.destination,
            start_date=request.start_date,
            end_date=request.end_date,
            budget=request.budget,
            travelers=request.travelers,
            interests=request.interests,
            special_requirements=request.special_requirements
        )

        return TravelResponse(success=True, data=result)

    except Exception as e:
        return TravelResponse(success=False, message=str(e))

@router.get("/regions/{country}")
async def get_country_regions(country: str):
    """获取国家的所有地区"""
    regions = region_service.get_regions(country)
    return {"regions": regions}

@router.get("/attractions/{city}")
async def get_city_attractions(city: str, interest: Optional[str] = None):
    """获取城市景点"""
    attractions = attraction_service.get_attractions(city, interest)
    return {"attractions": attractions}
```

### 5.2 前端调用

```typescript
// frontend/src/api/travel.ts

export interface TravelRequest {
  destination: string;
  startDate: string;
  endDate: string;
  budget: number;
  travelers: number;
  interests: string[];
  specialRequirements?: string;
}

export interface TravelResponse {
  success: boolean;
  data?: any;
  message?: string;
}

export async function planTravel(request: TravelRequest): Promise<TravelResponse> {
  const response = await fetch('/api/travel/plan', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });
  return response.json();
}
```

---

## 6. 实施计划

### 6.1 阶段1：基础框架（第1周）

**目标**：搭建可运行的基础框架

- [x] 创建项目需求文档
- [ ] 创建State定义
- [ ] 创建基础Graph结构
- [ ] 实现用户分析Agent
- [ ] 实现地区发现Agent
- [ ] 集成地区数据库（日本、泰国）

**验收标准**：
- 可以输入用户需求
- 可以返回推荐地区列表

### 6.2 阶段2：方案生成（第2周）

**目标**：实现方案生成和行程规划

- [ ] 实现方案生成Agent
- [ ] 实现行程规划Agent
- [ ] 集成景点数据库
- [ ] 集成SerpAPI实时数据
- [ ] 实现预算分析Agent

**验收标准**：
- 可以生成2-3个不同方案
- 可以为方案生成详细行程
- 可以计算预算

### 6.3 阶段3：完善优化（第3周）

**目标**：完成所有功能，优化体验

- [ ] 实现实用信息整合Agent
- [ ] 实现方案评估Agent
- [ ] 优化输出格式
- [ ] 添加更多国家数据
- [ ] 测试和修复bug

**验收标准**：
- 所有8个Agent正常工作
- 支持至少5个国家
- 输出格式美观易读

---

## 7. 技术栈总结

| 层级 | 技术 | 说明 |
|------|------|------|
| **LLM** | SiliconFlow API | DeepSeek-V3 |
| **Agent框架** | LangGraph | 多Agent编排 |
| **后端** | FastAPI | 原项目已有 |
| **前端** | Vue 3 + Element Plus | 原项目已有 |
| **数据库** | 演示数据库 | Python字典 |
| **实时数据** | SerpAPI, Open-Meteo | 外部API |

---

## 8. 风险与应对

| 风险 | 应对措施 |
|------|---------|
| LLM调用失败 | 降级到规则引擎 |
| API额度耗尽 | 使用演示数据 |
| 数据覆盖不足 | 优先支持热门国家 |
| 时间不够 | 分阶段交付 |

---

## 9. 附录

### 9.1 兴趣标签映射

```python
INTEREST_TAGS = {
    "temples": ["寺庙", "古迹", "历史建筑", "religion", "temples", "shrines"],
    "food": ["美食", "小吃", "餐厅", "food", "dining", "cuisine"],
    "shopping": ["购物", "商场", "shopping", "mall"],
    "nature": ["自然", "风景", "公园", "nature", "scenery"],
    "beach": ["海滩", "海岛", "beach", "island"],
    "modern_culture": ["现代文化", "动漫", "流行文化"],
    "history": ["历史", "文化", "history", "culture"],
    "art": ["艺术", "博物馆", "art", "museum", "gallery"],
    "nightlife": ["夜生活", "酒吧", "nightlife"],
    "adventure": ["冒险", "户外", "adventure", "outdoor"]
}
```

### 9.2 季节映射

```python
SEASON_MAP = {
    "spring": ["03", "04", "05"],
    "summer": ["06", "07", "08"],
    "autumn": ["09", "10", "11"],
    "winter": ["12", "01", "02"]
}

def get_season(date_str: str) -> str:
    """从日期获取季节"""
    month = int(date_str.split("-")[1])
    if month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "autumn"
    else:
        return "winter"
```

---

## 变更记录

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| v1.0 | 2025-03-10 | 初始版本 | Claude |
