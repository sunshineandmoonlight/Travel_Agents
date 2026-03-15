# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**TradingAgents-CN** is a multi-agent AI trading framework for financial analysis, adapted from [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents). This is the Chinese-enhanced version with full A-share market support.

### Technology Stack

- **Backend**: FastAPI + Uvicorn (Python 3.10+)
- **Frontend**: Vue 3 + Vite + Element Plus + TypeScript
- **Databases**: MongoDB (primary data) + Redis (cache/session)
- **Agent Framework**: LangGraph with LangChain
- **Data Sources**: AkShare, BaoStock, Tushare (A-shares), FinnHub, yfinance (US/HK)

## Development Commands

### Backend (Python)

```bash
# Install dependencies (recommended: use uv for faster installs)
pip install -e .
# or
uv pip install -e .

# Run backend development server
cd app && python -m uvicorn main:app --reload --port 8000

# Run tests
python -m pytest tests/

# Run specific test
python tests/test_analysis.py
```

### Frontend (Vue 3)

```bash
cd frontend

# Install dependencies
yarn install

# Development server
yarn dev

# Build for production
yarn build

# Type check
yarn type-check

# Lint
yarn lint
```

### Docker Deployment

```bash
# Full stack with databases
docker-compose up -d

# With management tools (Mongo Express, Redis Commander)
docker-compose --profile management up -d

# Build images
docker-compose build
```

## Architecture Overview

### Multi-Agent System (`tradingagents/`)

The core is a **LangGraph-based multi-agent system** that analyzes stocks through specialized agents:

- **Analysts** (`tradingagents/agents/analysts/`):
  - `market_analyst.py` - Technical analysis (moving averages, RSI, MACD)
  - `fundamentals_analyst.py` - Fundamental analysis (P/E, P/B, financial ratios)
  - `news_analyst.py` - News sentiment and analysis
  - `social_media_analyst.py` - Social media monitoring (Reddit, etc.)
  - `china_market_analyst.py` - A-share market specific analysis

- **Managers** (`tradingagents/agents/managers/`):
  - `research_manager.py` - Orchestrates research phases
  - `risk_manager.py` - Risk assessment and position sizing

- **Trader** (`tradingagents/agents/trader/`):
  - Makes final buy/sell/hold decisions based on all agent inputs

- **Researchers** (`tradingagents/agents/researchers/`):
  - Gather data from various sources

- **Graph Structure** (`tradingagents/graph/`):
  - `trading_graph.py` - Main LangGraph orchestration with conditional routing
  - `setup.py` - Graph initialization and LLM binding
  - `conditional_logic.py` - Decision routing logic
  - `propagation.py` - Analysis propagation through the graph
  - `reflection.py` - Post-analysis reflection and learning

### Backend API (`app/`)

FastAPI backend with the following structure:

- **Routers** (`app/routers/`): API endpoints organized by feature
- **Services** (`app/services/`): Business logic layer
  - `analysis_service.py` - Stock analysis orchestration
  - `config_service.py` - System configuration management
  - `stock_data_service.py` - Stock data operations
  - `news_data_service.py` - News data handling
  - `simple_analysis_service.py` - Simplified single-stock analysis
- **Models** (`app/models/`): Pydantic models for request/response
- **Schemas** (`app/schemas/`): Database schemas (MongoDB)

### Frontend (`frontend/src/`)

Vue 3 SPA with:
- **Views** (`views/`): Page components (Dashboard, Analysis, Settings, etc.)
- **Components** (`components/`): Reusable UI components
- **Stores** (`stores/`): Pinia state management
- **API** (`api/`): Axios-based API client
- **Router** (`router/`): Vue Router configuration

### Data Flow (`tradingagents/dataflows/`)

- **Data Cache**: `dataflows/data_cache/` - Cached financial data
- **Interface**: `dataflows/interface.py` - Unified data source interface

### LLM Integration (`tradingagents/llm_adapters/`)

Support for multiple LLM providers:
- OpenAI (`openai`)
- Google AI (`google`) - Gemini models
- DeepSeek (`deepseek`)
- Alibaba DashScope (`dashscope`)
- And custom OpenAI-compatible endpoints via `openai_compatible_base.py`

## Key Configuration

### Environment Variables (`.env`)

Required settings:
- `MONGODB_HOST`, `MONGODB_PORT`, `MONGODB_USERNAME`, `MONGODB_PASSWORD`
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
- `JWT_SECRET`, `CSRF_SECRET` - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

LLM API keys (at least one required):
- `OPENAI_API_KEY` / `OPENAI_BASE_URL`
- `GOOGLE_API_KEY`
- `DEEPSEEK_API_KEY`
- `DASHSCOPE_API_KEY`

Data source API keys (optional):
- `TUSHARE_TOKEN`
- `FINNHUB_API_KEY`

### Default Config (`tradingagents/default_config.py`)

Controls:
- `llm_provider` - Which LLM to use
- `deep_think_llm` / `quick_think_llm` - Models for deep/quick analysis
- `max_debate_rounds` - Number of debate iterations
- `online_tools` / `online_news` / `realtime_data` - Feature flags

## Important Design Patterns

### Multi-Provider LLM System

The system uses `create_llm_by_provider()` in `trading_graph.py` to dynamically create LLM instances based on provider configuration. Always use this function when adding new LLM calls.

### Agent State Management

Agent states are defined in `tradingagents/agents/utils/agent_states.py`:
- `AgentState` - Base state for all agents
- `InvestDebateState` - Investment discussion phase
- `RiskDebateState` - Risk assessment phase

### Data Source Unification

All data sources implement a common interface pattern. When adding new data sources:
1. Create provider in `tradingagents/tools/` or `app/services/data_sources/`
2. Follow the unified data access patterns
3. Add configuration to `config_service.py`

### Async Architecture

- Backend uses `asyncio` throughout (FastAPI, motor for MongoDB)
- Worker processes handle long-running analysis tasks
- SSE (Server-Sent Events) for real-time progress updates
- WebSocket for notifications

## Testing

Tests are in `tests/` directory:
- Integration tests: `tests/integration/`
- Unit tests: `tests/unit/`
- Debug/diagnostic scripts: `debug_*.py` and various `test_*.py` files

Run tests from project root: `python -m pytest tests/`

## Common Tasks

### Adding a New LLM Provider

1. Create adapter in `tradingagents/llm_adapters/`
2. Add provider logic to `create_llm_by_provider()` in `trading_graph.py`
3. Update `config_service.py` to store provider configuration
4. Add frontend model selection in `frontend/src/views/Settings/`

### Adding a New Data Source

1. Create service in `app/services/data_sources/`
2. Add tool implementation in `tradingagents/tools/` (for agent access)
3. Update `stock_data_service.py` for unified access
4. Add configuration options to `config_service.py`

### Modifying Agent Behavior

1. Edit agent implementation in `tradingagents/agents/`
2. Update `graph/setup.py` if changing agent initialization
3. Modify `graph/conditional_logic.py` for routing changes
4. Update `graph/signal_processing.py` for decision logic changes

## Notes

- The `app/` and `frontend/` directories are **proprietary** (require commercial license)
- All other code is Apache 2.0 licensed
- Configuration is stored in MongoDB and managed via `config_service.py`
- Logs are written to `logs/` directory with rotation
- Data cache is stored in `tradingagents/dataflows/data_cache/`
