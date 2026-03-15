# Unsplash API 图片获取指南

## 问题解决

### 1. 404问题 - 已修复

**原因**: Unsplash图片URL需要包含 `ixlib` 参数

**修复前**:
```
https://images.unsplash.com/photo-1511739001486-6bfe10ce7859?w=800&q=80
```

**修复后**:
```
https://images.unsplash.com/photo-1511739001486-6bfe10ce7859?ixlib=rb-4.0.3&q=80&w=800
```

### 2. LoremFlickr相关性问题 - 解决方案

**问题**: LoremFlickr只基于城市关键词，与具体景点相关性较弱

**解决方案**: 使用Unsplash API搜索，支持"景点+城市"的精确搜索

---

## Unsplash API 使用方法

### 1. 获取Access Key

1. 访问 https://unsplash.com/developers
2. 注册开发者账号
3. 创建新应用获取 Access Key
4. 设置环境变量:
   ```bash
   export UNSPLASH_ACCESS_KEY="your_access_key_here"
   ```

### 2. 免费额度

- **每小时**: 50次请求
- **每月**: 5000次请求
- 对于个人项目完全够用

### 3. API使用示例

#### 搜索埃菲尔铁塔图片

```bash
curl "https://api.unsplash.com/search/photos?query=eiffel%20tower%20paris&per_page=1&orientation=landscape" \
  -H "Authorization: Client-ID YOUR_ACCESS_KEY"
```

#### 响应格式

```json
{
  "results": [
    {
      "id": "pFqrYbhIAXs",
      "urls": {
        "raw": "https://images.unsplash.com/photo-xxx?ixlib=rb-...",
        "full": "https://images.unsplash.com/photo-xxx?ixlib=rb-...",
        "regular": "https://images.unsplash.com/photo-xxx?ixlib=rb-...",
        "small": "https://images.unsplash.com/photo-xxx?ixlib=rb-...",
        "thumb": "https://images.unsplash.com/photo-xxx?ixlib=rb-..."
      },
      "user": {
        "username": "photographer_name",
        "name": "Photographer Name"
      },
      "location": {
        "name": "Paris, France",
        "city": "Paris"
      }
    }
  ]
}
```

---

## 代码集成

### 使用新的图片服务

```python
from tradingagents.services.attraction_image_service import get_attraction_image

# 现在支持Unsplash API搜索
url = get_attraction_image("某个冷门景点", "巴黎")

# 优先级:
# 1. Unsplash API搜索 (如果有密钥) - 最精准 ⭐⭐⭐⭐⭐
# 2. 预定义精选图 - 热门景点 ⭐⭐⭐⭐⭐
# 3. LoremFlickr - 关键词搜索 ⭐⭐⭐
# 4. Picsum - 随机备用 ⭐⭐
```

### Unsplash API Python实现

```python
import requests
import os

def search_unsplash(query: str, access_key: str = None) -> str:
    """
    使用Unsplash API搜索图片

    Args:
        query: 搜索关键词，如 "eiffel tower paris"
        access_key: Unsplash Access Key

    Returns:
        图片URL
    """
    access_key = access_key or os.getenv("UNSPLASH_ACCESS_KEY")

    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "per_page": 1,
        "orientation": "landscape"
    }
    headers = {
        "Authorization": f"Client-ID {access_key}"
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data.get("results"):
            photo = data["results"][0]
            raw_url = photo["urls"]["regular"]
            # 确保URL包含ixlib参数
            if "ixlib=" not in raw_url:
                raw_url = f"{raw_url}?ixlib=rb-4.0.3&q=80&w=800"
            return raw_url

    return None
```

---

## 验证图片URL

### 测试修复后的URL

| 景点 | 修复后的URL（可直接打开） |
|------|----------------------|
| 埃菲尔铁塔 | [点击查看](https://images.unsplash.com/photo-1511739001486-6bfe10ce7859?ixlib=rb-4.0.3&q=80&w=800) |
| 伦敦大本钟 | [点击查看](https://images.unsplash.com/photo-1529655683826-aba9b3e77383?ixlib=rb-4.0.3&q=80&w=800) |
| 自由女神 | [点击查看](https://images.unsplash.com/photo-1503731404080-6ac4c707c626?ixlib=rb-4.0.3&q=80&w=800) |
| 北京故宫 | [点击查看](https://images.unsplash.com/photo-1508804185872-d7badad00f7d?ixlib=rb-4.0.3&q=80&w=800) |
| 东京塔 | [点击查看](https://images.unsplash.com/photo-1536098561742-ca998e48cbcc?ixlib=rb-4.0.3&q=80&w=800) |

### Unsplash API搜索测试

配置API Key后，可以测试实时搜索：

```python
# 搜索 "paris eiffel tower"
search_unsplash("paris eiffel tower")

# 搜索 "tokyo travel"
search_unsplash("tokyo travel")

# 搜索 "sydney opera house"
search_unsplash("sydney opera house")
```

---

## 推荐方案总结

### 有Unsplash API Key（推荐）

```
Unsplash API搜索 → 预定义精选图 → LoremFlickr → Picsum
```

- **相关性**: ⭐⭐⭐⭐⭐ (精确搜索)
- **稳定性**: ⭐⭐⭐⭐⭐
- **成本**: 免费（有配额限制）

### 无Unsplash API Key

```
预定义精选图 → LoremFlickr → Picsum
```

- **相关性**: ⭐⭐⭐ (热门景点精准，冷门景点一般)
- **稳定性**: ⭐⭐⭐⭐⭐
- **成本**: 完全免费

---

## 配置步骤

### 1. 获取Unsplash Access Key

```
1. 访问 https://unsplash.com/developers
2. 点击 "New Application"
3. 填写应用信息（可以是个人项目）
4. 获取 Access Key
```

### 2. 配置环境变量

在 `.env` 文件中添加:
```
UNSPLASH_ACCESS_KEY=your_actual_access_key_here
```

### 3. 验证配置

```bash
# 测试API是否工作
curl "https://api.unsplash.com/search/photos?query=paris&per_page=1" \
  -H "Authorization: Client-ID YOUR_ACCESS_KEY"
```

---

## 更新后的文件

| 文件 | 说明 |
|------|------|
| `tradingagents/services/attraction_image_service.py` | 更新URL格式，支持Unsplash API |
| `tradingagents/services/unsplash_image_service.py` | Unsplash API专用服务 |

所有预定义图片URL已更新为正确格式（包含 `ixlib=rb-4.0.3` 参数）
