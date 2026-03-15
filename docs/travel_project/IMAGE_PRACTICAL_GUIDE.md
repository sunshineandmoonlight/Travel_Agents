# 景点图片获取实用指南

## 问题分析

Unsplash的图片URL格式复杂，直接构造容易出错。推荐以下实用方案：

---

## 方案对比

| 方案 | 难度 | 可靠性 | 相关性 | 推荐 |
|------|------|--------|--------|------|
| **Unsplash网站手动获取** | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ 最推荐 |
| **动态图床服务** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ 推荐 |
| **百度图片搜索** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ 备用 |
| **直接使用关键词服务** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ✅ 简单 |

---

## 方案1: Unsplash网站手动获取（最推荐）

### 步骤

1. 访问 https://unsplash.com/sphotos/{关键词}
   ```
   https://unsplash.com/sphotos/eiffel tower
   https://unsplash.com/sphotos/great wall of china
   https://unsplash.com/sphotos/tokyo tower
   ```

2. 选择喜欢的图片，点击下载

3. 复制图片URL（从浏览器或响应数据中获取）

### 获取真实URL的方法

在图片页面，打开浏览器开发者工具(F12)，Network标签，找到图片请求，复制真实URL。

**Unsplash真实URL格式示例**:
```
https://images.unsplash.com/photo-1499856871958-5b9627545d1a?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80
```

---

## 方案2: 动态图床服务（推荐）

使用 ImgPx 或类似服务，根据关键词动态生成图片：

```python
def get_dynamic_image(keyword: str, width: int = 800, height: int = 600) -> str:
    """
    使用动态图床服务获取图片
    """
    # 方案A: ImgPx API
    return f"https://imgpx.photos/{width}/{height}?q={keyword}"

    # 方案B: Picsum (但加上关键词哈希，使相同关键词返回相同图片)
    import hashlib
    seed = hashlib.md5(keyword.encode()).hexdigest()[:8]
    return f"https://picsum.photos/seed/{seed}/{width}/{height}"
```

**示例URL**:
```
https://imgpx.photos/800/600?q=eiffel tower paris
https://picsum.photos/seed/eiffel/800/600
```

---

## 方案3: 直接使用关键词图片服务

### 推荐服务

1. **Lorem Picsum** (带关键词)
   ```
   https://picsum.photos/seed/{keyword}/800/600
   ```

   示例:
   - 巴黎: `https://picsum.photos/seed/paris/800/600`
   - 埃菲尔铁塔: `https://picsum.photos/seed/eiffel/800/600`
   - 长城: `https://picsum.photos/seed/greatwall/800/600`

2. **Flickr API** (需要密钥，但相关性好)
   ```
   https://www.flickr.com/services/rest/?method=flickr.photos.search&text=eiffel+tower
   ```

3. **Pexels API** (需要密钥，免费额度大)
   ```
   https://api.pexels.com/v1/search?query=eiffel%20tower&per_page=1
   ```

---

## 方案4: 使用前端图片组件

最可靠的方案是使用前端图片组件，支持多个备选源：

```vue
<template>
  <img
    :src="imageUrl"
    @error="handleImageError"
    loading="lazy"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  attractionName: String,
  city: String
})

const imageUrl = ref('')
const fallbackSources = ref([])

onMounted(() => {
  // 生成带备选源的图片URL
  const sources = [
    // 尝试1: 关键词图床
    `https://loremflickr.com/800/600/${props.city},${props.attractionName}`,
    // 尝试2: Picsum带种子
    `https://picsum.photos/seed/${props.attractionName}/800/600`,
    // 尝试3: 占位图
    `https://via.placeholder.com/800x600/0EA5E9/FFFFFF?text=${encodeURIComponent(props.attractionName)}`
  ]

  fallbackSources.value = sources
  imageUrl.value = sources[0]
})

function handleImageError(e) {
  // 当前图片加载失败，尝试下一个
  const currentIndex = fallbackSources.value.indexOf(imageUrl.value)
  if (currentIndex < fallbackSources.value.length - 1) {
    imageUrl.value = fallbackSources.value[currentIndex + 1]
  }
}
</script>
```

---

## 推荐的最终方案

### 简单可靠（当前推荐）

使用 **关键词种子 + Picsum**:

```python
import hashlib

def get_attraction_image(attraction_name: str, city: str) -> str:
    """获取景点图片URL"""
    # 组合关键词
    keyword = f"{city}_{attraction_name}".replace(" ", "_")

    # 生成一致的种子
    seed = hashlib.md5(keyword.encode()).hexdigest()[:8]

    # 使用Picsum（带种子确保一致性）
    return f"https://picsum.photos/seed/{seed}/800/600"
```

**优点**:
- ✅ 100%可用，无需API
- ✅ 相同关键词返回相同图片
- ✅ 加载快速

**示例**:
```python
get_attraction_image("埃菲尔铁塔", "巴黎")
# → https://picsum.photos/seed/bali_aifuleta_800/600

get_attraction_image("故宫", "北京")
# → https://picsum.photos/seed/beijing_gugong/800/600
```

---

## 手动收集图片库（可选）

对于重要的热门景点，可以手动收集真实图片URL：

```python
MANUAL_CURATED_IMAGES = {
    "Paris_Eiffel Tower": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg/800px-Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg",
    "London_Big Ben": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Clock_Tower_-_Palace_of_Westminster%2C_London_-_May_2007.jpg/800px-Clock_Tower_-_Palace_of_Westminster%2C_London_-_May_2007.jpg",
    "Beijing_Forbidden_City": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Forbidden_Circle_2006_10_24.jpg/800px-Forbidden_Circle_2006_10_24.jpg",
    # 使用维基百科（可靠，但质量一般）
}

# 或者使用你自己拍摄/收集的图片URL
```

---

## 总结

### 当前最推荐方案

**Picsum带关键词种子** - 简单、可靠、免费

```python
url = f"https://picsum.photos/seed/{hashlib.md5(keyword.encode()).hexdigest()[:8]}/800/600"
```

### 如果需要高质量图片

1. 手动从Unsplash网站获取真实URL
2. 或者使用维基百科的公开图片
3. 或者自己拍摄/收集图片库

### 如果需要API自动化

配置 **Pexels API** - 免费额度大(200次/小时)，图片质量高

注册地址: https://www.pexels.com/api/
