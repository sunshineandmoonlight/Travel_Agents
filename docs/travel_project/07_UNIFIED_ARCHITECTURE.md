# TravelAgents-CN 国内+国际统一架构设计

## 📋 文档信息

| 项目 | 信息 |
|------|------|
| 项目名称 | TravelAgents-CN 国内+国际统一架构 |
| 版本 | v3.0 |
| 创建日期 | 2025-03-10 |
| 文档类型 | 系统架构设计 |

---

## 🎯 设计目标

### 核心目标
设计一个**统一的旅行规划系统**，能够：
1. 自动识别目的地类型（国内/国际）
2. 无缝切换不同的API和数据源
3. 提供一致的用户体验
4. 易于扩展新的目的地类型

### 设计原则

| 原则 | 说明 |
|------|------|
| **统一入口** | 用户无需区分国内/国际 |
| **自动识别** | 系统自动判断目的地类型 |
| **统一接口** | 内部API调用接口一致 |
| **统一输出** | 用户看到的输出格式一致 |
| **易于扩展** | 方便添加新的目的地类型 |

---

## 🏗️ 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户交互层                                │
│                    （统一的UI和交互流程）                         │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                      目的地识别层                                 │
│                   自动判断：国内 vs 国际                          │
└─────────────────────────────────────────────────────────────────┘
                    ┌───────────────┴───────────────┐
                    ↓                               ↓
┌───────────────────────────┐   ┌───────────────────────────┐
│      国内分支                │   │      国际分支                │
│   (Domestic Branch)         │   │  (International Branch)    │
├───────────────────────────┤   ├───────────────────────────┤
│  📊 数据源                  │   │  📊 数据源                  │
│  • 高德地图 API             │   │  • SerpAPI                 │
│  • 高德天气 API             │   │  • Open-Meteo              │
│  • 国内城市数据库            │   │  • 国际国家数据库            │
│  • 高铁/火车估算             │   │  • 机票估算/Amadeus         │
│                           │   │                           │
│  🏙️ 主要城市                │   │  🌍 主要国家                │
│  • 北京、上海、西安等        │   │  • 日本、泰国、新加坡等      │
│                           │   │                           │
│  🚄 主要交通                │   │  ✈️ 主要交通                │
│  • 高铁、火车、自驾          │   │  • 飞机                    │
│                           │   │                           │
│  💰 价格特征                │   │  💰 价格特征                │
│  • 高铁二等座 0.4元/km      │   │  • 机票往返 2000-5000元     │
│  • 酒店 300-600元/晚         │   │  • 酒店 400-800元/晚        │
└───────────────────────────┘   └───────────────────────────┘
                    └───────────────┬───────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                      统一方案生成层                               │
│                   生成3种风格方案（沉浸/探索/松弛）                  │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                      统一输出层                                   │
│              （格式统一的行程、预算、实用信息）                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 核心模块设计

### 1. 目的地识别模块

```python
# travelagents/utils/destination_classifier.py

from typing import Literal, Dict
import re

class DestinationClassifier:
    """目的地分类器"""

    # 国内城市列表（300+城市）
    DOMESTIC_CITIES = {
        # 直辖市
        "北京", "上海", "天津", "重庆",
        # 省会城市
        "广州", "深圳", "成都", "杭州", "西安", "南京", "武汉", "长沙",
        "郑州", "沈阳", "大连", "青岛", "宁波", "厦门", "苏州", "无锡",
        "福州", "济南", "石家庄", "太原", "合肥", "南昌", "南宁", "海口",
        "贵阳", "昆明", "拉萨", "兰州", "西宁", "银川", "乌鲁木齐", "呼和浩特",
        "长春", "哈尔滨",
        # 热门旅游城市
        "三亚", "丽江", "大理", "桂林", "桂林", "张家界", "九寨沟", "黄山",
        "五台山", "峨眉山", "武夷山", "庐山", "敦煌", "嘉峪关", "银川",
        "延吉", "呼伦贝尔", "漠河", "伊犁", "喀什", "林芝", "日喀则",
        # 港澳台
        "香港", "澳门", "台北"
    }

    # 国际国家列表
    INTERNATIONAL_DESTINATIONS = {
        # 亚洲
        "日本", "韩国", "泰国", "新加坡", "马来西亚", "越南", "柬埔寨",
        "印尼", "菲律宾", "印度", "尼泊尔", "马尔代夫", "斯里兰卡",
        # 欧洲
        "法国", "英国", "意大利", "西班牙", "德国", "瑞士", "荷兰",
        "比利时", "奥地利", "希腊", "葡萄牙", "捷克", "匈牙利",
        # 大洋洲
        "澳大利亚", "新西兰",
        # 北美
        "美国", "加拿大", "墨西哥",
        # 其他
        "土耳其", "埃及", "南非", "阿联酋", "迪拜"
    }

    # 城市别名映射
    CITY_ALIASES = {
        "北京": ["Beijing", "PEK", "首都"],
        "上海": ["Shanghai", "SHA", "魔都"],
        "广州": ["Guangzhou", "CAN", "羊城"],
        "深圳": ["Shenzhen", "SZX"],
        "成都": ["Chengdu", "CTU", "蓉城"],
        # ... 更多
    }

    @classmethod
    def classify(cls, destination: str) -> Dict:
        """
        分类目的地

        Returns:
            {
                "type": "domestic" | "international",
                "normalized_name": "标准名称",
                "confidence": 0.9,
                "matched_by": "exact" | "alias" | "fuzzy"
            }
        """
        dest = destination.strip()

        # 1. 精确匹配 - 国内城市
        if dest in cls.DOMESTIC_CITIES:
            return {
                "type": "domestic",
                "normalized_name": dest,
                "confidence": 1.0,
                "matched_by": "exact"
            }

        # 2. 精确匹配 - 国际国家
        if dest in cls.INTERNATIONAL_DESTINATIONS:
            return {
                "type": "international",
                "normalized_name": dest,
                "confidence": 1.0,
                "matched_by": "exact"
            }

        # 3. 别名匹配
        for city_name, aliases in cls.CITY_ALIASES.items():
            if dest in aliases:
                return {
                    "type": "domestic",
                    "normalized_name": city_name,
                    "confidence": 0.9,
                    "matched_by": "alias"
                }

        # 4. 模糊匹配（包含）
        for city in cls.DOMESTIC_CITIES:
            if city in dest or dest in city:
                return {
                    "type": "domestic",
                    "normalized_name": city,
                    "confidence": 0.7,
                    "matched_by": "fuzzy"
                }

        # 5. LLM辅助判断（如果前面都没匹配）
        return cls._llm_classify(dest)

    @classmethod
    def _llm_classify(cls, destination: str) -> Dict:
        """
        使用LLM判断目的地类型

        当规则匹配失败时的降级方案
        """
        # 这里可以调用LLM来判断
        # 或者返回一个让用户确认的结果
        return {
            "type": "unknown",
            "normalized_name": destination,
            "confidence": 0.0,
            "matched_by": "unknown",
            "need_user_confirm": True
        }
```

---

### 2. 统一数据接口层

```python
# travelagents/utils/unified_data_interface.py

from abc import ABC, abstractmethod
from typing import Dict, List

class BaseTravelDataProvider(ABC):
    """旅行数据提供者基类"""

    @abstractmethod
    def search_attractions(self, location: str, interest_type: str = "") -> Dict:
        """搜索景点"""
        pass

    @abstractmethod
    def get_weather(self, location: str, days: int = 7) -> Dict:
        """获取天气"""
        pass

    @abstractmethod
    def estimate_transport_cost(self, origin: str, destination: str) -> Dict:
        """估算交通费用"""
        pass

    @abstractmethod
    def get_location_info(self, location: str) -> Dict:
        """获取地点信息"""
        pass


class DomesticDataProvider(BaseTravelDataProvider):
    """国内数据提供者"""

    def __init__(self):
        from travelagents.integrations.amap_client import AmapClient
        self.amap = AmapClient()

    def search_attractions(self, location: str, interest_type: str = "") -> Dict:
        """使用高德API搜索景点"""
        return self.amap.search_attractions(location, interest_type)

    def get_weather(self, location: str, days: int = 7) -> Dict:
        """使用高德API获取天气"""
        return self.amap.get_weather(location, days)

    def estimate_transport_cost(self, origin: str, destination: str) -> Dict:
        """估算国内交通费用（高铁/火车）"""
        # 城市距离表
        distance_map = {
            ("北京", "上海"): 1200,
            ("北京", "西安"): 1000,
            ("上海", "杭州"): 180,
            # ... 更多
        }

        distance = distance_map.get((origin, destination), 500)

        # 高铁价格估算
        return {
            "type": "high_speed_rail",
            "price_estimate": {
                "二等座": distance * 0.4,
                "一等座": distance * 0.6,
                "商务座": distance * 1.2
            },
            "duration": f"{int(distance/300)}小时",  # 300km/h
            "distance": f"{distance}公里"
        }

    def get_location_info(self, location: str) -> Dict:
        """获取城市信息"""
        from travelagents.data.domestic_cities_db import DOMESTIC_CITIES_DB
        return DOMESTIC_CITIES_DB.get(location, {})


class InternationalDataProvider(BaseTravelDataProvider):
    """国际数据提供者"""

    def __init__(self):
        from travelagents.integrations.serpapi_client import SerpAPIClient
        from travelagents.integrations.openmeteo_client import OpenMeteoClient
        self.serpapi = SerpAPIClient()
        self.openmeteo = OpenMeteoClient()

    def search_attractions(self, location: str, interest_type: str = "") -> Dict:
        """使用SerpAPI搜索景点"""
        return self.serpapi.search_attractions(location, interest_type)

    def get_weather(self, location: str, days: int = 7) -> Dict:
        """使用Open-Meteo获取天气"""
        return self.openmeteo.get_weather(location, days)

    def estimate_transport_cost(self, origin: str, destination: str) -> Dict:
        """估算国际交通费用（机票）"""
        # 机票价格估算（往返）
        base_prices = {
            ("中国", "日本"): 3000,
            ("中国", "韩国"): 2500,
            ("中国", "泰国"): 2500,
            ("中国", "新加坡"): 3500,
            ("中国", "法国"): 6000,
            ("中国", "英国"): 6500,
            ("中国", "美国"): 7000,
        }

        base = base_prices.get(("中国", destination), 5000)

        return {
            "type": "flight",
            "price_estimate": {
                "经济舱": base,
                "商务舱": base * 3,
                "头等舱": base * 5
            },
            "duration": "往返",
            "note": "价格仅供参考"
        }

    def get_location_info(self, location: str) -> Dict:
        """获取国家信息"""
        from travelagents.data.international_countries_db import INTERNATIONAL_COUNTRIES_DB
        return INTERNATIONAL_COUNTRIES_DB.get(location, {})


class UnifiedDataProvider:
    """统一数据提供者（自动切换）"""

    def __init__(self):
        self.domestic = DomesticDataProvider()
        self.international = InternationalDataProvider()

    def get_provider(self, destination: str) -> BaseTravelDataProvider:
        """根据目的地类型返回对应的数据提供者"""
        classification = DestinationClassifier.classify(destination)

        if classification["type"] == "domestic":
            return self.domestic
        elif classification["type"] == "international":
            return self.international
        else:
            # 无法判断时，默认使用国际
            return self.international

    def search_attractions(self, destination: str, interest_type: str = "") -> Dict:
        """统一景点搜索接口"""
        provider = self.get_provider(destination)
        result = provider.search_attractions(destination, interest_type)
        result["destination_type"] = "domestic" if isinstance(provider, DomesticDataProvider) else "international"
        return result

    def get_weather(self, destination: str, days: int = 7) -> Dict:
        """统一天气查询接口"""
        provider = self.get_provider(destination)
        result = provider.get_weather(destination, days)
        result["destination_type"] = "domestic" if isinstance(provider, DomesticDataProvider) else "international"
        return result
```

---

### 3. 统一State结构

```python
# travelagents/agents/utils/travel_states.py

from typing import TypedDict, List, Dict, Optional, Literal
from langchain_core.messages import BaseMessage

class TravelPlanningState(TypedDict):
    """统一的旅行规划State（兼容国内+国际）"""

    # ==================== 用户输入 ====================
    user_input: str
    destination: str                      # 目的地（城市或国家）
    destination_type: Literal["domestic", "international", "auto"]  # 目的地类型
    start_date: str
    end_date: str
    days: int
    budget: float
    travelers: int
    interests: List[str]
    special_requirements: str

    # ==================== 目的地识别结果 ====================
    destination_info: Dict                # 目的地信息
    # {
    #     "type": "domestic" | "international",
    #     "normalized_name": "标准名称",
    #     "country": "所属国家",
    #     "province": "所属省份（国内）",
    #     "currency": "货币",
    #     "timezone": "时区"
    # }

    # ==================== 数据收集结果 ====================
    attractions: List[Dict]               # 景点列表
    weather_forecast: Dict                # 天气预报
    transport_options: Dict               # 交通选项
    location_highlights: List[str]        # 目的地亮点

    # ==================== 方案生成 ====================
    proposals: List[Dict]                 # 生成的方案（3种风格）
    selected_proposal: Optional[str]      # 用户选择的方案

    # ==================== 详细规划 ====================
    detailed_itinerary: Optional[Dict]    # 详细行程
    budget_breakdown: Optional[Dict]      # 预算明细
    practical_info: Optional[Dict]        # 实用信息

    # ==================== 调整历史 ====================
    adjustment_history: List[Dict]        # 调整历史

    # ==================== 最终输出 ====================
    final_plan: Optional[Dict]            # 最终方案

    # ==================== 系统字段 ====================
    messages: List[BaseMessage]
    current_step: str
    error: Optional[str]
```

---

### 4. 统一Agent接口

```python
# travelagents/agents/unified/__init__.py

from typing import Dict

def unified_attraction_analyst(llm, tools):
    """
    统一的景点分析Agent

    根据目的地类型自动调用不同的数据源
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是旅行规划助手，负责分析目的地景点。

你会根据目的地类型使用不同的数据源：
- 国内目的地：使用高德地图API
- 国际目的地：使用SerpAPI

你的任务：
1. 分析用户需求和目的地
2. 调用合适的API搜索景点
3. 根据用户偏好筛选和推荐景点
4. 给出景点推荐的评分和理由

输出格式：
- 景点名称
- 推荐理由
- 适合人群
- 预计游览时间
- 费用估算
"""),
        ("human", """请分析以下目的地的景点：

目的地：{destination}
类型：{destination_type}
用户兴趣：{interests}
旅行天数：{days}

请推荐适合的景点。"""),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    agent = prompt | llm.bind_tools(tools)

    def node(state: TravelPlanningState) -> TravelPlanningState:
        # 获取统一的数据提供者
        from travelagents.utils.unified_data_interface import UnifiedDataProvider
        data_provider = UnifiedDataProvider()

        # 搜索景点（自动选择API）
        interest = state["interests"][0] if state["interests"] else ""
        attractions_result = data_provider.search_attractions(
            state["destination"],
            interest
        )

        # 更新State
        state["attractions"] = attractions_result.get("attractions", [])
        state["destination_type"] = attractions_result.get("destination_type", "auto")

        # 调用Agent分析
        agent_input = {
            "destination": state["destination"],
            "destination_type": state["destination_type"],
            "interests": ", ".join(state["interests"]),
            "days": state["days"],
            "agent_scratchpad": []
        }

        result = agent.invoke(agent_input)
        state["messages"].append(result)

        return state

    return node
```

---

## 🎨 用户界面设计

### 统一的目的地选择界面

```
┌─────────────────────────────────────────────────────────────────┐
│  📝 第1步：选择您的目的地                                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🏠 国内热门目的地                                               │
│  ┌────────┬────────┬────────┬────────┬────────┬────────┐        │
│  │  北京  │  上海  │  西安  │  成都  │  杭州  │  更多  │        │
│  └────────┴────────┴────────┴────────┴────────┴────────┘        │
│  ┌────────┬────────┬────────┬────────┬────────┬────────┐        │
│  │  三亚  │  丽江  │  大理  │  重庆  │  厦门  │  更多  │        │
│  └────────┴────────┴────────┴────────┴────────┴────────┘        │
│                                                                 │
│  ──────────── 或 ────────────                                   │
│                                                                 │
│  🌐 国际旅行目的地                                               │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐        │
│  │ 🇯🇵 日本  │ 🇹🇭 泰国  │ 🇸🇬 新加坡│ 🇫🇷 法国  │ 🇬🇧 英国  │        │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘        │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐        │
│  │ 🇺🇸 美国  │ 🇦🇺 澳大利亚│ 🇰🇷 韩国  │ 🇮🇹 意大利 │ 🇪🇸 西班牙│        │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘        │
│                                                                 │
│  💬 或直接输入城市/国家名称：                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ [输入目的地...]                             [搜索]      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  系统会自动识别目的地类型，使用最佳数据源为您规划                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 目的地识别反馈

```
┌─────────────────────────────────────────────────────────────────┐
│  🔍 识别您的目的地...                                            │
│                                                                 │
│  您输入：西安                                                   │
│  ├─ 识别结果：🇨🇳 国内目的地                                   │
│  ├─ 标准名称：西安                                             │
│  ├─ 所在省份：陕西省                                           │
│  ├─ 使用数据源：高德地图API                                    │
│  └─ 主要景点：兵马俑、大雁塔、城墙、回民街                        │
│                                                                 │
│  [确认]  [修改]                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 数据源对比表

| 维度 | 国内（高德） | 国际（SerpAPI+Open-Meteo） |
|------|-------------|---------------------------|
| 景点搜索 | ✅ 高德POI | ✅ SerpAPI |
| 天气预报 | ✅ 高德天气 | ✅ Open-Meteo |
| 路线规划 | ✅ 高德路径 | ❌ 需要其他 |
| 交通方式 | 高铁/火车/自驾 | 飞机 |
| 价格数据 | 估算 | 估算 |
| 覆盖范围 | 中国300+城市 | 全球20+国家 |
| API费用 | 免费 | 免费额度 |

---

## 🚀 实施步骤

### 第1步：建立分类系统（1天）
```python
- 创建DestinationClassifier
- 建立国内城市列表
- 建立国际国家列表
- 测试识别准确性
```

### 第2步：实现国内分支（3-4天）
```python
- 集成高德地图API
- 实现国内景点搜索
- 实现国内天气查询
- 实现高铁价格估算
- 建立国内城市数据库
```

### 第3步：实现国际分支（3-4天）
```python
- 集成SerpAPI
- 集成Open-Meteo
- 实现国际景点搜索
- 实现机票价格估算
- 建立国际国家数据库
```

### 第4步：统一接口层（1-2天）
```python
- 创建UnifiedDataProvider
- 统一Agent接口
- 统一State结构
- 测试切换逻辑
```

### 第5步：测试和优化（2-3天）
```python
- 测试国内目的地流程
- 测试国际目的地流程
- 测试切换逻辑
- 优化识别准确性
```

---

## ⚠️ 注意事项

### 1. 港澳台的处理

```python
# 特殊处理：港澳台
SPECIAL_REGIONS = {
    "香港": {"type": "domestic", "special": true, "visa": "需要通行证"},
    "澳门": {"type": "domestic", "special": true, "visa": "需要通行证"},
    "台湾": {"type": "domestic", "special": true, "visa": "需要入台证"}
}
```

### 2. 边界情况

| 情况 | 处理方式 |
|------|---------|
| 无法识别的目的地 | 使用LLM辅助判断或让用户确认 |
| 同时匹配国内外 | 优先国内（如"北京"不会是美国城市） |
| 特殊地区（如港台） | 单独处理，标注特殊要求 |
| 目的地为国际机场 | 可能是国内城市，需要二次判断 |

### 3. 性能优化

```python
# 使用缓存减少API调用
from functools import lru_cache

@lru_cache(maxsize=1000)
def classify_destination_cached(destination: str):
    """带缓存的分类"""
    return DestinationClassifier.classify(destination)
```

---

## 💡 代码示例完整流程

```python
# 完整的旅行规划流程

def plan_travel(destination: str, days: int, budget: float, interests: List[str]):
    """统一的旅行规划入口"""

    # 1. 识别目的地类型
    classification = DestinationClassifier.classify(destination)
    destination_type = classification["type"]

    print(f"🔍 识别为：{'国内' if destination_type == 'domestic' else '国际'}目的地")

    # 2. 获取对应的数据提供者
    provider = UnifiedDataProvider()

    # 3. 搜索景点（自动选择API）
    attractions = provider.search_attractions(destination)
    if destination_type == "domestic":
        print(f"✅ 使用高德API找到{len(attractions)}个景点")
    else:
        print(f"✅ 使用SerpAPI找到{len(attractions)}个景点")

    # 4. 获取天气
    weather = provider.get_weather(destination, days)

    # 5. 估算交通费用
    transport = provider.estimate_transport_cost("出发地", destination)

    # 6. 生成方案（后续流程相同）
    proposals = generate_proposals(attractions, weather, budget, interests)

    return {
        "destination": destination,
        "type": destination_type,
        "proposals": proposals
    }
```

---

## 📝 总结

| 优势 | 说明 |
|------|------|
| **用户体验统一** | 无需区分国内国际，系统自动处理 |
| **易于扩展** | 新增目的地类型只需添加新的Provider |
| **代码复用** | 核心逻辑只需一套 |
| **维护简单** | 问题定位清晰，修改独立 |

| 注意点 | 说明 |
|--------|------|
| 识别准确性 | 需要完善的城市列表 |
| API配额 | 高德免费，SerpAPI有限额 |
| 性能优化 | 需要添加缓存 |
| 错误处理 | 识别失败时的降级方案 |

---

这个架构设计实现了国内+国际的统一支持，用户无需关心区别，系统自动处理。你觉得这个设计如何？需要调整吗？
