# 图片API修复总结

## 问题描述

1. **Unsplash API未被使用**：推荐地点的图片显示为默认图片，与实际地区无关
2. **前端布局问题**：四个地区/风格方案显示为3+1布局（第一行3个，第二行1个）
3. **国家名称无法识别**：国家级目的地（如"韩国"、"泰国"）没有被正确映射

## 修复内容

### 1. Unsplash服务修复 (`tradingagents/services/unsplash_search_service.py`)

#### 添加国家/地区映射
在 `city_map` 中添加了以下国家/地区的英文映射：
- 泰国 → thailand
- 韩国 → south korea
- 日本 → japan
- 新加坡 → singapore
- 马来西亚 → malaysia
- 越南 → vietnam
- 印尼 → indonesia
- 菲律宾 → philippines
- 中国 → china
- 香港 → hong kong
- 澳门 → macau
- 台湾 → taiwan

#### 修复 `_build_search_query` 方法
添加了特殊逻辑处理当景点名和城市名相同的情况：
```python
# 特殊处理：如果景点和城市相同（如"韩国 韩国"），使用城市英文翻译
if attraction_name == city and city in city_map:
    query = f"{city_en} travel"
# 如果景点在city_map中但不在attraction_map中（国家名）
elif attraction_name in city_map and attraction_name not in attraction_map:
    attraction_city_en = city_map.get(attraction_name, attraction_name)
    query = f"{attraction_city_en} {city_en}" if attraction_city_en != city_en else f"{city_en} travel"
```

### 2. 前端布局修复

#### DestinationCards.vue
```css
/* 修改前：auto-fit 导致3+1布局 */
.cards-grid {
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

/* 修改后：固定2列布局 */
.cards-grid {
  grid-template-columns: repeat(2, 1fr);
}
```

#### StyleSelection.vue
```css
/* 修改前：auto-fit 导致3+1布局 */
.styles-grid {
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
}

/* 修改后：固定2列布局 */
.styles-grid {
  grid-template-columns: repeat(2, 1fr);
}
```

### 3. 环境变量配置

`.env` 文件中已配置有效的 Unsplash Access Key：
```bash
UNSPLASH_ACCESS_KEY=TXRusbT1Jvwq9V0LXNBeqpA0eQ2vU92LGUpQZw_JMtk
```

## 测试结果

### 目的地图片测试
| 目的地 | 结果 | 图片来源 |
|--------|------|----------|
| 韩国 | ✅ | Unsplash |
| 泰国 | ✅ | Unsplash |
| 日本 | ✅ | Unsplash |
| 新加坡 | ✅ | Unsplash |
| 马来西亚 | ✅ | Unsplash |
| 越南 | ✅ | Unsplash |
| 印尼 | ✅ | Unsplash |
| 菲律宾 | ✅ | Unsplash |
| 中国 | ✅ | Unsplash |

### API状态检查
```json
{
  "unsplash": {
    "configured": true,
    "working": true,
    "rate_limit": {
      "limit": "50",
      "remaining": "49"
    }
  }
}
```

## 使用说明

### 直接调用服务
```python
from tradingagents.services.attraction_image_service import get_attraction_image

# 获取目的地图片
url = get_attraction_image('韩国', '韩国', 800, 600)
# 返回: https://images.unsplash.com/photo-...
```

### API调用
```bash
# 获取目的地图片
GET /api/travel/images/destination/{city}?width=800&height=600

# 批量获取图片
POST /api/travel/images/batch
Body: {
  "attractions": [
    {"name": "大皇宫", "city": "曼谷"},
    {"name": "景福宫", "city": "首尔"}
  ]
}
```

## 注意事项

1. **API限流**：Unsplash免费版每小时50次请求，合理使用
2. **回退机制**：当Unsplash失败时，自动回退到Pexels → Bing → 公开服务 → 占位图
3. **网络延迟**：大量并发请求可能导致部分请求超时，建议添加请求间隔
4. **服务重启**：修改配置后需要重启后端服务才能生效

## 相关文件

- `tradingagents/services/unsplash_search_service.py` - Unsplash API服务
- `tradingagents/services/attraction_image_service.py` - 图片获取主服务（回退链）
- `tradingagents/services/search_image_service.py` - 公开搜索服务（无需API Key）
- `app/routers/travel_images.py` - 图片API路由
- `frontend/src/views/travel/steps/DestinationCards.vue` - 目的地卡片组件
- `frontend/src/views/travel/steps/StyleSelection.vue` - 风格选择组件
- `.env` - 环境变量配置

## 更新日期

2025-03-13
