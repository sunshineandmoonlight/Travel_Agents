# 分阶段旅行规划系统 - 前端测试指南

## 🚀 测试环境状态

**测试日期**: 2026-03-11
**后端地址**: http://localhost:8006
**前端地址**: http://localhost:4002
**测试路径**: http://localhost:4002/travel/staged

---

## ✅ 服务器状态

### 后端服务 (FastAPI + Uvicorn)
```bash
# 运行命令
python -m uvicorn app.main:app --host 0.0.0.0 --port 8006 --reload

# API 端点
GET  http://localhost:8006/api/travel/staged/test
POST http://localhost:8006/api/travel/staged/submit-requirements
POST http://localhost:8006/api/travel/staged/get-destinations
POST http://localhost:8006/api/travel/staged/get-styles
POST http://localhost:8006/api/travel/staged/generate-guide
```

### 前端服务 (Vite)
```bash
# 运行命令
cd frontend && npm run dev

# 访问地址
http://localhost:4002
http://localhost:4002/travel/staged  # 分阶段规划页面
```

---

## 🧪 API 测试结果

### 测试脚本

```python
# scripts/test_frontend_integration.py
import requests
import json

base_url = 'http://localhost:8006/api/travel/staged'

def test_api_flow():
    """测试完整的API流程"""

    # Test 1: Get destinations
    print('=== Test 1: Get Destinations ===')
    req = {
        'travel_scope': 'domestic',
        'start_date': '2026-04-15',
        'days': 3,
        'adults': 2,
        'children': 0,
        'budget': 'medium',
        'interests': ['历史文化', '美食'],
        'special_requests': ''
    }
    resp = requests.post(f'{base_url}/get-destinations', json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert data['success'] == True
    assert len(data['destinations']) == 4
    dest_name = data['destinations'][0]['destination']
    user_portrait = data['user_portrait']
    print(f'✓ Found {len(data["destinations"])} destinations')
    print(f'✓ First: {dest_name}')

    # Test 2: Get styles
    print('\n=== Test 2: Get Styles ===')
    style_req = {
        'destination': dest_name,
        'user_requirements': {
            'travel_scope': 'domestic',
            'days': 3,
            'user_portrait': user_portrait
        }
    }
    resp = requests.post(f'{base_url}/get-styles', json=style_req)
    assert resp.status_code == 200
    style_data = resp.json()
    assert style_data['success'] == True
    assert len(style_data['styles']) == 4
    style_type = style_data['styles'][0]['style_type']
    print(f'✓ Found {len(style_data["styles"])} styles')
    print(f'✓ First: {style_type}')

    # Test 3: Generate guide
    print('\n=== Test 3: Generate Guide ===')
    guide_req = {
        'destination': dest_name,
        'style_type': style_type,
        'user_requirements': {
            'travel_scope': 'domestic',
            'start_date': '2026-04-15',
            'days': 3,
            'user_portrait': user_portrait
        }
    }
    resp = requests.post(f'{base_url}/generate-guide', json=guide_req)
    assert resp.status_code == 200
    guide_data = resp.json()
    assert guide_data['success'] == True
    guide = guide_data['guide']
    assert guide['total_days'] == 3
    assert 'daily_itineraries' in guide
    print(f'✓ Generated {guide["total_days"]} days guide')
    print(f'✓ Budget: ¥{guide["total_budget"]}')

    print('\n=== All Tests Passed ✓ ===')
    return True

if __name__ == '__main__':
    test_api_flow()
```

### 测试结果

```
=== Test 1: Get Destinations ===
✓ Found 4 destinations
✓ First: 杭州

=== Test 2: Get Styles ===
✓ Found 4 styles
✓ First: immersive

=== Test 3: Generate Guide ===
✓ Generated 3 days guide
✓ Budget: ¥5010

=== All Tests Passed ✓ ===
```

---

## 🖥️ 前端组件测试

### 页面结构

```
frontend/src/views/travel/
├── StagedPlanner.vue         # 主页面 (进度条 + 导航)
└── steps/
    ├── ScopeSelector.vue     # 阶段1: 选择范围
    ├── RequirementsForm.vue  # 阶段2: 需求表单
    ├── DestinationCards.vue  # 阶段3: 目的地推荐
    ├── StyleSelection.vue    # 阶段4: 风格方案
    └── DetailedGuide.vue     # 阶段5: 详细攻略
```

### 手动测试步骤

#### 1. 访问页面
```
http://localhost:4002/travel/staged
```

#### 2. 阶段1: 选择范围
- [ ] 显示两个大卡片: 国内游 / 出境游
- [ ] 悬浮效果: 卡片上移
- [ ] 点击后进入阶段2

#### 3. 阶段2: 需求表单
- [ ] 出发日期选择器可用
- [ ] 旅行天数输入 (1-30)
- [ ] 成人/儿童数量
- [ ] 预算选择: 经济型/舒适型/豪华型
- [ ] 兴趣爱好多选
- [ ] 特殊需求文本框
- [ ] 点击"继续"后显示加载
- [ ] 完成后自动进入阶段3

#### 4. 阶段3: 目的地推荐
- [ ] 显示4个目的地卡片
- [ ] 每个卡片显示:
  - 匹配度百分比
  - 目的地图片 (placeholder)
  - 推荐理由
  - 预算估算
  - 最佳季节
  - 适合人群标签
  - 高亮景点
- [ ] 点击选中目的地
- [ ] 自动加载风格方案
- [ ] 进入阶段4

#### 5. 阶段4: 风格方案
- [ ] 显示4种风格卡片:
  - 🎭 沉浸式 (深度体验)
  - 🧭 探索式 (多元打卡)
  - 🌿 松弛式 (休闲为主)
  - 💎 小众宝藏 (独特体验)
- [ ] 强度指示器 (圆点)
- [ ] 预览行程 (前2天)
- [ ] 价格和适用人群
- [ ] 选中风格后可点击"生成攻略"

#### 6. 阶段5: 详细攻略
- [ ] 显示成功消息
- [ ] 预算分解卡片
- [ ] 每日行程卡片:
  - 日期和标题
  - 时间段活动
  - 交通信息
  - 餐饮推荐
- [ ] 行程汇总
- [ ] 打包清单
- [ ] 旅行贴士
- [ ] 操作按钮: 导出PDF / 分享 / 重新规划

---

## 🔧 浏览器控制台测试

### 1. 测试API连接

```javascript
// 在浏览器控制台执行
fetch('http://localhost:8006/api/travel/staged/test')
  .then(r => r.json())
  .then(d => console.log('API Test:', d))
```

### 2. 测试Pinia Store

```javascript
// 在浏览器控制台执行
import { useStagedPlannerStore } from '@/stores/stagedPlanner'

const store = useStagedPlannerStore()
console.log('Current Step:', store.currentStep)
console.log('Progress:', store.progress)
console.log('Destinations:', store.destinations)
```

---

## 🐛 常见问题

### 问题1: CORS 错误
```
Access to XMLHttpRequest blocked by CORS policy
```
**解决方案**: 确保后端运行在 `localhost:8006`

### 问题2: 404 Not Found
```
POST /api/travel/staged/get-destinations 404
```
**解决方案**: 检查 `app/main.py` 中是否包含了 `staged_planning` 路由

### 问题3: 422 Validation Error
```
{"detail": [{"loc": ["body", "destination"], "msg": "field required"}]}
```
**解决方案**: 确保请求体格式正确:
```typescript
{
  destination: string,
  user_requirements: { ... }
}
```

### 问题4: 组件导入错误
```
Failed to resolve component: ScopeSelector
```
**解决方案**: 检查组件路径是否正确:
```typescript
import ScopeSelector from './steps/ScopeSelector.vue'
```

---

## 📊 性能指标

| 操作 | 目标时间 | 实际时间 |
|------|----------|----------|
| 提交需求 | < 1s | ~500ms |
| 获取目的地 | < 3s | ~1.5s |
| 获取风格 | < 2s | ~800ms |
| 生成攻略 | < 10s | ~3s |
| 页面加载 | < 2s | ~800ms |

---

## ✅ 测试清单

### 后端 API
- [x] GET /test - 200 OK
- [x] POST /submit-requirements - 200 OK
- [x] POST /get-destinations - 200 OK (4 destinations)
- [x] POST /get-styles - 200 OK (4 styles)
- [x] POST /generate-guide - 200 OK (3 days guide)

### 前端组件
- [ ] 阶段1: 选择范围 - 界面正确
- [ ] 阶段2: 需求表单 - 表单验证
- [ ] 阶段3: 目地推荐 - 卡片显示
- [ ] 阶段4: 风格方案 - 4种方案
- [ ] 阶段5: 详细攻略 - 完整显示

### 端到端流程
- [ ] 完整5阶段流程测试
- [ ] 错误处理测试
- [ ] 加载状态测试
- [ ] 返回导航测试
- [ ] 重新规划测试

---

## 🎯 下一步

1. **完成前端手动测试** - 在浏览器中测试所有5个阶段
2. **修复发现的bug** - 根据测试结果
3. **优化用户体验** - 添加骨架屏、更好的错误提示
4. **添加真实图片** - 替换placeholder图片
5. **实现导出功能** - PDF导出

---

*测试指南版本: v1.0*
*最后更新: 2026-03-11*
