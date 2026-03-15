# 优先级加载功能修复总结

## 问题诊断

### 根本原因
前端图片轮询不工作的原因是：**后端返回的数据中没有 `image_source` 字段**

前端轮询逻辑 (`DetailedGuide.vue`) 检查：
```javascript
if (item.image_source === 'preset') {
  // 触发更新
}
```

但是后端 `tool_enhanced_guide_generator.py` 只设置了 `imageUrl`，没有设置 `image_source` 字段。

### 诊断过程
1. ✅ 确认后端图片API正常工作 (端口8005, 3-4秒响应)
2. ✅ 确认前端轮询代码正确实现
3. ❌ 发现后端 `app/` 目录中完全没有 `image_source` 字段
4. ❌ 发现 `tool_enhanced_guide_generator.py` 缺少 `image_source` 字段

## 修复内容

### 文件：`tradingagents/services/tool_enhanced_guide_generator.py`

#### 1. 添加预设图片字典
```python
class ToolEnhancedGuideGenerator:
    PRESET_IMAGES = {
        "成都": {...},
        "杭州": {...},
        "北京": {...},
        "上海": {...},
        "新加坡": {...},
        "西安": {...},
    }
```

#### 2. 添加 `_get_preset_image()` 方法
```python
def _get_preset_image(self, attraction_name: str, city: str) -> str:
    """获取预设图片URL（快速返回，不调用API）"""
    # 精确匹配 -> 模糊匹配 -> 城市通用图 -> 默认图
```

#### 3. 添加 `_add_preset_images_fast()` 方法
```python
def _add_preset_images_fast(self, guide: Dict[str, Any]) -> Dict[str, Any]:
    """
    快速添加预设图片（不调用API）

    为所有景点添加预设图片，标记 image_source="preset"
    前端会识别这个标记并进行轮询更新
    """
```

**关键逻辑：**
- 跳过餐饮活动 (lunch/dinner)
- 跳过已有真实图片的项目 (`image_source == "api"`)
- 为其他景点添加预设图片和 `image_source="preset"` 标记

#### 4. 添加 `_fetch_real_images_for_guide()` 方法
```python
def _fetch_real_images_for_guide(self, guide: Dict[str, Any]) -> Dict[str, str]:
    """
    异步获取真实图片（用于后台任务）

    只获取标记为 preset 的景点，使用更长的超时时间
    """
```

**关键逻辑：**
- 只处理 `image_source == "preset"` 的项目
- 使用重试机制 (最多2次，尝试3个端口)
- 更新图片URL和 `image_source="api"`

#### 5. 添加 `_fetch_attraction_image_with_retry()` 方法
```python
def _fetch_attraction_image_with_retry(
    self, attraction_name: str, city: str, max_retries: int = 2
) -> str:
    """使用重试机制获取景点图片URL"""
```

#### 6. 修改 `generate_detailed_guide()` 方法
```python
def generate_detailed_guide(self, basic_guide: Dict[str, Any]) -> Dict[str, Any]:
    # ... 生成攻略内容 ...

    # 🔥 分优先级图片加载：立即添加预设图片（快速返回）
    detailed_guide = self._add_preset_images_fast(detailed_guide)

    # 💡 在后台线程中异步获取真实图片（不阻塞返回）
    def fetch_real_images_background():
        self._fetch_real_images_for_guide(detailed_guide)

    thread = threading.Thread(target=fetch_real_images_background, daemon=True)
    thread.start()

    return detailed_guide  # 立即返回
```

#### 7. 修改 `_generate_attraction_with_tools()` 方法
```python
# 2. 搜索景点图片
image_url = image_tool.search_attraction_image(location, destination)
if image_url:
    attraction_details["imageUrl"] = image_url
    attraction_details["image_source"] = "api"  # ✅ 新增：标记为API获取的真实图片
```

## 优先级加载流程

### 阶段1：快速响应 (3秒内)
1. 生成攻略内容
2. 为所有景点添加预设图片
3. 设置 `image_source="preset"`
4. 立即返回给前端

### 阶段2：后台增强 (3-30秒)
1. 后台线程启动
2. 收集所有 `image_source="preset"` 的景点
3. 并发调用图片API (去重：同一景点只调用一次)
4. 更新图片URL和 `image_source="api"`

### 阶段3：前端轮询 (可选)
- 前端每5秒检查一次图片更新
- 发现 `image_source="preset"` 时调用图片API
- 最多轮询6次 (30秒)

## 数据字段说明

### 攻略行程项目 (schedule item)
```javascript
{
  "period": "morning",           // 时段
  "activity": "游览圣淘沙",       // 活动名称
  "location": "圣淘沙",           // 地点
  "imageUrl": "https://...",      // 图片URL
  "image_source": "preset",       // ✅ 图片来源: "preset" | "api" | undefined
  "image_loading": false,         // 加载状态
  "has_real_image": false        // 是否有真实图片 (可选)
}
```

### image_source 值含义
- `"preset"`: 预设图片，前端应该轮询更新
- `"api"`: 真实图片，来自API或工具调用，不需要更新
- `undefined`: 未设置，通常用于餐饮项目

## 测试验证

### 测试脚本
```bash
python scripts/test_priority_loading.py
```

### 预期结果
```
✅ 模块导入成功
✅ 生成器创建成功
✅ 预设图片包含 6 个城市
✅ _get_preset_image() 正常工作
✅ 攻略生成成功
✅ image_source 字段正确设置
```

### 实际测试结果
```
Visit Sentosa: source=preset, has_url=True
Lunch: source=NOT_SET, has_url=False
Marina Bay: source=preset, has_url=True
```

## 兼容性说明

### 向后兼容
- 如果 `image_source` 不存在，前端会跳过该项目
- 旧的攻略数据仍然可以正常显示

### 降级策略
1. 如果工具API失败 → 使用预设图片
2. 如果预设图片不存在 → 使用城市通用图
3. 如果城市通用图不存在 → 使用默认图片

## 性能优化

### 去重机制
同一景点在多天行程中出现时，只调用一次API：
```python
if image_key not in attraction_indices:
    attractions_to_fetch.append(attraction_name)  # 只添加一次
attraction_indices[image_key].append((day_idx, item_idx))  # 记录所有位置
```

### 并发处理
- 使用线程池并发获取图片
- 最多3个端口尝试
- 5秒超时

## 相关文件

### 后端
- `tradingagents/services/tool_enhanced_guide_generator.py` (主要修改)
- `tradingagents/services/enhanced_guide_generator.py` (参考实现)

### 前端
- `frontend/src/views/travel/steps/DetailedGuide.vue` (轮询逻辑)

### API
- `GET /api/travel/images/attraction` (图片服务)

## 后续建议

1. **缓存机制**: 在Redis中缓存已获取的图片URL
2. **批量API**: 实现批量获取图片的API接口
3. **CDN加速**: 将常用图片上传到CDN
4. **进度反馈**: 后台图片获取进度通过WebSocket通知前端

## 更新日志

- 2025-03-16: 添加 `image_source` 字段支持
- 2025-03-16: 实现优先级加载 (预设图片 + 后台异步)
- 2025-03-16: 添加去重和重试机制
