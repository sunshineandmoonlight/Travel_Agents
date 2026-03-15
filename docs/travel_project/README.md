# 智能旅行规划系统 (TravelAgents-CN)

> 基于多智能体架构的AI旅行规划系统

## 项目概述

TravelAgents-CN 是一个基于 LangGraph 多智能体架构的智能旅行规划系统，通过多个专业化Agent协作完成从需求分析到攻略生成的全流程自动化旅行规划。

### 核心特性

- 🤖 **多智能体协作** - 10+ 专业化Agent协同工作
- 🧠 **LLM驱动决策** - 智能需求分析与个性化推荐
- 🌍 **全球化支持** - 国内+国际目的地覆盖
- 📊 **实时数据集成** - 天行数据景点库、OpenTripMap、Unsplash
- 🎯 **智能推荐引擎** - 基于用户画像的精准匹配
- 📄 **多格式导出** - PDF、Word、Markdown攻略导出
- ⚡ **异步处理** - Celery + Redis 后台任务队列

## 系统架构

### 架构图

项目包含完整的系统架构图，使用 draw.io 格式保存：

- **[系统架构图](./diagrams/01_system_architecture.drawio)** - 展示前端、API、业务逻辑、数据层的完整架构
- **[智能体协作流程图](./diagrams/02_agent_flow.drawio)** - 展示各智能体之间的协作关系
- **[数据流设计图](./diagrams/03_data_flow.drawio)** - 展示数据在系统中的流动

### 使用图表

访问 [app.diagrams.net](https://app.diagrams.net) → 打开 `.drawio` 文件即可查看和编辑。

详细的图表使用说明请参考: **[Draw.io 使用指南](./diagrams/README.md)**

### 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端层 (Vue 3)                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │ 需求收集    │ │ 目的地展示  │ │ 攻略生成    │ │ 攻略中心  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP/SSE
┌──────────────────────────────▼──────────────────────────────────┐
│                       API层 (FastAPI)                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │ 旅行规划API │ │ 异步任务API │ │ 缓存API     │ │ 导出API   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                      业务逻辑层 (Python)                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              多智能体协调层 (LangGraph)                     │ │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐  │ │
│  │  │需求分析│→│目的地  │→│行程    │→│景点    │→│攻略    │  │ │
│  │  │Agent   │ │匹配    │ │规划    │ │设计师  │ │生成    │  │ │
│  │  │        │ │Agent   │ │Agent   │ │Agent   │ │Agent   │  │ │
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   Group B 智能体                            │ │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐             │ │
│  │  │景点    │ │酒店    │ │餐厅    │ │交通    │             │ │
│  │  │推荐    │ │推荐    │ │推荐    │ │规划    │             │ │
│  │  └────────┘ └────────┘ └────────┘ └────────┘             │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   Group C 智能体                            │ │
│  │  ┌────────┐ ┌────────┐ ┌────────┐                         │ │
│  │  │目的地  │ │预算    │ │LLM攻略 │                         │ │
│  │  │情报    │ │分析    │ │生成    │                         │ │
│  │  └────────┘ └────────┘ └────────┘                         │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                        数据层                                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │ MongoDB     │ │ Redis       │ │ 天行数据    │ │ Unsplash  │ │
│  │ (数据存储)  │ │ (缓存/队列) │ │ (景点库)    │ │ (图片)    │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 智能体架构

### Group A - 分析层智能体

| 智能体 | 功能 | 输入 | 输出 |
|--------|------|------|------|
| **UserRequirementAnalyst** | 需求分析 | 用户表单 | 用户画像 |
| **DestinationMatcher** | 目的地匹配 | 用户画像 | 候选目的地列表 |

### Group B - 设计层智能体

| 智能体 | 功能 | 数据源 |
|--------|------|--------|
| **AttractionDesigner** | 景点推荐 | 天行数据、OpenTripMap |
| **AccommodationDesigner** | 酒店推荐 | 模拟数据 |
| **RestaurantDesigner** | 餐厅推荐 | 模拟数据 |
| **TransportationDesigner** | 交通规划 | 距离计算 |

### Group C - 生成层智能体

| 智能体 | 功能 | 特性 |
|--------|------|------|
| **DestinationIntelligenceAgent** | 目的地情报 | 实时天气、新闻 |
| **BudgetAnalyst** | 预算分析 | 多维度成本估算 |
| **LLMGuideWriter** | 攻略生成 | TianAPI真实景点数据 |

## 数据流设计

```
用户输入
    │
    ▼
┌───────────────┐
│ 需求分析      │ → 用户画像
│ (A1)          │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ 目的地匹配    │ → 候选目的地 (带分数)
│ (A2)          │
└───────┬───────┘
        │
        ├─────────────────────────────────────┐
        │                                     │
        ▼                                     ▼
┌───────────────┐                   ┌───────────────┐
│ 景点推荐      │                   │ 目的地情报    │
│ (B1)          │                   │ (C1)          │
└───────┬───────┘                   └───────┬───────┘
        │                                   │
        ▼                                   ▼
┌───────────────┐                   ┌───────────────┐
│ 行程规划      │ ◄─────────────────┤ 预算分析      │
│ (A3)          │                   │ (C2)          │
└───────┬───────┘                   └───────────────┘
        │
        ▼
┌───────────────┐
│ 攻略生成      │ → 完整攻略
│ (C3)          │
└───────────────┘
```

## 核心功能

### 1. 智能需求分析

- **多维度画像生成**: 旅行类型、节奏偏好、预算等级
- **特殊需求解析**: 支持自然语言理解（如"靠近西藏的地方"）
- **否定表达识别**: 自动排除用户不想去的地方

### 2. 智能目的地匹配

- **规则引擎评分**: 基于兴趣标签、预算、天数的快速匹配
- **LLM智能评分**: 深度语义理解，个性化推荐
- **优先推荐机制**: 特殊需求中的城市获得 +20 加分

### 3. 景点推荐系统

- **TianAPI集成**: 真实国内景点数据
- **OpenTripMap**: 全球景点信息
- **智能筛选**: 基于用户兴趣的景点匹配

### 4. 攻略生成

- **LLM驱动**: 使用大语言模型生成自然流畅的攻略
- **真实数据**: 集成TianAPI景点信息
- **多格式导出**: PDF、Word、Markdown

### 5. 攻略中心

- **历史管理**: 保存和查看历史攻略
- **状态追踪**: 实时查看生成进度
- **快速加载**: 缓存优化，秒开历史攻略

## 技术栈

### 后端

- **框架**: FastAPI
- **智能体**: LangGraph + LangChain
- **数据库**: MongoDB (文档存储) + Redis (缓存/队列)
- **任务队列**: Celery
- **LLM**: DeepSeek V3 / DashScope / OpenAI兼容

### 前端

- **框架**: Vue 3 + TypeScript
- **UI库**: Element Plus
- **状态管理**: Pinia
- **构建工具**: Vite

### 数据源

- **国内景点**: 天行数据 (TianAPI)
- **国际景点**: OpenTripMap
- **图片**: Unsplash + Pexels
- **天气**: OpenWeatherMap (可选)

## 项目结构

```
TradingAgents-CN/
├── app/                          # FastAPI后端
│   ├── routers/                  # API路由
│   │   ├── travel.py            # 旅行规划API
│   │   ├── travel_plans.py      # 攻略管理API
│   │   ├── travel_intelligence.py # 目的地情报API
│   │   └── travel_guides.py     # 攻略生成API
│   ├── services/                 # 业务逻辑
│   │   └── travel/              # 旅行相关服务
│   ├── models/                  # 数据模型
│   └── tasks/                   # Celery任务
│
├── tradingagents/               # 智能体系统
│   ├── agents/                  # 智能体定义
│   │   ├── group_a/            # 分析层智能体
│   │   ├── group_b/            # 设计层智能体
│   │   └── group_c/            # 生成层智能体
│   ├── graph/                   # LangGraph定义
│   ├── integrations/            # 外部API集成
│   └── services/                # 智能体服务
│
├── frontend/                    # Vue前端
│   ├── src/
│   │   ├── views/travel/       # 旅行相关页面
│   │   ├── api/travel/         # API客户端
│   │   └── stores/             # Pinia状态管理
│   └── vite.config.ts
│
└── docs/travel_project/         # 项目文档
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 16+
- MongoDB 4.4+
- Redis 6.0+

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN
```

2. **配置环境变量**
```bash
cp .env.example .env.travel
# 编辑 .env.travel，配置必要的环境变量
```

3. **安装后端依赖**
```bash
pip install -e .
```

4. **安装前端依赖**
```bash
cd frontend
yarn install
```

5. **启动服务**

后端:
```bash
python app/travel_main.py
```

前端:
```bash
cd frontend
yarn dev
```

## 环境变量配置

### 必需配置

```bash
# MongoDB
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=travelagents

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# LLM (至少配置一个)
OPENAI_API_KEY=your_openai_key
# 或
DEEPSEEK_API_KEY=your_deepseek_key
# 或
DASHSCOPE_API_KEY=your_dashscope_key
```

### 可选配置

```bash
# 天行数据 (国内景点)
TIANAPI_KEY=your_tianapi_key

# Unsplash (图片)
UNSPLASH_ACCESS_KEY=your_unsplash_key

# OpenTripMap (国际景点)
OPENTRIPMAP_API_KEY=your_opentripmap_key
```

## API文档

### 核心端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/travel/analyze` | POST | 分析用户需求 |
| `/api/travel/destinations` | GET | 获取推荐目的地 |
| `/api/travel/plan/generate` | POST | 生成旅行计划 |
| `/api/travel/guide/stream` | POST | 流式生成攻略 |
| `/api/travel/guides` | GET | 获取历史攻略 |
| `/api/travel/guides/{id}` | GET | 获取单个攻略 |
| `/api/travel/guides/{id}/export` | GET | 导出攻略 |

详细API文档请参考 [API集成指南](./05_API_INTEGRATION_GUIDE.md)

## 特殊需求功能

系统支持智能解析用户的特殊需求：

### 示例

| 输入 | 解析结果 |
|------|---------|
| `我想去三亚玩几天` | 优先推荐三亚 |
| `不想去三亚，想看海` | 排除三亚，推荐其他海滨城市 |
| `靠近西藏的地方` | 推荐成都、昆明、西宁 |
| `看海的城市` | 推荐三亚、厦门、青岛、大连 |
| `有古城的` | 推荐西安、丽江、大理 |

### 技术实现

1. **规则引擎**: 正则匹配城市名，检测否定表达
2. **LLM解析**: 深度语义理解，地理推理，特征匹配

## 性能优化

- **批量LLM调用**: 14次优化为1次 (92%减少)
- **TianAPI缓存**: 76次优化为1-2次 (98%减少)
- **景点数据预加载**: 热门城市缓存，1小时TTL
- **Redis缓存**: 用户画像、目的地匹配结果缓存
- **异步任务**: Celery后台处理耗时操作

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 🙏 致谢

### 本项目基于以下项目学习开发

- **[TradingAgents-CN](https://github.com/hsliuping/TradingAgents-CN)**
  - 作者: hsliuping
  - 项目: 多智能体金融交易框架
  - 学习内容: LangGraph多智能体架构、智能体协作模式、状态管理

### 感谢以下开源项目

- **[LangGraph](https://github.com/langchain-ai/langgraph)** - 多智能体编排框架
- **[LangChain](https://github.com/langchain-ai/langchain)** - LLM 应用开发框架
- **[FastAPI](https://github.com/tiangolo/fastapi)** - 现代化 Python Web 框架
- **[Vue 3](https://github.com/vuejs/core)** - 渐进式 JavaScript 框架
- **[Element Plus](https://github.com/element-plus/element-plus)** - Vue 3 UI 组件库

### 数据源服务

- **[天行数据](https://www.tianapi.com/)** - 国内旅游景点数据 API
- **[OpenTripMap](https://opentripmap.org/)** - 开放旅行地图数据
- **[Unsplash](https://unsplash.com/)** - 高质量免费图片
- **[Pexels](https://www.pexels.com/)** - 免费库存照片

## 开源许可

本项目是学习项目，代码结构借鉴了 TradingAgents-CN 的多智能体架构设计思路。

- **旅行系统代码**: 学习项目，仅供学习参考
- **架构设计思路**: 来自 TradingAgents-CN 项目
- **原项目**: Apache 2.0 许可证

## 联系我们

- **GitHub Issues**: [提交问题](https://github.com/hsliuping/TradingAgents-CN/issues)
- **邮箱**: hsliup@163.com
- **QQ群**: 782124367

## 许可证

- **旅行系统**: 专有许可证 (需商业授权)
- **其他代码**: Apache 2.0

## 更新日志

- **v1.3.0** - 特殊需求智能解析、否定表达识别
- **v1.2.0** - TianAPI集成、攻略中心
- **v1.1.0** - 分阶段规划、PDF导出
- **v1.0.0** - 初始版本
