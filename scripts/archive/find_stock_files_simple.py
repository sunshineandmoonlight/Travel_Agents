import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from pathlib import Path
from typing import List

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 股票相关的关键词（用于识别旧股票文件）
STOCK_KEYWORDS = {
    'akshare_init', 'baostock_init', 'tushare_init',
    'financial_data', 'historical_data', 'multi_market_stocks',
    'multi_period_sync', 'multi_source_sync', 'stock_sync',
    'stock_data', 'stocks', 'sync',
    'analysis', 'screening', 'favorites', 'paper',
    'quotes', 'quotes_ingestion', 'basics_sync',
    'social_media', 'news_data',
    'hk_data', 'hk_sync', 'us_data', 'us_sync',
    'simple_analysis', 'database_screening', 'enhanced_screening',
    'stock_data_service', 'unified_stock_service',
    'favorites_service', 'financial_data_service',
    'historical_data_service', 'foreign_stock_service',
    'quotes_service', 'queue_service',
    'akshare_adapter', 'baostock_adapter', 'tushare_adapter',
    'stock_models',
}

# 旅行相关的关键词（这些要保留）
TRAVEL_KEYWORDS = {
    'travel', 'planner', 'guide', 'destination', 'attraction',
    'restaurant', 'hotel', 'itinerary', 'immersive', 'exploration',
    'relaxation', 'hidden_gem', 'style', 'staged',
    'travel_pdf', 'travel_service', 'travel_cache', 'travel_images',
    'travel_intelligence', 'travel_messages', 'travel_notifications',
    'travel_operation_logs', 'travel_plans', 'travel_queue',
    'travel_reports', 'travel_tags', 'travel_guides',
    'destination_intelligence', 'destination_matcher',
    'itinerary_planner', 'attraction_analyst', 'budget_analyst',
}

# 需要保留的核心文件
KEEP_CORE_FILES = {
    '__init__.py', '__pycache__',
    'config.py', 'config_bridge.py', 'database.py',
    'logging_config.py', 'fallback_config.py', 'fallback_manager.py',
    'redis_client.py', 'rate_limiter.py',
    'auth.py', 'auth_db.py',
    'cache.py', 'sse.py', 'notifications.py',
    'operation_logs.py', 'usage_statistics.py', 'system_config.py',
    'logs.py', 'health.py', 'debug.py', 'async_tasks.py',
    'internal_messages.py', 'model_capabilities.py',
    'websocket_notifications.py',
    'error_handler.py', 'request_id.py', 'rate_limit.py',
    'pdf_generator.py', 'report_exporter.py',
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

    for root_dir in ['app', 'frontend/src', 'tradingagents']:
        root_path = PROJECT_ROOT / root_dir
        if not root_path.exists():
            continue

        for file_path in root_path.rglob('*'):
            if file_path.suffix not in ['.py', '.vue', '.ts', '.js']:
                continue
            if '__pycache__' in str(file_path) or 'node_modules' in str(file_path):
                continue
            if is_stock_related(file_path):
                stock_files.append(file_path)

    return sorted(stock_files)

def main():
    print("=" * 80)
    print("股票相关旧文件分析")
    print("=" * 80)
    print()

    stock_files = find_stock_files()

    if not stock_files:
        print("[OK] 没有找到需要删除的股票相关文件")
        return

    total_count = 0
    total_size = 0

    for file_path in stock_files:
        rel_path = file_path.relative_to(PROJECT_ROOT)
        size = file_path.stat().st_size if file_path.exists() else 0
        total_count += 1
        total_size += size
        print(f"[{total_count:02d}] {rel_path} ({size:,} bytes)")

    print()
    print("=" * 80)
    print(f"总计: {total_count} 个文件, {total_size / 1024 / 1024:.2f} MB")
    print("=" * 80)
    print()

    # 生成删除脚本
    bat_script_path = PROJECT_ROOT / 'scripts' / 'delete_old_stock_files.bat'
    with open(bat_script_path, 'w', encoding='utf-8') as f:
        f.write("@echo off\n")
        f.write("echo 开始删除股票相关旧文件...\n")
        f.write("echo 请确认: 这些文件将被永久删除!\n")
        f.write("pause\n\n")

        for file_path in stock_files:
            rel_path = file_path.relative_to(PROJECT_ROOT)
            win_path = str(rel_path).replace('/', '\\')
            f.write(f"echo 删除: {rel_path}\n")
            f.write(f"del /f /q \"{win_path}\"\n")

        f.write("\necho.\necho 删除完成!\npause\n")

    print(f"[OK] 删除脚本已生成: scripts/delete_old_stock_files.bat")
    print()
    print("注意事项:")
    print("1. 请仔细检查上述文件列表")
    print("2. 确认没有误删旅行相关的文件")
    print("3. 建议先备份整个项目")
    print("4. 确认无误后再执行删除脚本")

if __name__ == '__main__':
    main()
