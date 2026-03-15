# 项目API使用完整清单

## 🤖 大语言模型 (LLM) API

### 1. DeepSeek API
- **环境变量**: `DEEPSEEK_API_KEY`
- **用途**: 主要AI推理引擎
- **模型**: DeepSeek-V3
- **特点**: 性价比极高，国产模型，推荐使用
- **配置**: `DEEPSEEK_BASE_URL=https://api.deepseek.com`

### 2. 阿里百炼 / DashScope API
- **环境变量**: `DASHSCOPE_API_KEY`
- **用途**: 备用AI推理引擎，国产稳定
- **模型**: 通义千问系列
- **特点**: 阿里云服务，国内访问稳定

### 3. OpenAI API
- **环境变量**: `OPENAI_API_KEY`
- **用途**: 国际AI模型（需国外网络）
- **模型**: GPT-3.5/GPT-4
- **特点**: 需要有效的API密钥格式验证

### 4. Google AI API
- **环境变量**: `GOOGLE_API_KEY`
- **用途**: Gemini模型
- **特点**: 可选，提供更多模型选择

### 5. 硅基流动 API
- **环境变量**: `SILICONFLOW_API_KEY`
- **用途**: 备用AI推理
- **特点**: 可选，国内聚合平台

## 🏛️ 旅游数据 API

### 1. 天行数据 API (TianAPI)
- **环境变量**: `TIANAPI_KEY`
- **用途**: 中国国内旅游景点数据库
- **功能**:
  - 获取城市景点列表
  - 景点详情查询
  - 景点描述和子景点信息
- **文档**: `tradingagents/integrations/tianapi_client.py`
- **应用**: LLMGuideWriter使用真实景点数据生成攻略

### 2. 高德地图 API (Amap)
- **环境变量**: `AMAP_API_KEY`
- **用途**: 中国旅游数据
- **功能**:
  - POI景点搜索
  - 天气查询
  - 路径规划
- **文档**: `tradingagents/integrations/amap_client.py`
- **限制**: 仅限中国境内

### 3. SerpAPI
- **环境变量**: `SERPAPI_KEY`
- **用途**: Google搜索结果API
- **功能**:
  - Google Places景点搜索
  - 酒店搜索
  - 餐厅搜索
- **文档**: `tradingagents/integrations/serpapi_client.py`
- **应用**: 国际旅游数据获取

### 4. OpenTripMap API
- **环境变量**: `OPENTRIPMAP_API_KEY` (可选)
- **用途**: 国际旅游景点数据
- **功能**:
  - 全球景点搜索
  - 景点详情
  - 周边景点推荐
- **特点**: 完全免费，有免费API Key
- **文档**: `tradingagents/integrations/opentripmap_client.py`

### 5. RestCountries API
- **用途**: 国家信息查询
- **功能**:
  - 国家基本信息
  - 货币、语言、时区
  - 邻国信息
- **特点**: 完全免费，无需API Key
- **文档**: `tradingagents/integrations/restcountries_client.py`

## 🖼️ 图片服务 API

### 1. Unsplash API
- **环境变量**: `UNSPLASH_ACCESS_KEY`
- **用途**: 高质量免费图片
- **功能**:
  - 按关键词搜索图片
  - 景点图片获取
  - 城市风光图
- **特点**: 无版权限制，图片质量高
- **文档**: `tradingagents/services/attraction_image_service.py`

### 2. Pexels API
- **环境变量**: `PEXELS_API_KEY`
- **用途**: 免版权图片备用源
- **功能**:
  - 视频和图片搜索
  - 按颜色、方向筛选
- **特点**: 免费商用，无需署名
- **文档**: `tradingagents/services/attraction_image_service.py`

## 🌤️ 天气服务 API

### 1. Open-Meteo API
- **用途**: 天气预报数据
- **功能**:
  - 7天天气预报
  - 历史天气数据
  - 气候统计
- **特点**: 完全免费，无需API Key
- **文档**: `tradingagents/integrations/openmeteo_client.py`

### 2. 高德地图天气 API
- **环境变量**: `AMAP_API_KEY`
- **用途**: 中国天气查询
- **特点**: 与高德地图API共用密钥

## 💱 其他服务 API

### 1. Exchange Rate API
- **用途**: 汇率转换
- **功能**:
  - 实时汇率查询
  - 多货币转换
- **文档**: `tradingagents/integrations/exchange_rate_client.py`

## 📊 API使用优先级

### 必需API (至少配置一个)
1. **LLM API** (选一个):
   - DeepSeek API (推荐)
   - DashScope API
   - OpenAI API

### 推荐API (提升体验)
1. **TianAPI** - 国内真实景点数据
2. **Unsplash API** - 高质量图片
3. **SerpAPI** - 国际旅游数据

### 可选API (增强功能)
1. **高德地图API** - 国内POI和天气
2. **OpenTripMap** - 国际景点数据
3. **Pexels API** - 图片备用源

## 🔑 API密钥获取指南

### LLM API密钥
1. **DeepSeek**: https://platform.deepseek.com/
2. **DashScope**: https://dashscope.aliyun.com/
3. **OpenAI**: https://platform.openai.com/

### 旅游数据API密钥
1. **TianAPI**: https://www.tianapi.com/
2. **高德地图**: https://lbs.amap.com/
3. **SerpAPI**: https://serpapi.com/

### 图片API密钥
1. **Unsplash**: https://unsplash.com/developers
2. **Pexels**: https://www.pexels.com/api/

## 📝 配置建议

### 最小配置（仅基础功能）
```bash
# 必需：至少一个LLM API
DEEPSEEK_API_KEY=your_deepseek_key_here
```

### 推荐配置（国内旅行优化）
```bash
# LLM
DEEPSEEK_API_KEY=your_deepseek_key_here

# 国内数据
TIANAPI_KEY=your_tianapi_key_here
AMAP_API_KEY=your_amap_key_here

# 图片
UNSPLASH_ACCESS_KEY=your_unsplash_key_here
```

### 完整配置（全功能）
```bash
# LLM (多个备用)
DEEPSEEK_API_KEY=your_deepseek_key_here
DASHSCOPE_API_KEY=your_dashscope_key_here
OPENAI_API_KEY=your_openai_key_here

# 旅游数据
TIANAPI_KEY=your_tianapi_key_here
AMAP_API_KEY=your_amap_key_here
SERPAPI_KEY=your_serpapi_key_here

# 图片
UNSPLASH_ACCESS_KEY=your_unsplash_key_here
PEXELS_API_KEY=your_pexels_key_here
```

## ⚠️ 注意事项

1. **API频率限制**: 免费API都有调用频率限制
2. **成本控制**: LLM API按token计费，注意使用量
3. **网络访问**: OpenAI等需要国外网络
4. **密钥安全**: 不要将真实密钥提交到代码仓库
5. **备用方案**: 建议配置同类型的多个API作为备用

## 📚 相关文档

- 天行数据集成: `docs/travel_project/TIANAPI_INTEGRATION_COMPLETE.md`
- 图片服务指南: `docs/travel_project/IMAGE_SERVICE_GUIDE.md`
- LLM配置指南: `docs/LLM_CONFIG_GUIDE.md`
