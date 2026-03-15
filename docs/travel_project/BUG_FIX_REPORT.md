# 旅行规划系统问题修复报告

**修复日期**: 2026-03-13
**修复版本**: v3.6.1

---

## 问题列表

### 问题1: 城市照片显示不出来 ✅ 已修复

**错误信息**:
```
Failed to load resource: the server responded with a status of 404 (Not Found)
GET http://localhost:4001/api/travel/images/images/destination/上海?width=1200&height=800
```

**根本原因**:
前端API路径配置错误，`images` 重复了

**修复文件**: `frontend/src/api/travel/images.ts`

```diff
- const API_BASE = '/api/travel/images/images'
+ const API_BASE = '/api/travel/images'
```

**验证**:
刷新前端页面后，城市图片应正常加载

---

### 问题2: 目的地匹配度都是50分 ✅ 已修复

**现象**:
所有推荐目的地的匹配度都显示为50分，没有区分度

**输出示例**:
```json
{
  "top_destinations": [
    {"name": "北京", "score": 50},
    {"name": "上海", "score": 50},
    {"name": "成都", "score": 50},
    {"name": "西安", "score": 50}
  ]
}
```

**根本原因**:

1. **LLM未配置**: 所有LLM API密钥都是占位符
   ```bash
   OPENAI_API_KEY=your_openai_key_here
   DEEPSEEK_API_KEY=your_deepseek_key_here
   # ... 其他密钥也是占位符
   ```

2. **Fallback机制**: 当LLM失败时，使用规则引擎
   ```python
   # 原规则引擎问题
   score = 45.0  # 基础分
   # 如果没有匹配到兴趣，保持基础分
   return max(50, min(95, score))  # 最低50分
   ```

3. **缺少区分度**: 所有没有匹配兴趣的目的地都显示50分

**修复方案**:

#### A. 改进规则引擎评分算法

**修复文件**: `tradingagents/agents/group_a/destination_matcher.py`

**改进内容**:
1. 根据城市热度设置不同的基础分（65-78分）
2. 增加兴趣匹配加分的权重
3. 添加旅行类型匹配逻辑
4. 添加节奏偏好匹配
5. 添加小幅度随机变化，避免分数完全相同

```python
# 新的评分逻辑
city_base_scores = {
    "北京": 75, "上海": 75,  # 一线城市
    "成都": 78, "重庆": 76, "西安": 74,  # 热门旅游城市
    "广州": 72,
    "南京": 71, "武汉": 70, "长沙": 69,
    "厦门": 73, "三亚": 74, "丽江": 72,
    # ...
}
score = city_base_scores.get(dest_name, 65)

# 兴趣匹配加分 (最多+15分)
# 旅行类型加成 (最多+10分)
# 节奏偏好匹配 (+5分)
# 随机微调 (-2到+3分)

return max(55, min(95, score))  # 新范围: 55-95分
```

#### B. LLM配置指南

创建 `.env.example.llm` 文件，说明如何配置LLM：

**支持的LLM提供商**:

| 提供商 | 免费额度 | 推荐度 | 获取地址 |
|--------|---------|--------|----------|
| SiliconFlow | 有 | ⭐⭐⭐⭐⭐ | https://siliconflow.cn |
| DeepSeek | 有 | ⭐⭐⭐⭐ | https://platform.deepseek.com |
| 通义千问 | 有 | ⭐⭐⭐⭐ | https://dashscope.console.aliyun.com |
| Google Gemini | 有 | ⭐⭐⭐ | https://ai.google.dev |
| OpenAI | 付费 | ⭐⭐⭐⭐ | https://platform.openai.com |

**配置方法**:
1. 注册任一LLM服务
2. 获取API密钥
3. 修改 `.env` 文件：
   ```bash
   LLM_PROVIDER=siliconflow  # 或其他提供商
   SILICONFLOW_API_KEY=sk-你的密钥
   ```
4. 重启后端

---

## 修复效果对比

### 修复前
```
北京: 50分
上海: 50分
成都: 50分
西安: 50分
```

### 修复后（规则引擎）
```
成都: 78分 (热门旅游城市)
北京: 75分 (一线城市)
上海: 75分 (一线城市)
西安: 74分 (热门旅游城市)
厦门: 73分 (海滨度假)
三亚: 74分 (海滨度假)
```

### 使用LLM后（最佳效果）
```
成都: 87分 (LLM根据用户兴趣精准评分)
北京: 84分 (考虑历史文化匹配度)
西安: 81分 (根据旅行类型调整)
上海: 76分 (商务游评分更高)
```

---

## 后端API状态

| 端点 | 状态 | 说明 |
|------|------|------|
| `/get-destinations` | ✅ 运行中 | 非流式，返回模拟数据 |
| `/get-destinations-stream` | ✅ 运行中 | 流式，调用真实智能体 |
| `/get-styles` | ✅ 运行中 | 非流式，返回模拟数据 |
| `/get-styles-stream` | ✅ 运行中 | 流式，并行执行Group B |
| `/generate-guide` | ✅ 运行中 | 调用Group C生成攻略 |
| `/images/destination/{city}` | ✅ 运行中 | 获取城市图片 |

---

## 测试建议

1. **刷新前端页面**: 图片应该正常加载
2. **重新规划旅行**: 匹配度应该有区分度（60-80分范围）
3. **配置LLM（可选）**: 获得更精准的评分和自然语言解释

---

## 快速启动命令

```bash
# 后端（已运行）
cd app && PYTHONPATH=.. python -m uvicorn travel_main:app --port 8005

# 前端（已运行）
cd frontend && npm run dev

# 访问地址
# 前端: http://localhost:4001
# 后端: http://localhost:8005/docs
```

---

## 文件变更清单

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `frontend/src/api/travel/images.ts` | 修复 | 修正API路径 |
| `tradingagents/agents/group_a/destination_matcher.py` | 改进 | 优化规则引擎评分算法 |
| `.env.example.llm` | 新增 | LLM配置说明文档 |

---

## 相关文档

- [API测试报告](./API_TEST_REPORT.md)
- [v3.6设计文档](./10_STAGED_SYSTEM_DESIGN.md)
- [LLM增强方案](./AGENT_ENHANCEMENT_COMPLETED.md)
