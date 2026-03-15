# 景点图片获取示例说明

## 预定义图片库找不到会怎样？

### 自动降级流程

```
预定义图片库 (查找)
    ↓ 未找到
LoremFlickr关键词搜索 (自动)
    ↓ 失败
Picsum随机图 (最终备用)
```

### 示例代码

```python
from tradingagents.services.attraction_image_service import get_attraction_image

# 场景1: 预定义图片库中有
url = get_attraction_image("故宫", "北京")
# → https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800&q=80
# (直接返回预定义的高质量图片)

# 场景2: 预定义图片库中没有，自动用LoremFlickr搜索
url = get_attraction_image("某个冷门景点", "巴黎")
# → https://loremflickr.com/800/600/paris,landmark?lock=abc123
# (自动用关键词搜索)

# 场景3: 国际景点，支持中英文
url = get_attraction_image("埃菲尔铁塔", "巴黎")
# → https://images.unsplash.com/photo-1511739001486-6bfe10ce7859?w=800&q=80
# (中文自动转换，找到预定义图片)
```

---

## Flickr是什么？

**Flickr** 是雅虎旗下的图片分享和托管网站，拥有数以亿计的高质量照片。

### LoremFlickr

**LoremFlickr** 是一个基于Flickr图片的免费API服务，可以根据关键词获取相关图片。

**官网**: https://loremflickr.com/

---

## 实际图片示例

### 1. 预定义图片库示例

#### 巴黎埃菲尔铁塔
```
https://images.unsplash.com/photo-1511739001486-6bfe10ce7859?w=800&q=80
```
![巴黎埃菲尔铁塔](https://images.unsplash.com/photo-1511739001486-6bfe10ce7859?w=800&q=80)

#### 伦敦大本钟
```
https://images.unsplash.com/photo-1529655683826-aba9b3e77383?w=800&q=80
```
![伦敦大本钟](https://images.unsplash.com/photo-1529655683826-aba9b3e77383?w=800&q=80)

#### 北京故宫
```
https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800&q=80
```
![北京故宫](https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800&q=80)

#### 纽约自由女神
```
https://images.unsplash.com/photo-1503731404080-6ac4c707c626?w=800&q=80
```
![纽约自由女神](https://images.unsplash.com/photo-1503731404080-6ac4c707c626?w=800&q=80)

---

### 2. LoremFlickr图片示例

LoremFlickr会根据关键词从Flickr获取相关图片：

#### 巴黎景点搜索
```
https://loremflickr.com/800/600/paris,landmark
```
<iframe src="https://loremflickr.com/800/600/paris,landmark" width="800" height="600" frameborder="0"></iframe>

#### 东京旅行
```
https://loremflickr.com/800/600/tokyo,travel
```
<iframe src="https://loremflickr.com/800/600/tokyo,travel" width="800" height="600" frameborder="0"></iframe>

#### 悉尼歌剧院
```
https://loremflickr.com/800/600/sydney,opera
```
<iframe src="https://loremflickr.com/800/600/sydney,opera" width="800" height="600" frameborder="0"></iframe>

---

### 3. Picsum随机图片示例（最后备用）

```
https://picsum.photos/800/600?random=abc123
```

---

## 对比总结

| 服务 | 图片来源 | 相关性 | 稳定性 | 示例URL |
|------|----------|--------|--------|---------|
| 预定义库 | Unsplash精选 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | `images.unsplash.com/photo-xxx` |
| LoremFlickr | Flickr实时 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | `loremflickr.com/800/600/paris` |
| Picsum | 随机图库 | ⭐⭐ | ⭐⭐⭐⭐⭐ | `picsum.photos/800/600` |

---

## 实际使用中的效果

### 热门景点（预定义库）

| 搜索词 | 返回图片 |
|--------|----------|
| `get_attraction_image("Eiffel Tower", "Paris")` | 真实的埃菲尔铁塔照片 |
| `get_attraction_image("埃菲尔铁塔", "巴黎")` | 同上（中文自动转换） |
| `get_attraction_image("故宫", "北京")` | 真实的故宫照片 |

### 冷门景点（LoremFlickr自动搜索）

| 搜索词 | 返回图片 |
|--------|----------|
| `get_attraction_image("某个小众公园", "东京")` | 东京相关的Flickr图片 |
| `get_attraction_image("Custom Place", "Paris")` | 巴黎相关的Flickr图片 |

### 完全未知的地点（Picsum备用）

| 搜索词 | 返回图片 |
|--------|----------|
| `get_attraction_image("未知地点", "未知城市")` | 随机风景图片 |

---

## 如何添加更多预定义图片？

如果发现常用景点没有被预定义库覆盖，可以手动添加：

```python
# 在 attraction_image_service.py 中添加

INTERNATIONAL_ATTRACTION_IMAGES = {
    "Vienna": {  # 新增城市
        "Schonbrunn Palace": "https://images.unsplash.com/photo-1571005756534-48e56e48f215?w=800&q=80",
        "St. Stephen's": "https://images.unsplash.com/photo-1575881869344-822770b65d8f?w=800&q=80",
    },
    "Amsterdam": {  # 新增城市
        "Canal": "https://images.unsplash.com/photo-1534351590666-13e3e96b5017?w=800&q=80",
        "Museum Square": "https://images.unsplash.com/photo-1555993212-2ad577d28733?w=800&q=80",
    },
}
```

---

## 推荐策略

**对于旅行规划应用**，建议：

1. **预定义热门景点** - 覆盖80%的用户搜索
2. **LoremFlickr备选** - 处理剩余20%的长尾需求
3. **Picsum兜底** - 确保永远不会失败

这样既能保证热门景点的图片质量，又能处理任意景点的图片需求，且完全免费无需API密钥。
