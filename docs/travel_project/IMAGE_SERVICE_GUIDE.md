# 景点图片服务配置指南

## 概述

景点图片服务采用**多源回退策略**，确保在任何情况下都能获取到图片：

```
优先级:
1. Unsplash Search API (最佳质量，需API Key)
2. Bing Search API (备选方案，需API Key)
3. 公开搜索服务 (无需API Key，质量一般)
4. 占位图 (最后回退)
```

---

## 快速开始

### 无需配置的方案（开箱即用）

系统已默认配置**公开搜索服务**（LoremFlickr），无需任何API密钥即可使用：

```python
from tradingagents.services.attraction_image_service import get_attraction_image

# 获取景点图片
url = get_attraction_image("埃菲尔铁塔", "巴黎")
# -> https://loremflickr.com/800/600/Paris,Eiffel%20Tower,landmark
```

### 最佳质量方案（推荐）

配置 **Unsplash Search API** 获取高质量真实照片：

```bash
# 1. 注册 Unsplash 开发者账号
# 访问: https://unsplash.com/developers

# 2. 创建新应用，获取 Access Key

# 3. 设置环境变量
export UNSPLASH_ACCESS_KEY="your_access_key_here"
```

```python
# 配置后自动使用Unsplash
url = get_attraction_image("埃菲尔铁塔", "巴黎")
# -> https://images.unsplash.com/photo-1511739001486-6bfe10ce7859?ixlib=rb-4.0.3&q=80
```

---

## API 配置详情

### 1. Unsplash Search API（推荐）

**优点**: 高质量专业照片，内容丰富
**限制**: 每小时 50 次请求（免费）

#### 注册步骤

1. 访问 https://unsplash.com/developers
2. 点击 "Register as a developer"
3. 创建新应用 (New Application)
4. 复制 Access Key（不是 Secret Key）

#### 配置

```bash
# Linux/Mac
export UNSPLASH_ACCESS_KEY="your_access_key"

# Windows PowerShell
$env:UNSPLASH_ACCESS_KEY="your_access_key"

# Windows CMD
set UNSPLASH_ACCESS_KEY=your_access_key
```

#### 永久配置（推荐）

添加到 `.env` 文件：

```env
UNSPLASH_ACCESS_KEY=your_access_key_here
```

#### 检查状态

```python
from tradingagents.services.unsplash_search_service import get_unsplash_service

service = get_unsplash_service()
status = service.check_api_status()
print(status)
# {'configured': True, 'working': True, 'rate_limit': {...}}
```

---

### 2. Bing Search API（备选）

**优点**: 图片来源丰富，微软基础设施
**限制**: 每月 1000 次免费请求

#### 注册步骤

1. 访问 https://portal.azure.com/
2. 搜索 "Bing Search v7"
3. 创建新资源
4. 获取 API Key

#### 配置

```bash
export BING_SEARCH_API_KEY="your_api_key_here"
```

或添加到 `.env` 文件：

```env
BING_SEARCH_API_KEY=your_api_key_here
```

---

### 3. 公开搜索服务（默认）

使用 **LoremFlickr** 等公开服务，无需配置。

**优点**: 无需API Key，开箱即用
**缺点**: 图片质量一般，相关性不稳定

---

## 使用方法

### 基础用法

```python
from tradingagents.services.attraction_image_service import get_attraction_image

# 中文景点
url = get_attraction_image("故宫", "北京")
print(url)

# 英文景点
url = get_attraction_image("Colosseum", "Rome")
print(url)
```

### 服务类用法

```python
from tradingagents.services.attraction_image_service import get_image_service

service = get_image_service()

# 单个图片
url = service.get_image("埃菲尔铁塔", "巴黎")

# 批量获取
attractions = [
    {"name": "埃菲尔铁塔", "city": "巴黎"},
    {"name": "卢浮宫", "city": "巴黎"},
    {"name": "凯旋门", "city": "巴黎"},
]
results = service.batch_get_images(attractions)
# {
#     "埃菲尔铁塔": "https://...",
#     "卢浮宫": "https://...",
#     "凯旋门": "https://..."
# }
```

### 主题色图片

```python
from tradingagents.services.attraction_image_service import get_themed_image

# 不同城市使用不同主题色
url = get_themed_image("故宫", "北京")  # 故宫红 #C41E3A
url = get_themed_image("埃菲尔铁塔", "巴黎")  # 巴黎紫 #8B5CF6
url = get_themed_image("大本钟", "伦敦")  # 伦敦橙 #F59E0B
```

### 直接使用特定服务

```python
# 直接使用 Unsplash
from tradingagents.services.unsplash_search_service import get_unsplash_service

unsplash = get_unsplash_service()
url = unsplash.get_attraction_image("Eiffel Tower", "Paris")

# 直接使用公开搜索
from tradingagents.services.search_image_service import get_public_search_service

public = get_public_search_service()
url = public.get_attraction_image("Great Wall", "Beijing")
```

---

## API 状态检查

```python
from tradingagents.services.attraction_image_service import get_image_service

service = get_image_service()
status = service.check_api_status()

print(status)
# {
#     'unsplash': {'configured': True, 'working': True, 'rate_limit': {...}},
#     'bing_search': {'configured': False, 'message': '未配置Bing API Key'},
#     'public_search': {'configured': True, 'working': True, 'type': 'public'}
# }
```

---

## 景点名称映射

Unsplash 搜索服务已内置常见景点中英文名称映射：

### 中国景点

| 中文 | 英文 |
|------|------|
| 故宫 | forbidden city |
| 长城 | great wall |
| 颐和园 | summer palace |
| 天坛 | temple of heaven |
| 西湖 | west lake |
| 外滩 | the bund |
| 东方明珠 | oriental pearl tower |
| 兵马俑 | terracotta warriors |
| 大雁塔 | big wild goose pagoda |

### 国际景点

| 中文 | 英文 |
|------|------|
| 埃菲尔铁塔 | eiffel tower |
| 卢浮宫 | louvre museum |
| 巴黎圣母院 | notre dame cathedral |
| 凯旋门 | arc de triomphe |
| 大本钟 | big ben |
| 伦敦塔桥 | tower bridge |
| 伦敦眼 | london eye |
| 自由女神 | statue of liberty |
| 帝国大厦 | empire state building |
| 斗兽场 | colosseum |
| 圣家堂 | sagrada familia |

### 城市名称映射

| 中文 | 英文 |
|------|------|
| 北京 | beijing |
| 上海 | shanghai |
| 西安 | xian |
| 成都 | chengdu |
| 巴黎 | paris |
| 伦敦 | london |
| 纽约 | new york |
| 东京 | tokyo |
| 罗马 | rome |

---

## 故障排除

### Unsplash 返回 403/401

```
原因: API Key 无效或过期
解决:
1. 检查 UNSPLASH_ACCESS_KEY 是否正确
2. 确认使用的是 Access Key，不是 Secret Key
3. 访问 https://unsplash.com/developers 重新生成
```

### 图片加载慢

```
原因: 网络问题或API速率限制
解决: 系统会自动回退到下一个源，无需手动处理
```

### 中文景点找不到图片

```
原因: Unsplash 主要使用英文索引
解决:
1. 使用英文景点名称: get_attraction_image("Forbidden City", "Beijing")
2. 系统会自动转换常见中文景点名
```

### 所有服务都失败

```
最终回退: 占位图 (placehold.co)
URL 格式: https://placehold.co/800x600/0EA5E9/FFFFFF?text=...
```

---

## 性能优化

### 缓存建议

```python
import hashlib

def cache_key(attraction: str, city: str) -> str:
    """生成缓存键"""
    return f"img:{attraction}:{city}"

# 使用 Redis 或内存缓存
# cached_url = cache.get(cache_key(attraction, city))
# if not cached_url:
#     cached_url = get_attraction_image(attraction, city)
#     cache.set(cache_key(attraction, city), cached_url, ttl=86400)
```

### 批量获取

对于多个景点，使用 `batch_get_images` 而非循环调用：

```python
# 推荐
service.batch_get_images(attractions)

# 避免
for attraction in attractions:
    service.get_image(attraction["name"], attraction["city"])
```

---

## 测试

运行测试脚本：

```bash
python scripts/test_image_service.py
```

输出示例：

```
============================================================
Test 2: Main Image Service (with fallback)
============================================================

Attraction: Eiffel Tower (Paris)
  URL: https://images.unsplash.com/photo-...
  [OK] Real image from Unsplash

============================================================
Test 4: Service Class
============================================================
API Status:
{
    'unsplash': {'configured': True, 'working': True},
    'bing_search': {'configured': False},
    'public_search': {'configured': True, 'working': True}
}
```

---

## 相关文件

```
tradingagents/services/
├── attraction_image_service.py      # 主服务（多源回退）
├── unsplash_search_service.py       # Unsplash API
├── search_image_service.py          # 搜索引擎API
└── __init__.py                       # 服务导出

scripts/
├── test_image_service.py            # 测试脚本
└── test_unsplash_search_api.py      # Unsplash测试

docs/travel_project/
└── IMAGE_SERVICE_GUIDE.md           # 本文档
```

---

## 总结

| 方案 | 质量 | 难度 | 成本 | 推荐度 |
|------|------|------|------|--------|
| **Unsplash Search** | ⭐⭐⭐⭐⭐ | 简单 | 免费（50次/小时） | ✅ 强烈推荐 |
| **Bing Search** | ⭐⭐⭐⭐ | 中等 | 免费（1000次/月） | ✅ 推荐 |
| **公开搜索** | ⭐⭐ | 极简 | 免费 | ✅ 默认/回退 |
| **占位图** | ⭐ | 极简 | 免费 | 仅作为最后回退 |

---

## 更新日志

### v3.0 (2025-03)
- 实现 Unsplash Search API 集成
- 添加 Bing Search API 支持
- 实现多源回退策略
- 添加中英文名称映射
- 优化错误处理和日志

### v2.0 (早期版本)
- 使用预定义图片数据库
- Picsum 随机图片
- LoremFlickr 关键词搜索
