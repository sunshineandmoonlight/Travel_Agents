#!/usr/bin/env python3
"""
分析并列出所有股票相关的旧文件（与旅行无关的文件）
这些文件是旧股票项目的遗留，可以安全删除
"""

import os
from pathlib import Path
from typing import Set, List

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 股票相关的关键词（用于识别旧股票文件）
STOCK_KEYWORDS = {
    # 路由相关
    'akshare_init', 'baostock_init', 'tushare_init',
    'financial_data', 'historical_data', 'multi_market_stocks',
    'multi_period_sync', 'multi_source_sync', 'stock_sync',
    'stock_data', 'stocks', 'sync',
    'analysis', 'screening', 'favorites', 'paper', 'paper_trading',
    'quotes', 'quotes_ingestion', 'basics_sync',
    'social_media', 'news_data',
    'hk_data', 'hk_sync', 'us_data', 'us_sync',

    # 服务相关
    'simple_analysis', 'database_screening', 'enhanced_screening',
    'stock_data_service', 'unified_stock_service',
    'favorites_service', 'financial_data_service',
    'historical_data_service', 'foreign_stock_service',
    'social_media_service', 'news_data_service',
    'quotes_service', 'queue_service',

    # Worker相关
    'akshare_sync_service', 'baostock_sync_service',
    'tushare_sync_service', 'financial_data_sync_service',
    'multi_period_sync_service', 'news_data_sync_service',
    'analysis_worker', 'hk_data_service', 'us_data_service',

    # 数据源适配器
    'akshare_adapter', 'baostock_adapter', 'tushare_adapter',

    # CLI相关
    'akshare_init', 'baostock_init', 'tushare_init',

    # 模型相关
    'stock_models', 'screening',

    # 前端相关
    'Analysis', 'Screening', 'StockData', 'FinancialData',
    'batch_analysis', 'multi_market', 'paper_trading',

    # tradingagents 中的股票相关（保留部分旅行用的）
}

# 旅行相关的关键词（这些要保留）
TRAVEL_KEYWORDS = {
    'travel', 'planner', 'guide', 'destination', 'attraction',
    'restaurant', 'hotel', 'itinerary', 'immersive', 'exploration',
    'relaxation', 'hidden_gem', 'style', 'staged', 'guide_center',
    'travel_pdf', 'travel_service', 'travel_cache', 'travel_images',
    'travel_intelligence', 'travel_messages', 'travel_notifications',
    'travel_operation_logs', 'travel_plans', 'travel_queue',
    'travel_reports', 'travel_tags', 'travel_guides',
    'destination_intelligence', 'destination_matcher',
    'itinerary_planner', 'attraction_analyst',
}

# 需要保留的核心文件（共享基础设施）
KEEP_CORE_FILES = {
    '__init__.py', '__pycache__',
    'config.py', 'config_bridge.py', 'database.py',
    'logging_config.py', 'fallback_config.py', 'fallback_manager.py',
    'redis_client.py', 'rate_limiter.py',
    'auth.py', 'auth_db.py',  # 共用的认证
    'cache.py',  # 共用的缓存
    'sse.py',  # 共用的SSE
    'notifications.py',  # 共用的通知
    'operation_logs.py',  # 共用的操作日志
    'usage_statistics.py',  # 共用的统计
    'system_config.py',  # 共用的配置
    'logs.py',  # 共用的日志
    'health.py',  # 共用的健康检查
    'debug.py',  # 共用的调试
    'async_tasks.py',  # 共用的异步任务
    'internal_messages.py',  # 共用的内部消息
    'model_capabilities.py',  # 共用的模型能力
    'websocket_notifications.py',  # 共用的WebSocket
    'error_handler.py', 'request_id.py', 'rate_limit.py',  # 中间件
}

def is_stock_related(file_path: Path) -> bool:
    """判断文件是否与股票相关"""
    path_str = str(file_path).lower()
    filename = file_path.name.lower()
    dirname = file_path.parent.name.lower() if file_path.parent else ''

    # 如果包含旅行关键词，保留
    for travel_kw in TRAVEL_KEYWORDS:
        if travel_kw.lower() in path_str:
            return False

    # 检查是否是核心文件
    if filename in KEEP_CORE_FILES or dirname in KEEP_CORE_FILES:
        return False

    # 检查股票关键词
    for stock_kw in STOCK_KEYWORDS:
        if stock_kw.lower() in path_str:
            return True

    return False

def find_stock_files() -> List[Path]:
    """找到所有股票相关的旧文件"""
    stock_files = []

    # 遍历项目目录
    for root_dir in ['app', 'frontend/src', 'tradingagents']:
        root_path = PROJECT_ROOT / root_dir
        if not root_path.exists():
            continue

        for file_path in root_path.rglob('*'):
            # 只检查Python/Vue/TS文件
            if file_path.suffix not in ['.py', '.vue', '.ts', '.js']:
                continue

            # 跳过__pycache__和node_modules
            if '__pycache__' in str(file_path) or 'node_modules' in str(file_path):
                continue

            if is_stock_related(file_path):
                stock_files.append(file_path)

    return sorted(stock_files)

def categorize_files(files: List[Path]) -> dict:
    """按类别分类文件"""
    categories = {
        'app/routers': [],
        'app/services': [],
        'app/models': [],
        'app/worker': [],
        'app/utils': [],
        'app/tasks': [],
        'app/cli': [],
        'tradingagents': [],
        'frontend': [],
        'other': []
    }

    for file_path in files:
        path_str = str(file_path)
        if '/app/routers/' in path_str:
            categories['app/routers'].append(file_path)
        elif '/app/services/' in path_str:
            categories['app/services'].append(file_path)
        elif '/app/models/' in path_str:
            categories['app/models'].append(file_path)
        elif '/app/worker/' in path_str:
            categories['app/worker'].append(file_path)
        elif '/app/utils/' in path_str:
            categories['app/utils'].append(file_path)
        elif '/app/tasks/' in path_str:
            categories['app/tasks'].append(file_path)
        elif '/cli/' in path_str:
            categories['app/cli'].append(file_path)
        elif '/tradingagents/' in path_str:
            categories['tradingagents'].append(file_path)
        elif '/frontend/' in path_str:
            categories['frontend'].append(file_path)
        else:
            categories['other'].append(file_path)

    return categories

def main():
    print("=" * 80)
    print("股票相关旧文件分析")
    print("=" * 80)
    print()

    # 查找所有股票相关文件
    stock_files = find_stock_files()

    if not stock_files:
        print("✅ 没有找到需要删除的股票相关文件")
        return

    # 按类别分类
    categories = categorize_files(stock_files)

    total_count = 0
    total_size = 0

    for category, files in categories.items():
        if not files:
            continue

        print(f"\n{'='*60}")
        print(f"📁 {category.upper()}")
        print(f"{'='*60}")
        print(f"   文件数量: {len(files)}")
        print()

        for file_path in files:
            rel_path = file_path.relative_to(PROJECT_ROOT)
            size = file_path.stat().st_size if file_path.exists() else 0
            total_count += 1
            total_size += size

            print(f"   {rel_path}")
            print(f"   大小: {size:,} bytes")
            print()

    print("=" * 80)
    print(f"📊 统计汇总")
    print("=" * 80)
    print(f"   总文件数: {total_count}")
    print(f"   总大小: {total_size:,} bytes ({total_size / 1024 / 1024:.2f} MB)")
    print()

    # 生成删除脚本
    print("=" * 80)
    print("📝 生成删除脚本")
    print("=" * 80)
    print()

    delete_script_path = PROJECT_ROOT / 'scripts' / 'delete_old_stock_files.sh'
    with open(delete_script_path, 'w', encoding='utf-8') as f:
        f.write("#!/bin/bash\n")
        f.write("# 删除所有股票相关的旧文件\n")
        f.write("# 执行前请确认！\n\n")
        f.write("echo '开始删除股票相关旧文件...'\n\n")

        for file_path in stock_files:
            rel_path = file_path.relative_to(PROJECT_ROOT)
            f.write(f"rm -f '{rel_path}'\n")

        f.write("\necho '删除完成！'\n")

    print(f"   删除脚本已生成: {delete_script_path.relative_to(PROJECT_ROOT)}")
    print(f"   Windows版本: {delete_script_path.with_suffix('.bat').relative_to(PRO_ROOT)}")
    print()

    # 生成Windows版本
    bat_script_path = delete_script_path.with_suffix('.bat')
    with open(bat_script_path, 'w', encoding='utf-8') as f:
        f.write("@echo off\n")
        f.write("echo 开始删除股票相关旧文件...\n\n")

        for file_path in stock_files:
            rel_path = file_path.relative_to(PROJECT_ROOT)
            # 转换路径格式
            win_path = str(rel_path).replace('/', '\\')
            f.write(f"del /f /q \"{win_path}\"\n")

        f.write("\necho 删除完成！\n")
        f.write("pause\n")

    print(f"   ✅ 脚本生成完成")
    print()
    print("=" * 80)
    print("⚠️  注意事项")
    print("=" * 80)
    print("1. 请仔细检查上述文件列表")
    print("2. 确认没有误删旅行相关的文件")
    print("3. 建议先备份整个项目")
    print("4. 确认无误后再执行删除脚本")
    print()

if __name__ == '__main__':
    main()
