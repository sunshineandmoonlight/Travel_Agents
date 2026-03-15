# 旅行规划系统 - 使用说明和图片URL

## 当前状态

### ✅ 已完成
1. **前端图片API路径** - 已修复
2. **规则引擎评分算法** - 已改进
3. **LLM函数代码** - 已修复
4. **环境变量加载** - 已添加
5. **高质量图片配置** - 已创建

### ⚠️ 需要验证
1. **LLM启用** - 代码已修复，需前端刷新后验证
2. **高质量图片** - 配置已创建，API集成中

---

## 直接可用的高质量图片URL

### 城市封面图片 (1200x800)

```html
<!-- 北京 -->
https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=1200&h=800&fit=crop
https://images.unsplash.com/photo-1547989687-61adfe544fee?w=1200&h=800&fit=crop
https://images.unsplash.com/photo-1584964733753-c8291263f014?w=1200&h=800&fit=crop

<!-- 上海 -->
https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=1200&h=800&fit=crop
https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=1200&h=800&fit=crop
https://images.unsplash.com/photo-1536697246260-dfb66cc6cba6?w=1200&h=800&fit=crop

<!-- 成都 -->
https://images.unsplash.com/photo-1628163574848-46a263a4232b?w=1200&h=800&fit=crop
https://images.unsplash.com/photo-1596221378303-74c2dc36e3b5?w=1200&h=800&fit=crop
https://images.unsplash.com/photo-1620627119562-44982ecc977c?w=1200&h=800&fit=crop

<!-- 西安 -->
https://images.unsplash.com/photo-1582573848606-38e674f3b683?w=1200&h=800&fit=crop
https://images.unsplash.com/photo-1599972017-4e117c09865a?w=1200&h=800&fit=crop
https://images.unsplash.com/photo-1567907886007-4db66ae4c14d?w=1200&h=800&fit=crop

<!-- 杭州 -->
https://images.unsplash.com/photo-1569163139539-0e27c1d520bd?w=1200&h=800&fit=crop
https://images.unsplash.com/photo-1548612591-2344263d54f1?w=1200&h=800&fit=crop
https://images.unsplash.com/photo-1528164344705-47584f1f3f26?w=1200&h=800&fit=crop

<!-- 厦门 -->
https://images.unsplash.com/photo-1601572637264-fc19c9d2a86a?w=1200&h=800&fit=crop
https://images.unsplash.com/photo-1580674684081-7617fbf3d745?w=1200&h=800&fit=crop
https://images.unsplash.com/photo-1528120928147-0acb8f10f4aa?w=1200&h=800&fit=crop

<!-- 三亚 -->
https://images.unsplash.com/photo-1597327637774-d9f65c57e18b?w=1200&h=800&fit=crop
https://images.unsplash.com/photo-1580914052510-4515b38692bd?w=1200&h=800&fit=crop
https://images.unsplash.com/photo-1532603505494-1f889d48084e?w=1200&h=800&fit=crop

<!-- 重庆 -->
https://images.unsplash.com/photo-1547975719-0ec76a592802?w=1200&h=800&fit=crop
https://images.unsplash.com/photo-1596482956222-1b84be86fd53?w=1200&h=800&fit=crop
https://images.unsplash.com/photo-1596221377592-518cf2e2108e?w=1200&h=800&fit=crop
```

### 景点图片 (800x600)

```html
<!-- 故宫 -->
https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800&h=600&fit=crop

<!-- 外滩 -->
https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800&h=600&fit=crop

<!-- 大熊猫 -->
https://images.unsplash.com/photo-1628163574848-46a263a4232b?w=800&h=600&fit=crop

<!-- 兵马俑 -->
https://images.unsplash.com/photo-1582573848606-38e674f3b683?w=800&h=600&fit=crop

<!-- 西湖 -->
https://images.unsplash.com/photo-1569163139539-0e27c1d520bd?w=800&h=600&fit=crop

<!-- 鼓浪屿 -->
https://images.unsplash.com/photo-1601572637264-fc19c9d2a86a?w=800&h=600&fit=crop

<!-- 洪崖洞 -->
https://images.unsplash.com/photo-1547975719-0ec76a592802?w=800&h=600&fit=crop

<!-- 黄鹤楼 -->
https://images.unsplash.com/photo-1578496501048-e14d87e36e42?w=800&h=600&fit=crop
```

---

## Unsplash动态搜索URL（无需API密钥）

```
# 格式
https://source.unsplash.com/{宽}x{高}/?{关键词}&sig={随机数}

# 示例
https://source.unsplash.com/1600x900/?beijing,forbidden+city&sig=1
https://source.unsplash.com/1600x900/?shanghai,skyline&sig=2
https://source.unsplash.com/1600x900/?chengdu,panda&sig=3
https://source.unsplash.com/1600x900/?xian,terracotta+warriors&sig=4
https://source.unsplash.com/1600x900/?hangzhou,west+lake&sig=5
https://source.unsplash.com/1600x900/?xiamen,gulangyu+island&sig=6
https://source.unsplash.com/1600x900/?sanya,tropical+beach&sig=7
```

---

## LoremFlickr搜索URL（备选）

```
# 格式
https://loremflickr.com/{宽}/{高}/{关键词1},{关键词2}

# 示例
https://loremflickr.com/1200/800/beijing
https://loremflickr.com/1200/800/shanghai,skyline
https://loremflickr.com/1200/800/chengdu,panda
https://loremflickr.com/1200/800/xian,warriors
```

---

## 前端使用方式

### 方式1: 直接使用URL
```vue
<template>
  <el-image :src="cityImageUrl" fit="cover" />
</template>

<script setup>
const CITY_IMAGES = {
  '北京': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=1200&h=800&fit=crop',
  '上海': 'https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=1200&h=800&fit=crop',
  // ...
}
</script>
```

### 方式2: 使用API（当前可用）
```typescript
import { getDestinationImageWithCache } from '@/api/travel/images'

const imageUrl = await getDestinationImageWithCache('北京', 1200, 800)
```

### 方式3: 动态Unsplash搜索
```typescript
const getCityImage = (city: string, width = 1200, height = 800) => {
  const cityMap: Record<string, string> = {
    '北京': 'beijing,forbidden+city',
    '上海': 'shanghai,skyline',
    '成都': 'chengdu,panda',
    '西安': 'xian,terracotta+warriors',
    // ...
  }
  const keyword = cityMap[city] || city
  const sig = Math.floor(Math.random() * 1000)
  return `https://source.unsplash.com/${width}x${height}/?${keyword}&sig=${sig}`
}
```

---

## 服务状态

| 服务 | 地址 | 状态 |
|------|------|------|
| 后端API | http://localhost:8005 | ✅ 运行中 |
| 前端界面 | http://localhost:4001 | ✅ 运行中 |
| 图片API | /api/travel/images/destination/{city} | ✅ 可用 |
| LLM配置 | SiliconFlow | ⚠️ 需前端刷新验证 |

---

## 下一步建议

1. **刷新前端页面** - 按F5或Ctrl+R
2. **重新规划旅行** - 查看LLM评分是否启用
3. **如需更好的图片** - 可以在前端直接使用上面列出的高质量Unsplash URL

---

## 高质量图片URL示例（复制即可用）

| 城市 | URL |
|------|-----|
| 北京 | `https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=1200&h=800&fit=crop` |
| 上海 | `https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=1200&h=800&fit=crop` |
| 成都 | `https://images.unsplash.com/photo-1628163574848-46a263a4232b?w=1200&h=800&fit=crop` |
| 西安 | `https://images.unsplash.com/photo-1582573848606-38e674f3b683?w=1200&h=800&fit=crop` |
| 杭州 | `https://images.unsplash.com/photo-1569163139539-0e27c1d520bd?w=1200&h=800&fit=crop` |
| 厦门 | `https://images.unsplash.com/photo-1601572637264-fc19c9d2a86a?w=1200&h=800&fit=crop` |
| 三亚 | `https://images.unsplash.com/photo-1597327637774-d9f65c57e18b?w=1200&h=800&fit=crop` |
| 重庆 | `https://images.unsplash.com/photo-1547975719-0ec76a592802?w=1200&h=800&fit=crop` |

这些都是精选的高质量旅行摄影作品，直接复制到前端使用即可！
