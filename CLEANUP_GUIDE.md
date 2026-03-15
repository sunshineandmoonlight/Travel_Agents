# 项目清理指南

本文档列出了项目中和旅行项目无关的文件，供确认删除或移动。

## 已清理 ✅

### 根目录临时文件
- 已删除所有 *.txt 日志文件
- 已删除 api_result*.json 测试文件
- 已删除 LLM_OUTPUT_SAMPLES.md

### 前端备份文件
- 已删除 Planner.vue.bak
- 已删除 DetailedGuide.vue.backup
- 已删除 DetailedGuide.vue.broken
- 已删除 travelGuideContent.json.bak

---

## 待确认清理 ⚠️

### Scripts 目录（378个测试脚本）
```
scripts/test_*.py
scripts/demo_*.py
scripts/diagnose_*.py
scripts/kill_*.py
scripts/migrate_*.py
scripts/show_*.py
```

**建议**：移动到 `scripts/archive/` 目录

### TradingAgents 股票相关文件
```
tradingagents/agents/analysts/market_analyst.py
tradingagents/agents/analysts/china_market_analyst.py
tradingagents/api/stock_api.py
tradingagents/dataflows/stock_api.py
tradingagents/graph/trading_graph.py
tradingagents/tools/analysis/
tradingagents/utils/stock_utils.py
tradingagents/utils/stock_validator.py
```

**建议**：移动到 `tradingagents/archive/stock_trading/`

### 前端非旅行视图
```
frontend/src/views/Dashboard/
frontend/src/views/Reports/
frontend/src/views/System/
frontend/src/views/Tasks/
frontend/src/views/Queue/
frontend/src/views/Settings/ (部分是旅行需要的)
frontend/src/views/Learning/
```

**注意**：Settings 可能包含旅行系统需要的配置，需要仔细检查

### 后端非旅行路由
```
app/routers/reports.py
app/routers/scheduler.py
app/routers/queue.py
app/routers/system_config.py
app/routers/database.py
app/routers/logs.py
app/routers/operation_logs.py
app/routers/cache.py
app/routers/internal_messages.py
app/routers/usage_statistics.py
```

---

## 清理命令示例

### 移动测试脚本
```bash
mkdir -p scripts/archive
mv scripts/test_*.py scripts/demo_*.py scripts/archive/
```

### 移动股票交易文件
```bash
mkdir -p tradingagents/archive/stock_trading
mv tradingagents/agents/analysts/market_analyst.py tradingagents/archive/stock_trading/
mv tradingagents/agents/analysts/china_market_analyst.py tradingagents/archive/stock_trading/
mv tradingagents/api/stock_api.py tradingagents/archive/stock_trading/
# ... 其他文件
```

---

## 保留的文件（旅行系统核心）

### 后端核心文件
- `app/travel_main.py` ✅
- `app/routers/travel_*.py` ✅
- `app/routers/staged_planning.py` ✅
- `app/routers/auth.py` ✅
- `tradingagents/agents/group_*/` ✅
- `tradingagents/agents/specialists/` ✅
- `tradingagents/services/tool_*.py` ✅

### 前端核心文件
- `frontend/src/views/travel/` ✅
- `frontend/src/views/Auth/` ✅
- `frontend/src/layouts/TravelLayout.vue` ✅
- `frontend/src/stores/travel*.ts` ✅
- `frontend/src/api/travel/` ✅

---

## 下一步

1. **确认要删除的文件列表**
2. **备份整个项目**（以防万一）
3. **执行清理命令**
4. **测试旅行系统功能是否正常**
