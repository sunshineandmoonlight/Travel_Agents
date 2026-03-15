# 旅行项目API集成方案

## 📋 可用的API平台

### 1. Amadeus for Developers

#### 简介
Amadeus是全球最大的旅游分销系统之一，提供专业的旅行API。

#### 免费额度
- **免费测试层**：每月2000次免费调用
- **申请方式**：注册开发者账号 → 创建应用 → 获取API Key
- **文档**：https://developers.amadeus.com/

#### 可用API

| API | 功能 | 是否需要用于MVP |
|-----|------|----------------|
| **Flight Offers Search** | 机票搜索 | ❌ MVP不需要，V2可以考虑 |
| **Hotel Search** | 酒店搜索 | ❌ MVP不需要，V2可以考虑 |
| **Points of Interest** | 景点搜索 | ✅ 可以补充SerpAPI |
| **Travel Recommendations** | 旅行推荐 | ✅ 可能有用 |
| **Airport and City Search** | 机场城市搜索 | ✅ 有用（规划路线） |

#### 集成难度
- ⚠️ 中等（需要OAuth 2.0认证）
- ⚠️ 需要处理B2B数据结构（Journey format等）

---

### 2. RapidAPI平台

#### 简介
RapidAPI是一个API聚合平台，上面有很多旅行相关的API，大部分都有免费层。

#### 推荐的旅行API

| API | 免费额度 | 推荐度 | 说明 |
|-----|---------|--------|------|
| **Amadeus API** | 同上 | ⭐⭐⭐⭐⭐ | 直接在RapidAPI调用Amadeus |
| **Booking.com** | 不确定 | ⭐⭐⭐ | 需要合作伙伴账号 |
| **Skyscanner API** | 有限免费 | ⭐⭐⭐⭐ | 机票比价 |
| **Hotels.com** | 有限免费 | ⭐⭐⭐ | 酒店搜索 |
| **TripAdvisor API** | 部分免费 | ⭐⭐⭐⭐ | 景点/餐厅评论 |
| **Airhob** | 100次/月 | ⭐⭐⭐ | 机票预订 |

#### 优势
- ✅ 一个平台管理多个API
- ✅ 统一的SDK支持（Python/JavaScript）
- ✅ 大部分有免费层
- ✅ 快速集成

---

## 🎯 推荐的API组合方案

### 方案A：基础版（MVP推荐）

| 数据来源 | API | 成本 |
|---------|-----|------|
| 景点 | SerpAPI（已有） | 免费 |
| 餐厅 | SerpAPI（已有） | 免费 |
| 天气 | Open-Meteo | 免费 |
| 汇率 | ExchangeRate-API | 免费 |
| 机票价格 | 规则估算（距离×系数） | 免费 |
| 酒店价格 | 等级估算（经济/舒适/豪华） | 免费 |

**优点**：
- 无需额外申请API
- 快速实施
- 足够MVP使用

---

### 方案B：增强版（求职加分）

| 数据来源 | API | 免费额度 |
|---------|-----|---------|
| 景点 | SerpAPI | 100次/月 |
| 餐厅 | SerpAPI | 100次/月 |
| 天气 | Open-Meteo | 无限制 |
| 汇率 | ExchangeRate-API | 无限制 |
| 机票价格 | RapidAPI - Skyscanner | 50次/月 |
| 酒店价格 | RapidAPI - Hotels.com | 有限 |
| 机场信息 | Amadeus | 2000次/月 |

**优点**：
- 有真实价格数据
- 面试时可以说集成了多个真实API
- 更有说服力

---

### 方案C：完整版（最强）

| 数据来源 | API | 说明 |
|---------|-----|------|
| 机票实时搜索 | Amadeus Flight API | 需要认证 |
| 酒店实时搜索 | Amadeus Hotel API | 需要认证 |
| 景点深度信息 | Amadeus POI | 补充数据 |
| 餐厅评论 | TripAdvisor | 用户评价 |

**优点**：
- 专业级数据
- 完整的旅行规划能力

**缺点**：
- 开发时间长
- OAuth认证复杂

---

## 🛠️ 快速集成指南

### RapidAPI集成示例

#### 1. 注册RapidAPI
```
1. 访问 https://rapidapi.com/
2. 注册账号
3. 搜索 "Amadeus" 或 "Skyscanner"
4. 点击 "Subscribe" 选择免费层
5. 获取 API Key
```

#### 2. Python代码示例

```python
import requests

def get_flight_prices(origin, destination, date):
    """获取机票价格（使用RapidAPI上的Skyscanner或Amadeus）"""

    # 示例：使用Amadeus通过RapidAPI
    url = "https://api.amadeus.com/v2/shopping/flight-offers"

    headers = {
        "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY",
        "X-RapidAPI-Host": "api.amadeus.com"
    }

    params = {
        "origin": origin,        # 如 "PEK" (北京)
        "destination": destination, # 如 "NRT" (东京)
        "departureDate": date,   # 如 "2024-05-01"
        "adults": 1,
        "max": 5  # 返回5个最低价
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()

        # 解析价格
        if 'data' in data and len(data['data']) > 0:
            prices = [offer['price']['total'] for offer in data['data']]
            return min(prices)  # 返回最低价
        else:
            return None

    except Exception as e:
        print(f"获取机票价格失败: {e}")
        return None

def get_hotel_prices(city, checkin, checkout):
    """获取酒店价格（使用RapidAPI）"""

    # 示例：使用Booking.com API
    url = "https://booking-com.p.rapidapi.com/v1/hotels/locations"

    headers = {
        "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY",
        "X-RapidAPI-Host": "booking-com.p.rapidapi.com"
    }

    params = {
        "name": city,
        "search_type": "city"
    }

    try:
        # 先获取城市ID
        response = requests.get(url, headers=headers, params=params)
        city_data = response.json()

        if city_data and len(city_data) > 0:
            dest_id = city_data[0]['dest_id']

            # 然后搜索酒店
            search_url = "https://booking-com.p.rapidapi.com/v1/hotels/search"
            search_params = {
                "dest_id": dest_id,
                "checkin_date": checkin,
                "checkout_date": checkout,
                "adults_number": 1,
                "order_by": "price",
                "units": "metric"
            }

            search_response = requests.get(search_url, headers=headers, params=search_params)
            hotel_data = search_response.json()

            if 'result' in hotel_data and len(hotel_data['result']) > 0:
                # 返回价格范围
                prices = [h.get('price_breakdown', {}).get('all_inclusive_price')
                         for h in hotel_data['result'] if h.get('price_breakdown')]
                if prices:
                    return min(prices), max(prices)

        return None, None

    except Exception as e:
        print(f"获取酒店价格失败: {e}")
        return None, None
```

#### 3. 降级策略

```python
def get_price_with_fallback(origin, destination, date, price_type="flight"):
    """
    带降级策略的价格获取
    """
    # 尝试从真实API获取
    if price_type == "flight":
        price = get_flight_prices(origin, destination, date)
    else:
        price = get_hotel_prices(origin, destination, date)

    # 如果API失败，使用估算
    if price is None:
        print(f"API获取失败，使用估算价格")
        price = estimate_price(origin, destination, price_type)

    return price

def estimate_price(origin, destination, price_type):
    """规则估算价格（降级方案）"""

    # 距离估算（简化版）
    distance_map = {
        ("中国", "日本"): 2000,
        ("中国", "泰国"): 2500,
        ("中国", "新加坡"): 3500,
        ("中国", "法国"): 8000,
        ("中国", "英国"): 8500
    }

    distance = distance_map.get(("中国", destination), 3000)

    if price_type == "flight":
        # 机票估算：往返价格
        base_price = distance * 2  # 每公里2元
        return base_price

    elif price_type == "hotel":
        # 酒店估算：每晚价格
        price_map = {
            "日本": 600,
            "泰国": 300,
            "新加坡": 500,
            "法国": 800,
            "英国": 900
        }
        return price_map.get(destination, 500) * 100  # 假设5晚
```

---

## 📊 API选择对比

| 方案 | 优点 | 缺点 | 推荐场景 |
|------|------|------|---------|
| **只用SerpAPI** | 已有key，简单 | 无机票酒店价格 | MVP |
| **+ RapidAPI** | 多个API可选 | 需要注册多个 | 增强版 |
| **+ Amadeus** | 专业数据 | OAuth复杂 | 完整版 |

---

## 🎯 我的建议

### 对于求职项目

**推荐组合**：SerpAPI + RapidAPI（Skyscanner或Hotels）

**理由**：
1. ✅ **有真实数据**：面试时可以展示集成了真实API
2. ✅ **免费额度够用**：开发测试完全够用
3. ✅ **不算太复杂**：比直接用Amadeus简单
4. ✅ **降级方案**：API失败时用估算兜底

### 实施步骤

**第1步**：先用估算实现MVP（1-2天）
```
- 规则估算机票价格
- 规则估算酒店价格
- 主流程跑通
```

**第2步**：集成1-2个RapidAPI（3-5天）
```
- 注册RapidAPI
- 集成Skyscanner获取机票价格
- 集成Hotels.com获取酒店价格
- 添加降级逻辑
```

**第3步**：测试和优化（2-3天）
```
- 测试API失败情况
- 优化降级逻辑
- 添加缓存减少API调用
```

---

## ⚠️ 注意事项

### 1. 免费额度限制

| API | 免费额度 | 应对 |
|-----|---------|------|
| SerpAPI | 100次/月 | 缓存结果 |
| RapidAPI | 50-100次/月 | 缓存+估算 |
| Amadeus | 2000次/月 | 相对充足 |

### 2. 价格数据时效性

机票价格实时变动，所以：
- **展示时**：标注"价格仅供参考，以实际预订为准"
- **估算时**：使用近期平均价格
- **缓存时**：缓存1-2小时

### 3. 法律声明

```
⚠️ 所有价格仅供参考，实际价格以预订时为准
⚠️ 本系统不提供预订服务，仅提供规划和参考信息
```

---

## 💡 面试时怎么说

**如果有真实API**：
```
"我集成了多个真实的旅行API，包括：
- SerpAPI获取景点和餐厅信息
- RapidAPI上的Skyscanner获取机票价格
- Open-Meteo获取天气预报
- 并且设计了降级策略，当API不可用时自动切换到估算数据"
```

**如果只用估算**：
```
"考虑到API的成本和稳定性，我使用了规则估算的方式，
并设计了可扩展的架构，未来可以轻松接入真实API"
```

两种说法都是可以接受的！

---

## 📝 总结

| 问题 | 答案 |
|------|------|
| **Amadeus能用吗** | ✅ 能，但有2000次/月限制 |
| **RapidAPI推荐吗** | ✅ 推荐，有多个选择 |
| **MVP需要吗** | ❌ MVP阶段不需要 |
| **求职项目用吗** | ✅ 用了加分 |
| **实施难度** | ⚠️ 中等，需要1-2天 |

**我的建议**：
- MVP阶段：先不用，用估算快速实现
- 增强阶段：集成1-2个RapidAPI（Skyscanner）
- 完整阶段：如果时间允许，可以集成Amadeus

你想在哪个阶段集成这些API？
