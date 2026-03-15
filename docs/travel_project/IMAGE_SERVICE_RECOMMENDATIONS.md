# 国内外景点图片获取方案推荐

## 问题总结

1. **Unsplash Source API已废弃** - 之前的`source.unsplash.com`不再可用
2. **需要支持国内外景点** - 中英文景点名称都需要处理
3. **图片相关性要求** - 最好能显示与景点相关的图片，而不是随机图

## 推荐方案对比

| 方案 | 相关性 | 稳定性 | 成本 | 推荐指数 |
|------|--------|--------|------|----------|
| **预定义图片库** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 免费 | ✅ 最推荐 |
| **LoremFlickr** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 免费 | ✅ 推荐 |
| **Pexels API** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 免费(需密钥) | 🔧 可选 |
| **Picsum** | ⭐⭐ | ⭐⭐⭐⭐⭐ | 免费 | ✅ 备用 |

### 1. 预定义图片库（最推荐）

**优点**:
- 100%相关性，图片精准匹配景点
- 无需API调用，最快最稳定
- 支持中英文景点名称

**缺点**:
- 需要手动维护图片库
- 只能覆盖热门景点

**已支持的景点**:

#### 国内景点
| 城市 | 景点 |
|------|------|
| 北京 | 故宫、长城、颐和园、天坛、天安门 |
| 上海 | 外滩、东方明珠、迪士尼 |
| 西安 | 兵马俑、大雁塔、古城墙 |
| 杭州 | 西湖、雷峰塔 |
| 成都 | 大熊猫、宽窄巷子 |
| 厦门 | 鼓浪屿、曾厝垵 |

#### 国际景点
| 城市 | 景点 |
|------|------|
| Paris | 埃菲尔铁塔、卢浮宫、巴黎圣母院、凯旋门 |
| London | 大本钟、伦敦塔桥、伦敦眼、白金汉宫、大英博物馆 |
| New York | 自由女神、帝国大厦、中央公园、布鲁克林大桥、时代广场 |
| Tokyo | 东京塔、浅草寺、涩谷十字路口、富士山 |
| Sydney | 悉尼歌剧院、海港大桥、邦迪海滩 |
| Dubai | 哈利法塔、棕榈岛、迪拜码头 |
| Rome | 斗兽场、许愿池、梵蒂冈、万神殿 |
| Barcelona | 圣家堂、桂尔公园、巴特罗之家 |
| Bangkok | 大皇宫、黎明寺、湄南河 |
| Singapore | 滨海湾金沙、 Gardens by the Bay、鱼尾狮 |

### 2. LoremFlickr（推荐备选）

**URL格式**: `https://loremflickr.com/800/600/{keywords}`

**优点**:
- 基于Flickr的真实图片
- 支持关键词搜索
- 无需API密钥
- 相关性较好

**示例**:
```python
# 巴黎埃菲尔铁塔
https://loremflickr.com/800/600/paris,eiffel_tower

# 东京塔
https://loremflickr.com/800/600/tokyo,tower

# 悉尼歌剧院
https://loremflickr.com/800/600/sydney,opera_house
```

### 3. Pexels API（高质量可选）

**需要注册**: https://www.pexels.com/api/
**免费额度**: 200次/小时

**优点**:
- 图片质量最高
- 完全基于关键词搜索
- 支持多种尺寸

**配置**:
```bash
export PEXELS_API_KEY="your_api_key_here"
```

### 4. Picsum（最后备用）

**URL格式**: `https://picsum.photos/800/600?random={seed}`

**优点**:
- 无需API，极其稳定
- 基于种子，相同景点返回相同图片

**缺点**:
- 完全随机，无相关性

## 最终推荐策略

```
1. 预定义图片库（热门景点） ✅
   ↓ 如果未找到
2. LoremFlickr关键词搜索（相关性） ✅
   ↓ 如果失败
3. Pexels API（高质量，可选） 🔧
   ↓ 如果失败
4. Picsum随机图（最终备用） ✅
```

## 使用代码

```python
from tradingagents.services.attraction_image_service import get_attraction_image

# 国内景点
url1 = get_attraction_image("故宫", "北京")
# → 预定义图片: https://images.unsplash.com/photo-1508804185872-d7badad00f7d...

# 国际景点（英文）
url2 = get_attraction_image("Eiffel Tower", "Paris")
# → 预定义图片: https://images.unsplash.com/photo-1511739001486-6bfe10ce7859...

# 国际景点（中文）
url3 = get_attraction_image("埃菲尔铁塔", "巴黎")
# → 自动转换为英文，获取预定义图片

# 冷门景点（使用关键词搜索）
url4 = get_attraction_image("某个冷门景点", "东京")
# → LoremFlickr: https://loremflickr.com/800/600/tokyo,travel,landmark
```

## 扩展图片库

要添加更多景点，只需在对应字典中添加条目：

```python
# 添加到 INTERNATIONAL_ATTRACTION_IMAGES
"Vienna": {
    "Schonbrunn Palace": "https://images.unsplash.com/photo-...",
    "St. Stephen's Cathedral": "https://images.unsplash.com/photo-...",
},
```

## 其他方案说明

### ❌ 不推荐的方案

1. **Unsplash API** - 需要付费密钥，有请求限制
2. **百度图片爬虫** - 违反服务条款，不稳定
3. **Google Images API** - 需要付费，配额限制
4. **Bing Image Search** - 需要API密钥

### 🔧 可考虑的方案

1. **自建CDN图床** - 长期方案，需要投入存储成本
2. **Cloudinary** - 提供图片优化和CDN服务
3. **Imgix** - 类似Cloudinary的图片处理服务

## 总结

**最推荐的方案** = **预定义图片库** + **LoremFlickr**

这种组合:
- 热门景点使用精准的高质量图片
- 冷门景点使用基于关键词的相关图片
- 完全免费，无需API密钥
- 稳定可靠，不会出现服务中断

对于旅行规划应用，这个方案已经足够满足需求。如果后续有更高需求，可以考虑：
1. 逐步扩充预定义图片库
2. 配置Pexels API获取更多高质量图片
3. 实现图片缓存减少重复请求
