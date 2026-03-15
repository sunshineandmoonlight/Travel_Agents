# LLM配置指南

## 问题诊断

如果您发现：
- 所有目的地的评分都相同（如80分）
- 所有目的地的预算都相同（如3000元）
- 智能体输出显示JSON格式而不是自然语言描述
- 后端日志显示 "使用规则计算"

**原因**: LLM API Key没有配置或配置不正确。

---

## 如何配置LLM

### 步骤1: 选择LLM提供商

系统支持以下LLM提供商（任选其一）：

| 提供商 | 推荐度 | 成本 | 获取API Key |
|--------|--------|------|-------------|
| **DeepSeek** | ⭐⭐⭐⭐⭐ | 便宜 | https://platform.deepseek.com/api_keys |
| OpenAI | ⭐⭐⭐⭐ | 中等 | https://platform.openai.com/api-keys |
| Google Gemini | ⭐⭐⭐⭐ | 便宜 | https://aistudio.google.com/app/apikey |
| 阿里云通义千问 | ⭐⭐⭐ | 便宜 | https://dashscope.console.aliyun.com/apiKey |

### 步骤2: 获取API Key

以DeepSeek为例（推荐）：
1. 访问 https://platform.deepseek.com/
2. 注册账号
3. 进入 API Keys 页面
4. 创建新的API Key
5. 复制API Key（格式如：`sk-xxxxxxxxxxxx`）

### 步骤3: 配置.env文件

打开项目根目录的 `.env` 文件，找到LLM配置部分：

```bash
# ============================================================
# LLM配置
# ============================================================
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_key_here
OPENAI_BASE_URL=
OPENAI_MODEL=gpt-3.5-turbo

DEEPSEEK_API_KEY=your_deepseek_key_here
DEEPSEEK_MODEL=deepseek-chat

GOOGLE_API_KEY=your_google_key_here
DASHSCOPE_API_KEY=your_dashscope_key_here
```

根据您选择的提供商，修改对应的配置：

#### 选项A: 使用DeepSeek（推荐）

```bash
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-你的实际API_Key
DEEPSEEK_MODEL=deepseek-chat
```

#### 选项B: 使用OpenAI

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-你的实际API_Key
OPENAI_MODEL=gpt-3.5-turbo
```

#### 选项C: 使用Google Gemini

```bash
LLM_PROVIDER=google
GOOGLE_API_KEY=你的实际API_Key
OPENAI_MODEL=gemini-pro
```

#### 选项D: 使用阿里云通义千问

```bash
LLM_PROVIDER=dashscope
DASHSCOPE_API_KEY=sk-你的实际API_Key
OPENAI_MODEL=qwen-turbo
```

### 步骤4: 重启服务

配置完成后，必须重启后端服务才能生效：

```bash
# 停止当前运行的服务
# 然后重新启动
cd app && python -m uvicorn main:app --reload --port 8005
```

### 步骤5: 验证配置

运行测试脚本验证配置是否成功：

```bash
python scripts/test_llm_config.py
```

如果配置成功，您会看到：
```
✅ 有有效的LLM配置
✅ OpenAI LLM创建成功
✅ LLM调用成功
```

---

## 智能体LLM使用说明

### 智能体会自动使用LLM

当LLM配置正确后，以下智能体会自动使用LLM：

**Group A - 地区推荐智能体**:
1. UserRequirementAnalyst - 生成详细的用户画像描述
2. DestinationMatcher - 使用LLM计算匹配分数和估算预算
3. RankingScorer - 使用LLM生成推荐理由

**Group B - 风格设计智能体**:
4. StyleDesigner - 使用LLM设计旅行风格
5. ...

**Group C - 行程规划智能体**:
6. AttractionScheduler - 使用LLM安排景点
7. TransportPlanner - 使用LLM规划交通
8. DiningRecommender - 使用LLM推荐餐厅
9. AccommodationAdvisor - 使用LLM推荐住宿
10. LLMGuideWriter - 使用LLM撰写攻略

### 规则引擎Fallback

如果LLM不可用（未配置或调用失败），系统会自动降级到规则引擎：
- ✅ 系统仍可正常运行
- ⚠️ 但个性化程度降低
- ⚠️ 输出内容会偏向模板化

---

## 日志说明

### LLM正常工作时
```
✅ [LLM] LLM实例创建成功!
   Provider: deepseek
   Model: deepseek-chat
   智能体将使用LLM进行智能分析和生成
🤖 [LLM] 使用LLM计算 成都 的匹配分数...
🤖 [LLM] 使用LLM估算 成都 的预算...
```

### LLM未配置时
```
❌ [LLM] LLM实例创建失败: 使用DeepSeek需要设置DEEPSEEK_API_KEY...
⚠️ [规则引擎] 系统将使用规则引擎运行，智能体功能受限
⚙️ [规则引擎] 使用规则计算 成都 的匹配分数 (LLM未配置或失败)
```

---

## 常见问题

### Q: 我看到日志显示 "LLM评分失败"？
A: 检查API Key是否正确，网络是否可以访问LLM服务。

### Q: 配置了但还是用规则引擎？
A:
1. 确认.env文件中的API Key不是占位符（如`your_openai_key_here`）
2. 确认重启了后端服务
3. 运行`python scripts/test_llm_config.py`诊断问题

### Q: DeepSeek便宜吗？
A: 是的，DeepSeek非常便宜：
- 输入: ¥1/百万tokens
- 输出: ¥2/百万tokens
- 新用户通常有免费额度

### Q: 可以同时配置多个LLM吗？
A: 可以，但系统只会使用`LLM_PROVIDER`指定的那一个。其他配置会被忽略。

---

## 代码中的LLM调用模式

所有智能体的LLM调用都遵循以下模式：

```python
def some_agent_function(data, llm=None):
    # 如果有LLM，使用LLM
    if llm:
        try:
            prompt = "..."
            response = llm.invoke([HumanMessage(content=prompt)])
            return parse_llm_response(response)
        except Exception as e:
            logger.warning(f"LLM失败: {e}")

    # 降级到规则引擎
    return rule_based_logic(data)
```

这确保了：
- ✅ 有LLM时使用智能分析
- ✅ LLM失败时系统仍可运行
- ✅ 用户体验不受影响
