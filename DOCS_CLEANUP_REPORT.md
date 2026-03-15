# 文档目录清理报告 - 股票相关文件

## 📊 发现的股票相关文档

### ✅ docs/guides/ 目录下的股票相关文件

| 文件 | 说明 | 大小 |
|------|------|------|
| `a-share-analysis-guide.md` | A股分析指南 | ~7.7KB |
| `baostock_unified/` | 贝索数据统一指南 | 目录 |
| `financial_data_system/` | 金融数据系统 | 目录 |
| `news-analysis-guide.md` | 新闻分析指南 | 文件 |
| `stock_basics_sync.md` | 股票基础数据同步 | 文件 |
| `stock_data_sdk_integration_guide.md` | 股票数据SDK集成指南 | 文件 |
| `tushare_financial_data/` | Tushare金融数据 | 目录 |

### 📂 可能包含股票内容的其他目录

| 目录 | 说明 |
|------|------|
| `docs/agents/` | 智能体文档（需检查内容） |
| `docs/api/` | API文档（需检查内容） |
| `docs/paper/` | 模拟交易相关 |
| `docs/overview/` | 项目概览（可能包含股票介绍） |

## 🔍 建议清理的文档

### 高优先级清理（纯股票内容）

```
docs/guides/a-share-analysis-guide.md
docs/guides/baostock_unified/
docs/guides/financial_data_system/
docs/guides/stock_basics_sync.md
docs/guides/stock_data_sdk_integration_guide.md
docs/guides/tushare_financial_data/
docs/guides/news-analysis-guide.md  # 如果是股票新闻分析
docs/paper/  # 整个模拟交易目录
```

### 中优先级检查（可能包含混合内容）

```
docs/overview/  # 检查是否包含股票系统介绍
docs/agents/  # 检查是否只有股票智能体说明
docs/api/      # 检查是否只有股票API文档
docs/features/ # 检查是否有股票相关功能文档
```

### 建议保留

```
docs/travel_project/  # ✅ 旅行系统文档
docs/travel_learning/ # ✅ 旅行学习文档
docs/archive/         # ✅ 归档文档
docs/llm/             # ✅ LLM相关（通用）
docs/configuration/  # ✅ 配置文档（通用）
docs/development/    # ✅ 开发指南（通用）
docs/deployment/     # ✅ 部署指南（通用）
```

## 🎯 清理建议

### 选项1: 创建 docs/archive_stock/ 目录

将股票相关文档移动到归档目录：

```bash
mkdir -p docs/archive_stock

# 移动股票相关文档
mv docs/guides/a-share-analysis-guide.md docs/archive_stock/
mv docs/guides/baostock_unified docs/archive_stock/
mv docs/guides/financial_data_system docs/archive_stock/
mv docs/guides/stock_basics_sync.md docs/archive_stock/
mv docs/guides/stock_data_sdk_integration_guide.md docs/archive_stock/
mv docs/guides/tushare_financial_data docs/archive_stock/
mv docs/guides/news-analysis-guide.md docs/archive_stock/
mv docs/paper docs/archive_stock/
```

### 选项2: 直接删除

如果确认不需要：

```bash
rm -rf docs/guides/a-share-analysis-guide.md
rm -rf docs/guides/baostock_unified/
rm -rf docs/guides/financial_data_system/
rm -rf docs/guides/stock_basics_sync.md
rm -rf docs/guides/stock_data_sdk_integration_guide.md
rm -rf docs/guides/tushare_financial_data/
rm -rf docs/guides/news-analysis-guide.md
rm -rf docs/paper/
```

### 选项3: 更新 README.md

在主README中只保留旅行系统相关文档链接。

## 📋 推荐清理方案

**推荐：选项1（归档）**

优点：
- 保留历史记录
- 不影响git历史
- 需要时可以恢复
- 项目更整洁

执行命令（如需执行）：

```bash
# 创建归档目录
mkdir -p docs/archive_stock

# 移动股票文档
mv docs/guides/a-share-analysis-guide.md docs/archive_stock/
mv docs/guides/baostock_unified docs/archive_stock/
mv docs/guides/financial_data_system docs/archive_stock/
mv docs/guides/stock_basics_sync.md docs/archive_stock/
mv docs/guides/stock_data_sdk_integration_guide.md docs/archive_stock/
mv docs/guides/tushare_financial_data docs/archive_stock/
mv docs/guides/news-analysis-guide.md docs/archive_stock/
mv docs/paper docs/archive_stock/

# 创建归档README
echo "# 股票交易系统文档归档

这些文档来自原TradingAgents-CN股票交易系统，现已归档保存。

- A股分析指南
- 数据源集成
- 模拟交易系统" > docs/archive_stock/README.md
```

## ❓ 需要执行清理吗？

请选择清理方案：

- [ ] **方案1: 归档到 docs/archive_stock/** （推荐）
- [ ] **方案2: 直接删除**
- [ ] **方案3: 暂不清理**

如果选择方案1，我可以立即执行。
