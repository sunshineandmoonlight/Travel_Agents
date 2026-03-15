# 国内旅游API集成方案

## 📋 可用的国内旅游API

### 1. 地图与POI类（核心推荐）

#### 高德地图 API ⭐⭐⭐⭐⭐
- **免费额度**：个人开发者100万次/天
- **注册地址**：https://console.amap.com/
- **可用功能**：
  | API | 功能 | 说明 |
  |-----|------|------|
  | **周边搜索** | 景点、餐厅搜索 | 代替SerpAPI |
  | **天气查询** | 天气预报 | 代替Open-Meteo |
  | **路径规划** | 交通路线 | 高铁/自驾/公交 |
  | **POI详情** | 景点详细信息 | 开放时间、门票等 |
  | **行政区划** | 省市区县查询 | 城市信息 |

```python
# 高德地图API示例
import requests

AMAP_KEY = "您的key"

def search_attractions(city, keyword="景点"):
    """搜索景点"""
    url = "https://restapi.amap.com/v3/place/text"
    params = {
        "key": AMAP_KEY,
        "keywords": keyword,
        "city": city,
        "types": "风景名胜",  # 只搜景点
        "offset": 20
    }
    response = requests.get(url, params=params)
    return response.json()

def get_weather(city):
    """获取天气（高德天气API）"""
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "key": AMAP_KEY,
        "city": city,
        "extensions": "all"  # 获取预报
    }
    response = requests.get(url, params=params)
    return response.json()
```

#### 百度地图 API ⭐⭐⭐⭐
- **免费额度**：个人开发者免费
- **注册地址**：https://lbsyun.baidu.com/
- **可用功能**：与高德类似

---

### 2. 火车/高铁类

#### 12306（无公开API）

| 方案 | 说明 | 推荐度 |
|------|------|--------|
| **第三方聚合** | 如：智能火车、路路通等 | ⭐⭐⭐ |
| **爬虫（不推荐）** | 有法律风险 | ❌ |
| **规则估算** | 根据里程估算价格 | ⭐⭐⭐⭐ MVP推荐 |

**估算方案（MVP）**：
```python
def estimate_train_price(origin, destination, seat_type="二等座"):
    """
    估算高铁/火车价格

    参考价格（每公里）：
    - 高铁二等座：0.3-0.5元/公里
    - 高铁一等座：0.5-0.8元/公里
    - 普通列车硬座：0.15-0.2元/公里
    """
    # 城市间距离（公里）
    distance_map = {
        ("北京", "上海"): 1200,
        ("北京", "西安"): 1000,
        ("北京", "成都"): 1800,
        ("上海", "杭州"): 180,
        ("上海", "南京"): 300,
        ("广州", "深圳"): 140,
        # ... 更多
    }

    # 如果不在表中，用直线距离估算
    distance = distance_map.get((origin, destination), 500)

    # 每公里价格
    price_per_km = {
        "二等座": 0.4,
        "一等座": 0.6,
        "商务座": 1.2,
        "硬座": 0.18,
        "硬卧": 0.35,
        "软卧": 0.55
    }

    return distance * price_per_km.get(seat_type, 0.4)
```

**真实数据方案（增强版）**：
```python
# 使用聚合平台API
# 如：心知天气、快递100等平台也提供火车数据
# 或者购买第三方API服务
```

---

### 3. 景点门票类

#### 携程/美团/飞猪（无公开API）

| 方案 | 说明 | 推荐度 |
|------|------|--------|
| **高德POI** | 包含景点信息 | ⭐⭐⭐⭐⭐ |
| **爬虫（谨慎）** | 有法律风险 | ⚠️ |
| **规则估算** | 根据景点等级 | ⭐⭐⭐⭐ |
| **第三方平台** | 如票牛、同程等 | ⭐⭐⭐ |

**高德POI获取景点信息**：
```python
def get_attraction_detail(poi_id):
    """获取景点详情（包含门票信息）"""
    url = "https://restapi.amap.com/v3/place/detail"
    params = {
        "key": AMAP_KEY,
        "id": poi_id
    }
    response = requests.get(url, params=params)
    data = response.json()

    # 解析信息
    return {
        "name": data.get("name"),
        "address": data.get("address"),
        "tel": data.get("tel"),
        "business_area": data.get("business_area"),
        # 门票价格需要从其他渠道获取
    }
```

---

### 4. 美食类

#### 高德/百度 POI搜索
```python
def search_restaurants(city, food_type=""):
    """搜索餐厅"""
    url = "https://restapi.amap.com/v3/place/text"
    params = {
        "key": AMAP_KEY,
        "keywords": f"{food_type}餐厅" if food_type else "美食",
        "city": city,
        "types": "餐饮服务",
        "offset": 20
    }
    response = requests.get(url, params=params)
    return response.json()
```

#### 大众点评（无公开API）
- 可以用爬虫（有风险）
- 或者使用高德/百度替代

---

## 🏗️ 系统架构调整

### 原架构（仅国际）

```
用户输入目的地 → 识别国家 → 搜索国际景点 → 生成方案
```

### 新架构（国内+国际）

```
用户输入目的地
    ↓
判断：国内 or 国际？
    ↓                    ↓
国内分支              国际分支
    ↓                    ↓
高德API搜索          SerpAPI搜索
高铁/火车估算        机票API
高德天气API          Open-Meteo
    ↓                    ↓
生成国内方案          生成国际方案
```

---

## 📊 国内外差异对比

| 维度 | 国内旅游 | 国际旅游 | 应对 |
|------|---------|---------|------|
| **主要交通** | 高铁/火车 | 飞机 | 分开处理 |
| **景点数据** | 高德/百度POI | SerpAPI | 不同API |
| **天气数据** | 高德/和风 | Open-Meteo | 可选其一 |
| **酒店预订** | 携程/美团 | Booking | 都用估算 |
| **门票信息** | 景区官网/高德 | 官网 | 都用估算 |
| **支付方式** | 微信/支付宝 | 信用卡 | 仅展示价格 |
| **签证要求** | 无 | 大部分需要 | 条件分支 |

---

## 🎯 国内城市数据库

### 热门旅游城市

```python
DOMESTIC_CITIES = {
    # 一线城市
    "北京": {
        "province": "北京市",
        "highlights": ["故宫", "长城", "颐和园", "天坛"],
        "best_season": ["spring", "autumn"],
        "budget_level": "medium"
    },
    "上海": {
        "province": "上海市",
        "highlights": ["外滩", "迪士尼", "豫园", "南京路"],
        "best_season": ["spring", "autumn"],
        "budget_level": "high"
    },
    "广州": {
        "province": "广东省",
        "highlights": ["广州塔", "长隆", "沙面", "陈家祠"],
        "best_season": ["autumn", "winter"],
        "budget_level": "medium"
    },
    "深圳": {
        "province": "广东省",
        "highlights": ["世界之窗", "欢乐谷", "大梅沙"],
        "best_season": ["autumn", "winter"],
        "budget_level": "high"
    },

    # 热门旅游城市
    "西安": {
        "province": "陕西省",
        "highlights": ["兵马俑", "大雁塔", "城墙", "回民街"],
        "best_season": ["spring", "autumn"],
        "budget_level": "medium"
    },
    "成都": {
        "province": "四川省",
        "highlights": ["熊猫基地", "宽窄巷子", "锦里", "都江堰"],
        "best_season": ["spring", "autumn"],
        "budget_level": "medium"
    },
    "杭州": {
        "province": "浙江省",
        "highlights": ["西湖", "灵隐寺", "西溪湿地", "宋城"],
        "best_season": ["spring", "autumn"],
        "budget_level": "medium"
    },
    "南京": {
        "province": "江苏省",
        "highlights": ["中山陵", "夫子庙", "明孝陵", "玄武湖"],
        "best_season": ["spring", "autumn"],
        "budget_level": "medium"
    },
    "重庆": {
        "province": "重庆市",
        "highlights": ["洪崖洞", "解放碑", "磁器口", "火锅"],
        "best_season": ["spring", "autumn"],
        "budget_level": "medium"
    },
    "厦门": {
        "province": "福建省",
        "highlights": ["鼓浪屿", "曾厝垵", "南普陀", "环岛路"],
        "best_season": ["autumn", "winter"],
        "budget_level": "medium"
    },

    # 休闲度假城市
    "三亚": {
        "province": "海南省",
        "highlights": ["亚龙湾", "天涯海角", "南山寺", "蜈支洲岛"],
        "best_season": ["autumn", "winter"],
        "budget_level": "high"
    },
    "丽江": {
        "province": "云南省",
        "highlights": ["古城", "玉龙雪山", "泸沽湖", "束河古镇"],
        "best_season": ["autumn", "winter"],
        "budget_level": "medium"
    },
    "大理": {
        "province": "云南省",
        "highlights": ["古城", "洱海", "苍山", "喜洲"],
        "best_season": ["spring", "autumn"],
        "budget_level": "medium"
    },
    "桂林": {
        "province": "广西省",
        "highlights": ["漓江", "象鼻山", "阳朔", "龙脊梯田"],
        "best_season": ["autumn"],
        "budget_level": "low"
    },
    "青岛": {
        "province": "山东省",
        "highlights": ["崂山", "栈桥", "八大关", "啤酒博物馆"],
        "best_season": ["summer", "autumn"],
        "budget_level": "medium"
    },
    "大连": {
        "province": "辽宁省",
        "highlights": ["星海广场", "老虎滩", "金石滩", "发现王国"],
        "best_season": ["summer", "autumn"],
        "budget_level": "medium"
    }
}
```

---

## 🔧 API集成代码

### 国内景点搜索

```python
def search_domestic_attractions(city, interest_type=""):
    """
    使用高德地图搜索国内景点

    Args:
        city: 城市名称（如"北京"、"西安"）
        interest_type: 兴趣类型（如"古镇"、"自然"、"寺庙"）
    """
    url = "https://restapi.amap.com/v3/place/text"

    # 关键词映射
    keyword_map = {
        "自然": "风景区",
        "寺庙": "寺庙",
        "古镇": "古镇",
        "博物馆": "博物馆",
        "公园": "公园",
        "": "风景名胜"  # 默认
    }

    keyword = keyword_map.get(interest_type, "风景名胜")

    params = {
        "key": AMAP_KEY,
        "keywords": keyword,
        "city": city,
        "types": "风景名胜",
        "offset": 20
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "1" and data.get("pois"):
            # 解析返回的景点
            attractions = []
            for poi in data["pois"][:10]:
                attractions.append({
                    "name": poi.get("name"),
                    "address": poi.get("address"),
                    "location": poi.get("location"),  # 经纬度
                    "tel": poi.get("tel"),
                    "type": poi.get("type"),
                    "poi_id": poi.get("id")  # 用于获取详情
                })
            return {
                "success": True,
                "city": city,
                "attractions": attractions,
                "count": len(attractions)
            }
        else:
            return {"success": False, "error": "未找到景点"}

    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 国内天气查询

```python
def get_domestic_weather(city, days=7):
    """
    使用高德地图查询国内天气

    Args:
        city: 城市名称
        days: 查询天数
    """
    url = "https://restapi.amap.com/v3/weather/weatherInfo"

    params = {
        "key": AMAP_KEY,
        "city": city,
        "extensions": "all"  # 获取预报天气
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "1":
            forecasts = data.get("forecasts", [])
            if forecasts and len(forecasts) > 0:
                forecast = forecasts[0]
                casts = forecast.get("casts", [])[:days]

                weather_info = []
                for cast in casts:
                    weather_info.append({
                        "date": cast.get("date"),
                        "weather": cast.get("dayweather"),
                        "temperature": f"{cast.get('nighttemp')}°C-{cast.get('daytemp')}°C",
                        "wind": cast.get("daywind", ""),
                        "week": cast.get("week")
                    })

                return {
                    "success": True,
                    "city": city,
                    "weather": weather_info
                }

        return {"success": False, "error": "获取天气失败"}

    except Exception as e:
        return {"success": False, "error": str(e)}
```

---

## 🎯 UI界面调整

### 目的地选择（国内+国际）

```
┌─────────────────────────────────────────────────────────────┐
│  🌍 您想去哪里？                                              │
│                                                             │
│  📍 国内热门：                                               │
│  ┌──────┬──────┬──────┬──────┬──────┬──────┐                │
│  │ 北京 │ 西安 │ 成都 │ 杭州 │ 重庆 │ 更多 │                │
│  └──────┴──────┴──────┴──────┴──────┴──────┘                │
│  ┌──────┬──────┬──────┬──────┬──────┬──────┐                │
│  │ 三亚 │ 丽江 │ 大理 │ 青岛 │ 厦门 │ 更多 │                │
│  └──────┴──────┴──────┴──────┴──────┴──────┘                │
│                                                             │
│  🌐 国际旅行：                                               │
│  ┌───────┬───────┬───────┬───────┬───────┐                   │
│  │ 🇯🇵 日本│ 🇹🇭 泰国│ 🇸🇬 新加坡│ 🇫🇷 法国│ 🇬🇧 英国│                   │
│  └───────┴───────┴───────┴───────┴───────┘                   │
│                                                             │
│  💬 或输入城市：                                            │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ [输入城市名称...]                                      │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 方案选择（国内版）

```
┌─────────────────────────────────────────────────────────────┐
│  为您设计了3种打开方式：                                      │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  【A】经典打卡  │  【B】深度体验  │  【C】休闲度假  │     │ │
│  │   必去景点      │   小众秘境      │   慢节奏放松       │     │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │  北京5天示例：  │  北京5天示例：  │  北京5天示例：  │     │ │
│  │  Day1: 天安门   │  Day1: 国家博物馆 │  Day1: 颐和园    │     │ │
│  │  Day2: 故宫    │  Day2: 首都博物馆 │  Day2: 什刹海    │     │ │
│  │  Day3: 长城    │  Day3: 798艺术区 │  Day3: 咖啡探店  │     │ │
│  │  Day4: 颐和园  │  Day4: 胡同探索  │  Day4: 自由活动  │     │ │
│  │  Day5: 天坛    │  Day5: 环球影城  │  Day5: 返程      │     │ │
│  │               │                 │                 │     │ │
│  │  交通：地铁+打车│  交通：地铁+公交 │  交通：少移动    │     │ │
│  │  住宿：市中心酒店│  住宿：特色民宿  │  住宿：度假村    │     │ │
│  │               │                 │                 │     │ │
│  │  预算: ¥3,500  │  预算: ¥4,000   │  预算: ¥5,000   │     │ │
│  │  强度: ★★★★☆  │  强度: ★★★☆☆   │  强度: ★★☆☆☆   │     │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  [选A]  [选B]  [选C]                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 实施建议

### 方案A：先做国内（推荐新手）

**理由**：
- ✅ 高德API免费且稳定
- ✅ 中文文档，易于理解
- ✅ 国内数据更熟悉
- ✅ 高铁/火车比机票简单

**实施顺序**：
```
1. 集成高德地图API（1-2天）
2. 建立国内城市数据库（1天）
3. 实现国内景点搜索（1天）
4. 实现国内天气查询（半天）
5. 实现方案生成（2-3天）
```

### 方案B：国内国际一起做

**架构**：
```
用户输入目的地
    ↓
判断类型：国内 vs 国际
    ↓        ↓
国内分支  国际分支
高德API   SerpAPI
    ↓        ↓
 合并生成方案
```

**实施顺序**：
```
1. 设计统一的State结构（1天）
2. 实现国际分支（3-4天）
3. 实现国内分支（3-4天）
4. 整合测试（1-2天）
```

---

## 💡 面试时怎么说

**如果做了国内+国际**：
```
"我的系统支持国内外旅行规划：
- 国内使用高德地图API，覆盖300+城市
- 国际使用SerpAPI和Open-Meteo
- 系统自动识别目的地类型，调用不同API
- 针对国内外差异（高铁vs机票）做了适配"
```

---

## ⚠️ 注意事项

| 问题 | 说明 | 应对 |
|------|------|------|
| 高德API配额 | 100万次/天，足够用 | 无需担心 |
| 火车票数据 | 12306无公开API | 使用估算 |
| 景点门票 | 无实时API | 使用估算+高德POI |
| 城市识别 | 用户输入不规范 | 建立城市别名表 |

---

## 📝 总结

| 问题 | 答案 |
|------|------|
| **国内API能用吗** | ✅ 可以，高德地图免费 |
| **推荐先做哪个** | ⭐⭐⭐⭐⭐ 推荐先做国内 |
| **国内国际能共存** | ✅ 可以，系统判断分支 |
| **开发难度** | ⚠️ 国内更简单 |
| **求职加分吗** | ✅ 加分，覆盖国内外 |

**我的建议**：
1. 先做国内版本（高德API免费且稳定）
2. 跑通后再加国际版本
3. 或者国内国际一起做（架构上支持分支）

你想先做哪个？还是一起做？
