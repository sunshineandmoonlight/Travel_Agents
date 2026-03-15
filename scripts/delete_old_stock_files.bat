@echo off
echo 开始删除股票相关旧文件...
echo 请确认: 这些文件将被永久删除!
pause

echo 删除: app\models\agent_analysis.py
del /f /q "app\models\agent_analysis.py"
echo 删除: app\models\analysis.py
del /f /q "app\models\analysis.py"
echo 删除: app\models\screening.py
del /f /q "app\models\screening.py"
echo 删除: app\models\stock_models.py
del /f /q "app\models\stock_models.py"
echo 删除: app\routers\akshare_init.py
del /f /q "app\routers\akshare_init.py"
echo 删除: app\routers\analysis.py
del /f /q "app\routers\analysis.py"
echo 删除: app\routers\baostock_init.py
del /f /q "app\routers\baostock_init.py"
echo 删除: app\routers\favorites.py
del /f /q "app\routers\favorites.py"
echo 删除: app\routers\financial_data.py
del /f /q "app\routers\financial_data.py"
echo 删除: app\routers\historical_data.py
del /f /q "app\routers\historical_data.py"
echo 删除: app\routers\multi_market_stocks.py
del /f /q "app\routers\multi_market_stocks.py"
echo 删除: app\routers\multi_period_sync.py
del /f /q "app\routers\multi_period_sync.py"
echo 删除: app\routers\multi_source_sync.py
del /f /q "app\routers\multi_source_sync.py"
echo 删除: app\routers\news_data.py
del /f /q "app\routers\news_data.py"
echo 删除: app\routers\paper.py
del /f /q "app\routers\paper.py"
echo 删除: app\routers\screening.py
del /f /q "app\routers\screening.py"
echo 删除: app\routers\social_media.py
del /f /q "app\routers\social_media.py"
echo 删除: app\routers\stock_data.py
del /f /q "app\routers\stock_data.py"
echo 删除: app\routers\stock_sync.py
del /f /q "app\routers\stock_sync.py"
echo 删除: app\routers\stocks.py
del /f /q "app\routers\stocks.py"
echo 删除: app\routers\sync.py
del /f /q "app\routers\sync.py"
echo 删除: app\routers\tushare_init.py
del /f /q "app\routers\tushare_init.py"
echo 删除: app\services\analysis\status_update_utils.py
del /f /q "app\services\analysis\status_update_utils.py"
echo 删除: app\services\analysis_service.py
del /f /q "app\services\analysis_service.py"
echo 删除: app\services\basics_sync\processing.py
del /f /q "app\services\basics_sync\processing.py"
echo 删除: app\services\basics_sync\utils.py
del /f /q "app\services\basics_sync\utils.py"
echo 删除: app\services\basics_sync_service.py
del /f /q "app\services\basics_sync_service.py"
echo 删除: app\services\data_sources\akshare_adapter.py
del /f /q "app\services\data_sources\akshare_adapter.py"
echo 删除: app\services\data_sources\baostock_adapter.py
del /f /q "app\services\data_sources\baostock_adapter.py"
echo 删除: app\services\data_sources\tushare_adapter.py
del /f /q "app\services\data_sources\tushare_adapter.py"
echo 删除: app\services\database_screening_service.py
del /f /q "app\services\database_screening_service.py"
echo 删除: app\services\enhanced_screening\utils.py
del /f /q "app\services\enhanced_screening\utils.py"
echo 删除: app\services\enhanced_screening_service.py
del /f /q "app\services\enhanced_screening_service.py"
echo 删除: app\services\favorites_service.py
del /f /q "app\services\favorites_service.py"
echo 删除: app\services\financial_data_service.py
del /f /q "app\services\financial_data_service.py"
echo 删除: app\services\foreign_stock_service.py
del /f /q "app\services\foreign_stock_service.py"
echo 删除: app\services\historical_data_service.py
del /f /q "app\services\historical_data_service.py"
echo 删除: app\services\multi_source_basics_sync_service.py
del /f /q "app\services\multi_source_basics_sync_service.py"
echo 删除: app\services\news_data_service.py
del /f /q "app\services\news_data_service.py"
echo 删除: app\services\queue_service.py
del /f /q "app\services\queue_service.py"
echo 删除: app\services\quotes_ingestion_service.py
del /f /q "app\services\quotes_ingestion_service.py"
echo 删除: app\services\quotes_service.py
del /f /q "app\services\quotes_service.py"
echo 删除: app\services\screening\eval_utils.py
del /f /q "app\services\screening\eval_utils.py"
echo 删除: app\services\screening_service.py
del /f /q "app\services\screening_service.py"
echo 删除: app\services\simple_analysis_service.py
del /f /q "app\services\simple_analysis_service.py"
echo 删除: app\services\social_media_service.py
del /f /q "app\services\social_media_service.py"
echo 删除: app\services\stock_data_service.py
del /f /q "app\services\stock_data_service.py"
echo 删除: app\services\unified_stock_service.py
del /f /q "app\services\unified_stock_service.py"
echo 删除: app\worker\akshare_init_service.py
del /f /q "app\worker\akshare_init_service.py"
echo 删除: app\worker\akshare_sync_service.py
del /f /q "app\worker\akshare_sync_service.py"
echo 删除: app\worker\analysis_worker.py
del /f /q "app\worker\analysis_worker.py"
echo 删除: app\worker\baostock_init_service.py
del /f /q "app\worker\baostock_init_service.py"
echo 删除: app\worker\baostock_sync_service.py
del /f /q "app\worker\baostock_sync_service.py"
echo 删除: app\worker\example_sdk_sync_service.py
del /f /q "app\worker\example_sdk_sync_service.py"
echo 删除: app\worker\financial_data_sync_service.py
del /f /q "app\worker\financial_data_sync_service.py"
echo 删除: app\worker\hk_data_service.py
del /f /q "app\worker\hk_data_service.py"
echo 删除: app\worker\hk_sync_service.py
del /f /q "app\worker\hk_sync_service.py"
echo 删除: app\worker\multi_period_sync_service.py
del /f /q "app\worker\multi_period_sync_service.py"
echo 删除: app\worker\news_data_sync_service.py
del /f /q "app\worker\news_data_sync_service.py"
echo 删除: app\worker\tushare_init_service.py
del /f /q "app\worker\tushare_init_service.py"
echo 删除: app\worker\tushare_sync_service.py
del /f /q "app\worker\tushare_sync_service.py"
echo 删除: app\worker\us_data_service.py
del /f /q "app\worker\us_data_service.py"
echo 删除: app\worker\us_sync_service.py
del /f /q "app\worker\us_sync_service.py"
echo 删除: frontend\src\api\analysis.ts
del /f /q "frontend\src\api\analysis.ts"
echo 删除: frontend\src\api\favorites.ts
del /f /q "frontend\src\api\favorites.ts"
echo 删除: frontend\src\api\paper.ts
del /f /q "frontend\src\api\paper.ts"
echo 删除: frontend\src\api\screening.ts
del /f /q "frontend\src\api\screening.ts"
echo 删除: frontend\src\api\stocks.ts
del /f /q "frontend\src\api\stocks.ts"
echo 删除: frontend\src\api\stockSync.ts
del /f /q "frontend\src\api\stockSync.ts"
echo 删除: frontend\src\api\sync.ts
del /f /q "frontend\src\api\sync.ts"
echo 删除: frontend\src\components\Dashboard\MultiSourceSyncCard.vue
del /f /q "frontend\src\components\Dashboard\MultiSourceSyncCard.vue"
echo 删除: frontend\src\components\Global\MultiMarketStockSearch.vue
del /f /q "frontend\src\components\Global\MultiMarketStockSearch.vue"
echo 删除: frontend\src\components\Sync\DataSourceStatus.vue
del /f /q "frontend\src\components\Sync\DataSourceStatus.vue"
echo 删除: frontend\src\components\Sync\SyncControl.vue
del /f /q "frontend\src\components\Sync\SyncControl.vue"
echo 删除: frontend\src\components\Sync\SyncHistory.vue
del /f /q "frontend\src\components\Sync\SyncHistory.vue"
echo 删除: frontend\src\components\Sync\SyncRecommendations.vue
del /f /q "frontend\src\components\Sync\SyncRecommendations.vue"
echo 删除: frontend\src\types\analysis.ts
del /f /q "frontend\src\types\analysis.ts"
echo 删除: frontend\src\views\Analysis\AnalysisHistory.vue
del /f /q "frontend\src\views\Analysis\AnalysisHistory.vue"
echo 删除: frontend\src\views\Analysis\BatchAnalysis.vue
del /f /q "frontend\src\views\Analysis\BatchAnalysis.vue"
echo 删除: frontend\src\views\Analysis\SingleAnalysis.vue
del /f /q "frontend\src\views\Analysis\SingleAnalysis.vue"
echo 删除: frontend\src\views\Favorites\index.vue
del /f /q "frontend\src\views\Favorites\index.vue"
echo 删除: frontend\src\views\PaperTrading\index.vue
del /f /q "frontend\src\views\PaperTrading\index.vue"
echo 删除: frontend\src\views\Screening\index.vue
del /f /q "frontend\src\views\Screening\index.vue"
echo 删除: frontend\src\views\Stocks\Detail.vue
del /f /q "frontend\src\views\Stocks\Detail.vue"
echo 删除: frontend\src\views\System\MultiSourceSync.vue
del /f /q "frontend\src\views\System\MultiSourceSync.vue"
echo 删除: tradingagents\agents\analysts\social_media_analyst.py
del /f /q "tradingagents\agents\analysts\social_media_analyst.py"
echo 删除: tradingagents\dataflows\stock_data_service.py
del /f /q "tradingagents\dataflows\stock_data_service.py"
echo 删除: tradingagents\dataflows\technical\stockstats.py
del /f /q "tradingagents\dataflows\technical\stockstats.py"
echo 删除: tradingagents\models\stock_data_models.py
del /f /q "tradingagents\models\stock_data_models.py"
echo 删除: tradingagents\tools\analysis\indicators.py
del /f /q "tradingagents\tools\analysis\indicators.py"

echo.
echo 删除完成!
pause
