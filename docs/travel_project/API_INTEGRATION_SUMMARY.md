# API集成详细攻略说明

## 概述

本文档说明如何为旅行规划系统生成包含真实餐厅名称、地址、电话号码、天气预报和景点图片的详细攻略。

---

## 1. 已配置的API集成

### 1.1 高德地图API (Amap)

**状态**: ✅ 已配置，API Key已设置

**位置**: `tradingagents/integrations/amap_client.py`

**功能**:
- `search_attractions(city, keyword, limit)` - 搜索景点
- `search_restaurants(city, keyword, limit)` - 搜索餐厅
- `get_weather(city, days)` - 获取天气预报
- `get_attraction_detail(poi_id)` - 获取POI详情
- `plan_route(origin, destination)` - 路径规划
- `get_distance(origins, destination)` - 距离矩阵
- `estimate_transport_cost(origin, destination, type)` - 交通费用估算

**返回数据包含**:
- 餐厅名称、地址、电话、坐标
- 景点名称、地址、电话、坐标
- 商圈信息
- POI类型

### 1.2 Open-Meteo天气API

**状态**: ✅ 已配置（免费，无需API密钥）

**位置**: `tradingagents/integrations/openmeteo_client.py`

**功能**:
- `get_weather_forecast(city, days)` - 天气预报
- `get_current_weather(city)` - 当前天气

### 1.3 统一数据接口

**状态**: ✅ 已配置

**位置**: `tradingagents/utils/unified_data_interface.py`

**功能**: 根据目的地类型（国内/国际）自动选择合适的数据源

---

## 2. 新增数据增强服务

### 2.1 TravelDataEnrichmentService

**位置**: `tradingagents/services/travel_data_enrichment.py`

**主要功能**:

#### `enrich_restaurant_data()` - 获取真实餐厅数据
```python
service = get_enrichment_service()
result = service.enrich_restaurant_data(
    city="北京",
    cuisine_type="美食",
    budget_level="medium",
    limit=15
)

# 返回
{
    "success": True,
    "restaurants": [
        {
            "name": "全聚德烤鸭店",
            "address": "东城区王府井大街9号",
            "phone": "010-65253871",
            "estimated_cost": 180,
            "cost_range": "144-216元/人",
            "specialties": ["北京烤鸭", "鸭卷", "鸭汤"],
            "business_area": "王府井",
            "recommendation_score": 0.85
        },
        # ... 更多餐厅
    ],
    "count": 15,
    "source": "amap"
}
```

#### `enrich_attraction_data()` - 获取真实景点数据
```python
result = service.enrich_attraction_data(
    city="北京",
    attraction_type="景点",
    limit=20
)

# 返回包含图片URL、门票价格、游览时长等
```

#### `get_detailed_weather()` - 获取详细天气
```python
weather = service.get_detailed_weather("北京", 7)
# 返回每日天气、温度、风力等
```

#### `get_attraction_image()` - 生成景点图片URL
```python
image_url = service.get_attraction_image("故宫", "北京")
# 返回: https://source.unsplash.com/800x600/?gugong,landmark
```

#### `search_nearby_restaurants()` - 搜索景点附近餐厅
```python
restaurants = service.search_nearby_restaurants(
    attraction_name="故宫",
    city="北京",
    meal_type="午餐",
    budget_level="medium"
)
```

---

## 3. Group C智能体集成

### 3.1 餐饮推荐师 (dining_recommender.py)

**更新内容**:
- 新增 `_get_real_restaurants()` 函数调用真实API
- 更新 `recommend_dining()` 优先使用真实数据
- 更新 `_recommend_meal()` 筛选合适的真实餐厅

**生成的餐厅信息包含**:
- 餐厅名称（来自高德POI）
- 详细地址
- 电话号码
- 人均消费估算
- 推荐菜系
- 商圈位置

### 3.2 攻略格式化师 (guide_formatter.py)

**更新内容**:
- 新增 `_get_weather_for_dates()` 获取天气预报
- 更新 `_build_daily_itineraries()` 集成天气数据
- 新增 `_enrich_dining_info()` 增强餐厅详情显示
- 更新 `format_guide_as_text()` 包含天气和详细餐厅信息

**生成的攻略包含**:
- 每日天气信息
- 推荐餐厅的详细联系方式
- 地址和电话
- 特色菜品推荐
- 价格范围

---

## 4. LLM联网查询能力

### 4.1 当前状态

系统配置了以下LLM提供商:
- OpenAI (支持GPT-4 with browsing)
- DeepSeek
- Google Gemini (部分模型支持联网)
- 阿里云通义千问

### 4.2 如何启用联网查询

对于支持的LLM（如GPT-4 with browsing），可以在创建LLM实例时指定:

```python
from tradingagents.graph.trading_graph import create_llm_by_provider

llm = create_llm_by_provider(
    provider="openai",
    model="gpt-4",
    backend_url="",  # 或使用Azure OpenAI
    temperature=0.7,
    max_tokens=2000,
    timeout=60
)
```

### 4.3 建议的增强方案

对于需要更详细信息的情况（如特色菜品描述、餐厅评价等），可以:

1. **使用Tavily API** - 专门的搜索API，支持实时搜索
2. **集成SerpAPI** - Google搜索结果API
3. **使用LLM Function Calling** - 让LLM调用搜索工具获取最新信息

---

## 5. 景点图片获取方案

### 5.1 国内景点

**方案A: 高德POI图片**
- 高德API部分POI包含图片信息
- 需要额外的API调用获取详情

**方案B: Unsplash API（当前实现）**
```python
# 使用Unsplash Source API（免费）
url = f"https://source.unsplash.com/800x600/?{keyword},landmark"
```

**方案C: 自建图片库**
- 维护一个景点名称到图片URL的映射
- 使用爬虫或手动整理

### 5.2 国际景点

**推荐方案**:
- Unsplash API - 免费高质量图片
- Pexels API - 免费图片和视频
- Pixabay API - 免费图片资源

**实现示例**:
```python
def get_international_attraction_image(attraction_name: str, city: str) -> str:
    keywords = f"{city} {attraction_name} travel landmark"
    return f"https://source.unsplash.com/800x600/?{keywords}"
```

---

## 6. 攻略质量示例

### 6.1 餐厅推荐示例

**之前的输出**:
```
午餐: 周边餐厅
特色: 北京烤鸭
```

**现在的输出**:
```
午餐: 王府井美食街
📍 推荐餐厅: 全聚德烤鸭店
   地址: 东城区王府井大街9号
   电话: 010-65253871
   人均: 144-216元/人
   特色: 北京烤鸭, 鸭卷, 鸭汤
🍽️ 推荐菜品: 北京烤鸭, 鸭卷
```

### 6.2 天气信息示例

**新增输出**:
```
📅 第1天: 皇家紫禁城探秘
🌤️ 天气: 晴 8°C-18°C
   东南风3级
```

---

## 7. 待完善项

### 7.1 需要安装的依赖

```bash
pip install pypinyin  # 用于生成图片URL
```

### 7.2 可选增强

1. **图片缓存**: 避免重复请求相同的图片
2. **餐厅评价**: 集成大众点评或美团API获取评分
3. **实时价格**: 获取餐厅最新菜单价格
4. **营业时间**: 确认餐厅营业状态
5. **预订链接**: 提供在线预订入口

---

## 8. 使用示例

### 8.1 测试数据增强服务

```python
from tradingagents.services.travel_data_enrichment import get_enrichment_service

service = get_enrichment_service()

# 获取餐厅数据
restaurants = service.enrich_restaurant_data("北京", "美食", "medium", 10)

# 获取景点数据
attractions = service.enrich_attraction_data("北京", "故宫", 10)

# 获取天气
weather = service.get_detailed_weather("北京", 5)
```

### 8.2 生成详细攻略

```python
from tradingagents.agents.group_c.guide_formatter import format_detailed_guide

guide = format_detailed_guide(
    destination="北京",
    style_proposal=style,
    scheduled_attractions=schedule,
    transport_plan=transport,
    dining_plan=dining,  # 现在包含真实餐厅数据
    accommodation_plan=accommodation,
    user_requirements=requirements
)

# 导出文本版本
from tradingagents.agents.group_c.guide_formatter import format_guide_as_text
text_guide = format_guide_as_text(guide)
```

---

## 9. API调用限制说明

### 高德地图API

- **免费配额**: 30万次/日
- **超出收费**: 按调用次数计费
- **建议**: 启用缓存减少重复调用

### Open-Meteo API

- **完全免费**: 无需注册
- **无限制**: 非商业使用无限制
- **建议**: 无需特殊处理

### Unsplash API

- **免费版**: 50次/小时
- **注册后**: 5000次/小时
- **建议**: 使用Source API无需密钥

---

## 10. 总结

✅ **已完成**:
1. 高德地图API已配置并集成
2. Open-Meteo天气API已配置
3. 新增数据增强服务
4. 餐饮推荐师使用真实餐厅数据
5. 攻略格式化师包含天气和详细餐厅信息
6. 支持景点图片URL生成

🔄 **可选增强**:
1. 集成LLM联网查询获取更详细信息
2. 添加餐厅评价和实时价格
3. 实现图片缓存机制
4. 添加预订功能

---

**生成时间**: 2026-03-12
**版本**: v3.0
