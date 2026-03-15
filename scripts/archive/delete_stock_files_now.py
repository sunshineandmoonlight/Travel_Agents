import sys
import os

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from pathlib import Path
import shutil

PROJECT_ROOT = Path(__file__).parent.parent

# 股票相关的文件列表
STOCK_FILES = [
    'app/models/agent_analysis.py',
    'app/models/analysis.py',
    'app/models/screening.py',
    'app/models/stock_models.py',
    'app/routers/akshare_init.py',
    'app/routers/analysis.py',
    'app/routers/baostock_init.py',
    'app/routers/favorites.py',
    'app/routers/financial_data.py',
    'app/routers/historical_data.py',
    'app/routers/multi_market_stocks.py',
    'app/routers/multi_period_sync.py',
    'app/routers/multi_source_sync.py',
    'app/routers/news_data.py',
    'app/routers/paper.py',
    'app/routers/screening.py',
    'app/routers/social_media.py',
    'app/routers/stock_data.py',
    'app/routers/stock_sync.py',
    'app/routers/stocks.py',
    'app/routers/sync.py',
    'app/routers/tushare_init.py',
    'app/services/analysis/status_update_utils.py',
    'app/services/analysis_service.py',
    'app/services/basics_sync/processing.py',
    'app/services/basics_sync/utils.py',
    'app/services/basics_sync_service.py',
    'app/services/data_sources/akshare_adapter.py',
    'app/services/data_sources/baostock_adapter.py',
    'app/services/data_sources/tushare_adapter.py',
    'app/services/database_screening_service.py',
    'app/services/enhanced_screening/utils.py',
    'app/services/enhanced_screening_service.py',
    'app/services/favorites_service.py',
    'app/services/financial_data_service.py',
    'app/services/foreign_stock_service.py',
    'app/services/historical_data_service.py',
    'app/services/multi_source_basics_sync_service.py',
    'app/services/news_data_service.py',
    'app/services/queue_service.py',
    'app/services/quotes_ingestion_service.py',
    'app/services/quotes_service.py',
    'app/services/screening/eval_utils.py',
    'app/services/screening_service.py',
    'app/services/simple_analysis_service.py',
    'app/services/social_media_service.py',
    'app/services/stock_data_service.py',
    'app/services/unified_stock_service.py',
    'app/worker/akshare_init_service.py',
    'app/worker/akshare_sync_service.py',
    'app/worker/analysis_worker.py',
    'app/worker/baostock_init_service.py',
    'app/worker/baostock_sync_service.py',
    'app/worker/example_sdk_sync_service.py',
    'app/worker/financial_data_sync_service.py',
    'app/worker/hk_data_service.py',
    'app/worker/hk_sync_service.py',
    'app/worker/multi_period_sync_service.py',
    'app/worker/news_data_sync_service.py',
    'app/worker/tushare_init_service.py',
    'app/worker/tushare_sync_service.py',
    'app/worker/us_data_service.py',
    'app/worker/us_sync_service.py',
    'frontend/src/api/analysis.ts',
    'frontend/src/api/favorites.ts',
    'frontend/src/api/paper.ts',
    'frontend/src/api/screening.ts',
    'frontend/src/api/stocks.ts',
    'frontend/src/api/stockSync.ts',
    'frontend/src/api/sync.ts',
    'frontend/src/components/Dashboard/MultiSourceSyncCard.vue',
    'frontend/src/components/Global/MultiMarketStockSearch.vue',
    'frontend/src/components/Sync/DataSourceStatus.vue',
    'frontend/src/components/Sync/SyncControl.vue',
    'frontend/src/components/Sync/SyncHistory.vue',
    'frontend/src/components/Sync/SyncRecommendations.vue',
    'frontend/src/types/analysis.ts',
    'frontend/src/views/Analysis/AnalysisHistory.vue',
    'frontend/src/views/Analysis/BatchAnalysis.vue',
    'frontend/src/views/Analysis/SingleAnalysis.vue',
    'frontend/src/views/Favorites/index.vue',
    'frontend/src/views/PaperTrading/index.vue',
    'frontend/src/views/Screening/index.vue',
    'frontend/src/views/Stocks/Detail.vue',
    'frontend/src/views/System/MultiSourceSync.vue',
    'tradingagents/agents/analysts/social_media_analyst.py',
    'tradingagents/dataflows/stock_data_service.py',
    'tradingagents/dataflows/technical/stockstats.py',
    'tradingagents/models/stock_data_models.py',
    'tradingagents/tools/analysis/indicators.py',
]

def delete_file(file_path: Path) -> bool:
    """删除文件或目录"""
    try:
        if file_path.is_dir():
            shutil.rmtree(file_path)
        elif file_path.is_file():
            file_path.unlink()
        return True
    except Exception as e:
        print(f"[ERROR] {file_path}: {e}")
        return False

def main():
    print("=" * 80)
    print("删除股票相关旧文件")
    print("=" * 80)
    print()

    deleted_count = 0
    failed_count = 0

    for file_str in STOCK_FILES:
        file_path = PROJECT_ROOT / file_str
        if file_path.exists():
            print(f"[{deleted_count + 1:02d}] 删除: {file_str}")
            if delete_file(file_path):
                deleted_count += 1
            else:
                failed_count += 1
        else:
            print(f"[SKIP] 不存在: {file_str}")

    # 清理空目录
    print()
    print("=" * 80)
    print("清理空目录...")
    print("=" * 80)

    empty_dirs = [
        'app/services/analysis',
        'app/services/basics_sync',
        'app/services/enhanced_screening',
        'app/services/data_sources',
        'app/cli',
        'app/worker',
        'tradingagents/dataflows',
        'tradingagents/dataflows/technical',
        'tradingagents/tools/analysis',
        'tradingagents/models',
        'frontend/src/api',
        'frontend/src/components/Dashboard',
        'frontend/src/components/Sync',
        'frontend/src/views/Analysis',
        'frontend/src/views/Favorites',
        'frontend/src/views/PaperTrading',
        'frontend/src/views/Screening',
        'frontend/src/views/Stocks',
        'frontend/src/views/System',
        'frontend/src/types',
    ]

    for dir_str in empty_dirs:
        dir_path = PROJECT_ROOT / dir_str
        if dir_path.exists() and dir_path.is_dir():
            try:
                # 检查目录是否为空
                if not list(dir_path.iterdir()):
                    shutil.rmtree(dir_path)
                    print(f"[DEL] 空目录: {dir_str}")
            except:
                pass

    print()
    print("=" * 80)
    print(f"完成! 已删除 {deleted_count} 个文件, {failed_count} 个失败")
    print("=" * 80)

if __name__ == '__main__':
    main()
