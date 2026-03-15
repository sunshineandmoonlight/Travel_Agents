# 目的地情报数据源API指南

## 概述

本文档介绍可用于获取目的地新闻、活动、风险信息的各种API数据源。

---

## 一、新闻数据源

### 1.1 天行数据 (推荐)

**官网**: https://www.tianapi.com/

**优势**:
- 新用户送15个接口，可以使用5000次
- 提供综合新闻接口
- 支持关键词搜索
- 响应速度快，稳定可靠

**新闻接口**:
- 综合新闻接口 - 混合输出全频道新闻数据
- 支持按关键词搜索
- 返回格式: JSON

**Python调用示例**:
```python
import requests

def get_tianapi_news(keyword, num=10):
    """获取天行数据新闻"""
    url = "http://api.tianapi.com/generalnews/index"
    params = {
        "key": "YOUR_API_KEY",  # 替换为你的API Key
        "word": keyword,        # 搜索关键词
        "num": num             # 返回数量
    }
    response = requests.get(url, params=params)
    return response.json()

# 使用示例
news = get_tianapi_news("杭州旅游", 10)
```

**配置项** (.env):
```bash
TIANAPI_KEY=your_api_key_here
```

---

### 1.2 聚合数据

**官网**: https://www.juhe.cn/

**优势**:
- 国内领先的综合数据服务平台
- 黑钻会员可享受免费接口无限调用
- 提供新闻API接口

**Python调用示例**:
```python
import requests

def get_juhe_news(keyword, page=1):
    """获取聚合数据新闻"""
    url = "http://v.juhe.cn/news/index"
    params = {
        "key": "YOUR_API_KEY",
        "keyword": keyword,
        "page": page
    }
    response = requests.get(url, params=params)
    return response.json()
```

**配置项** (.env):
```bash
JUHE_API_KEY=your_api_key_here
```

---

### 1.3 SerpApi - 百度新闻

**官网**: https://serpapi.com/baidu-news-api

**优势**:
- 提供结构化的百度新闻数据
- 支持Python SDK
- 有免费额度（100次/月）

**Python调用示例**:
```python
from serpapi import GoogleSearch

def get_baidu_news_serpapi(query, num=10):
    """使用SerpApi获取百度新闻"""
    params = {
        "engine": "baidu_news",
        "q": query,
        "num": num,
        "api_key": "YOUR_API_KEY"
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("news_results", [])

# 使用示例
news = get_baidu_news_serpapi("杭州旅游政策", 10)
```

**配置项** (.env):
```bash
SERPAPI_KEY=your_api_key_here
```

---

## 二、社交媒体数据源

### 2.1 微博API (官方)

**官网**: http://open.weibo.com/

**优势**:
- 官方API，数据权威
- 可以获取实时的社交媒体动态

**限制**:
- 需要申请开发者账号
- 审核需要2-3天
- 有API调用频率限制

**Python调用示例**:
```python
from weibo import Client

def get_weibo_search(keyword):
    """搜索微博相关内容"""
    client = Client(
        api_key='YOUR_API_KEY',
        api_secret='YOUR_API_SECRET',
        redirect_uri='YOUR_CALLBACK_URL',
        token='YOUR_ACCESS_TOKEN'
    )
    results = client.get('search/topics', q=keyword)
    return results
```

**配置项** (.env):
```bash
WEIBO_API_KEY=your_api_key
WEIBO_API_SECRET=your_api_secret
WEIBO_ACCESS_TOKEN=your_access_token
```

---

### 2.2 开源方案 - weibo-api

**GitHub**: https://github.com/tuian/weibo-api

**优势**:
- 免登录获取微博数据
- 开源免费
- 简单易用

**Python调用示例**:
```python
from weibo_api import WeiboClient

def get_weibo_by_user(user_id):
    """通过用户ID获取微博"""
    client = WeiboClient()
    posts = client.get_user_posts(user_id)
    return posts
```

---

## 三、文旅局数据源

### 3.1 官方网站爬虫

由于各地文旅局没有统一的API，需要针对不同城市编写爬虫：

**建议方案**:
1. 维护一个各地文旅局URL映射表
2. 使用BeautifulSoup或lxml解析HTML
3. 提取活动信息

**Python示例**:
```python
import requests
from bs4 import BeautifulSoup

def scrape_tourism_bureau(city):
    """爬取城市文旅局活动信息"""
    url_map = {
        "杭州": "http://whlyj.hangzhou.gov.cn/",
        "北京": "http://whlyj.beijing.gov.cn/",
        # ... 更多城市
    }

    url = url_map.get(city)
    if not url:
        return []

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 解析活动信息（需要根据实际网页结构调整）
    events = []
    for item in soup.select('.event-item'):
        events.append({
            "title": item.select_one('.title').text,
            "date": item.select_one('.date').text,
            "location": item.select_one('.location').text
        })

    return events
```

---

## 四、天气数据源

### 4.1 和风天气API (推荐)

**官网**: https://dev.qweather.com/

**优势**:
- 免费版每天1000次请求
- 提供天气预报、灾害预警
- 数据准确

**Python调用示例**:
```python
import requests

def get_weather_alerts(city):
    """获取天气预警信息"""
    url = "https://devapi.qweather.com/v7/warning/now"
    params = {
        "location": city,  # 城市ID
        "key": "YOUR_API_KEY"
    }
    response = requests.get(url, params=params)
    return response.json()

def get_weather_forecast(city, days=3):
    """获取天气预报"""
    url = "https://devapi.qweather.com/v7/weather/{}d".format(days)
    params = {
        "location": city,
        "key": "YOUR_API_KEY"
    }
    response = requests.get(url, params=params)
    return response.json()
```

**配置项** (.env):
```bash
QWEATHER_KEY=your_api_key
```

---

## 五、推荐实施方案

### 方案A: 最小成本方案 (免费)

| 数据类型 | 数据源 | 成本 |
|---------|--------|------|
| 新闻 | 天行数据 | 免费5000次 |
| 社交媒体 | 开源weibo-api | 免费 |
| 活动 | 文旅局官网爬虫 | 免费 |
| 天气 | 和风天气 | 1000次/天免费 |

**总成本**: 0元/月

### 方案B: 稳定可靠方案 (付费)

| 数据类型 | 数据源 | 成本 |
|---------|--------|------|
| 新闻 | SerpApi + 天行数据 | ~50元/月 |
| 社交媒体 | 微博官方API | 免费 |
| 活动 | 文旅局官网爬虫 | 免费 |
| 天气 | 和风天气高级版 | ~100元/月 |

**总成本**: 约150元/月

---

## 六、集成步骤

### 步骤1: 添加配置到 .env

```bash
# 新闻数据源
NEWS_SOURCE=tianapi  # tianapi / serpapi / juhe
TIANAPI_KEY=your_key
SERPAPI_KEY=your_key

# 社交媒体
WEIBO_API_KEY=your_key

# 天气
QWEATHER_KEY=your_key
```

### 步骤2: 创建数据源适配器

```python
# app/services/data_sources/news_adapter.py
class NewsAdapter:
    def __init__(self, source: str):
        self.source = source

    async def search_news(self, keyword: str, days: int = 7):
        if self.source == "tianapi":
            return await self._search_tianapi(keyword, days)
        elif self.source == "serpapi":
            return await self._search_serpapi(keyword, days)
        # ... 其他数据源
```

### 步骤3: 更新目的地情报智能体

```python
# tradingagents/agents/analysts/destination_intelligence.py
from app.services.data_sources.news_adapter import NewsAdapter

class DestinationIntelligenceAgent:
    def __init__(self):
        self.news_adapter = NewsAdapter(
            source=os.getenv("NEWS_SOURCE", "mock")
        )

    async def _search_news(self, destination: str, days: int = 7):
        if os.getenv("NEWS_SOURCE") == "mock":
            return await self._mock_news(destination)  # 模拟数据
        else:
            return await self.news_adapter.search_news(
                f"{destination} 旅游", days
            )
```

---

## 七、快速开始

### 最简配置 (仅使用模拟数据)

无需任何API Key，智能体将使用内置的模拟数据进行演示。

### 推荐配置 (天行数据)

1. 注册天行数据账号: https://www.tianapi.com/
2. 获取API Key
3. 添加到 .env: `TIANAPI_KEY=your_key`
4. 设置: `NEWS_SOURCE=tianapi`

### 完整配置

1. 天行数据 - 新闻数据
2. 和风天气 - 天气预警
3. 微博API - 社交媒体（可选）

---

**Sources:**
- [SerpApi - Baidu News API](https://serpapi.com/baidu-news-api)
- [GitHub - baidu_news](https://github.com/kkyykk96/baidu_news)
- [微博开放平台](http://open.weibo.com/)
- [天行数据](https://www.tianapi.com/)
- [聚合数据](https://www.juhe.cn/)
- [和风天气](https://dev.qweather.com/)
