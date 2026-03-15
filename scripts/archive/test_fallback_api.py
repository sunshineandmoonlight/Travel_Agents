#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试智能降级机制API
验证降级系统、熔断器、重试机制等功能
"""

import sys
import os
import asyncio
import httpx
from datetime import datetime

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 配置
API_BASE_URL = "http://127.0.0.1:8005"
TIMEOUT = 30.0


class Colors:
    """终端颜色"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title:^70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_success(message: str):
    """打印成功消息"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")


def print_error(message: str):
    """打印错误消息"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")


def print_warning(message: str):
    """打印警告消息"""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")


def print_info(message: str):
    """打印信息"""
    print(f"{Colors.OKCYAN}ℹ️  {message}{Colors.ENDC}")


async def test_api_connection() -> bool:
    """测试API连接"""
    print_section("1. API连接测试")

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, trust_env=False) as client:
            response = await client.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                print_success(f"API服务正常运行 - {response.json()}")
                return True
            else:
                print_error(f"API服务异常 - 状态码: {response.status_code}")
                return False
    except Exception as e:
        print_error(f"无法连接到API服务: {e}")
        print_info("请确保后端服务已启动 (python app/travel_main.py)")
        return False


async def test_fallback_status() -> dict:
    """测试获取降级系统状态"""
    print_section("2. 降级系统状态")

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, trust_env=False) as client:
            response = await client.get(f"{API_BASE_URL}/api/fallback/status")
            if response.status_code == 200:
                data = response.json()
                print_success(f"获取状态成功 - 策略数量: {data.get('total_strategies', 0)}")

                # 显示各策略摘要
                for strategy in data.get('strategies', []):
                    feature_name = strategy.get('feature_name', 'unknown')
                    success_rate = strategy.get('success_rate', 0)
                    current_provider = strategy.get('current_provider', 'N/A')
                    print(f"   • {feature_name}: 成功率 {success_rate:.1%} | 当前: {current_provider}")

                return data
            else:
                print_error(f"获取状态失败 - {response.status_code}")
                return {}
    except Exception as e:
        print_error(f"请求异常: {e}")
        return {}


async def test_list_strategies():
    """测试列出所有降级策略"""
    print_section("3. 列出所有降级策略")

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, trust_env=False) as client:
            response = await client.get(f"{API_BASE_URL}/api/fallback/strategies")
            if response.status_code == 200:
                data = response.json()
                print_success(f"获取策略列表成功 - 总数: {data.get('total', 0)}")

                # 详细显示每个策略
                for strategy in data.get('strategies', []):
                    feature_name = strategy.get('feature_name')
                    description = strategy.get('description', '')
                    providers = strategy.get('providers', [])

                    print(f"\n   {Colors.BOLD}{feature_name}{Colors.ENDC} - {description}")
                    print(f"   提供商:")
                    for p in providers:
                        status_emoji = "🟢" if p.get('status') == 'healthy' else "🔴"
                        enabled_str = "启用" if p.get('enabled') else "禁用"
                        print(f"      {status_emoji} {p.get('name')} (优先级{p.get('priority')}) - {enabled_str}")

                return data
            else:
                print_error(f"获取策略列表失败 - {response.status_code}")
                return None
    except Exception as e:
        print_error(f"请求异常: {e}")
        return None


async def test_strategy_detail(feature_name: str):
    """测试获取特定策略详情"""
    print_section(f"4. 策略详情 - {feature_name}")

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, trust_env=False) as client:
            response = await client.get(
                f"{API_BASE_URL}/api/fallback/strategies/{feature_name}"
            )
            if response.status_code == 200:
                data = response.json()
                print_success(f"获取策略详情成功")

                print(f"\n   功能名称: {data.get('feature_name')}")
                print(f"   描述: {data.get('description')}")

                stats = data.get('statistics', {})
                print(f"\n   统计:")
                print(f"      总调用: {stats.get('total_calls', 0)}")
                print(f"      成功: {stats.get('successful_calls', 0)}")
                print(f"      失败: {stats.get('failed_calls', 0)}")
                print(f"      成功率: {stats.get('success_rate', 0):.1%}")

                print(f"\n   提供商配置:")
                for p in data.get('providers', []):
                    print(f"      • {p.get('name')}")
                    print(f"        优先级: {p.get('priority')}")
                    print(f"        状态: {p.get('status')}")
                    print(f"        最大重试: {p.get('max_retries')}")
                    print(f"        重试延迟: {p.get('retry_delay')}秒")
                    print(f"        熔断阈值: {p.get('circuit_breaker_threshold')}次")
                    if p.get('check_endpoint'):
                        print(f"        检查端点: {p.get('check_endpoint')}")

                return data
            elif response.status_code == 404:
                print_warning(f"策略不存在: {feature_name}")
                return None
            else:
                print_error(f"获取策略详情失败 - {response.status_code}")
                return None
    except Exception as e:
        print_error(f"请求异常: {e}")
        return None


async def test_health_check():
    """测试健康检查"""
    print_section("5. 降级系统健康检查")

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, trust_env=False) as client:
            response = await client.get(f"{API_BASE_URL}/api/fallback/health")
            if response.status_code == 200:
                data = response.json()
                health = data.get('health', 'unknown')
                summary = data.get('summary', {})

                health_emoji = {
                    'healthy': '🟢',
                    'degraded': '🟡',
                    'unhealthy': '🔴'
                }.get(health, '⚪')

                print(f"   整体状态: {health_emoji} {health.upper()}")
                print(f"\n   摘要:")
                print(f"      总策略数: {summary.get('total_strategies', 0)}")
                print(f"      健康策略: {summary.get('healthy_strategies', 0)}")
                print(f"      降级策略: {summary.get('degraded_strategies', 0)}")
                print(f"      总提供商: {summary.get('total_providers', 0)}")
                print(f"      健康提供商: {summary.get('healthy_providers', 0)}")
                print(f"      提供商健康率: {summary.get('provider_health_rate', 0):.1%}")

                if health == 'healthy':
                    print_success("降级系统运行健康")
                elif health == 'degraded':
                    print_warning("降级系统部分功能降级")
                else:
                    print_error("降级系统状态不健康")

                return data
            else:
                print_error(f"健康检查失败 - {response.status_code}")
                return None
    except Exception as e:
        print_error(f"请求异常: {e}")
        return None


async def test_provider_toggle(feature_name: str, provider_name: str, enabled: bool):
    """测试切换提供商状态"""
    action = "启用" if enabled else "禁用"
    print_section(f"6. {action}提供商 - {feature_name}/{provider_name}")

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, trust_env=False) as client:
            response = await client.post(
                f"{API_BASE_URL}/api/fallback/strategies/{feature_name}/providers/{provider_name}/toggle",
                json={"provider_name": provider_name, "enabled": enabled}
            )
            if response.status_code == 200:
                data = response.json()
                print_success(f"{action}成功: {data.get('message')}")
                return data
            elif response.status_code == 404:
                print_warning(f"提供商不存在: {feature_name}/{provider_name}")
                return None
            else:
                print_error(f"{action}失败 - {response.status_code}")
                print(f"   响应: {response.text}")
                return None
    except Exception as e:
        print_error(f"请求异常: {e}")
        return None


async def test_reset_circuit_breaker(feature_name: str, provider_name: str):
    """测试重置熔断器"""
    print_section(f"7. 重置熔断器 - {feature_name}/{provider_name}")

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, trust_env=False) as client:
            response = await client.post(
                f"{API_BASE_URL}/api/fallback/strategies/{feature_name}/providers/{provider_name}/reset-circuit"
            )
            if response.status_code == 200:
                data = response.json()
                print_success(f"重置成功: {data.get('message')}")
                return data
            elif response.status_code == 404:
                print_warning(f"熔断器不存在: {feature_name}/{provider_name}")
                return None
            else:
                print_error(f"重置失败 - {response.status_code}")
                return None
    except Exception as e:
        print_error(f"请求异常: {e}")
        return None


async def run_all_tests():
    """运行所有测试"""
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║          智能降级机制 API 测试套件                                  ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

    start_time = datetime.now()

    # 1. 测试API连接
    if not await test_api_connection():
        print_error("API服务不可用，测试终止")
        return

    # 2. 测试降级状态
    status_data = await test_fallback_status()

    # 3. 列出所有策略
    strategies_data = await test_list_strategies()

    # 4. 测试特定策略详情（测试几个主要策略）
    test_features = ["weather_forecast", "attraction_search", "image_search"]
    for feature in test_features:
        await test_strategy_detail(feature)

    # 5. 健康检查
    await test_health_check()

    # 6. 测试提供商切换（使用mock进行测试）
    # 注意：这里会实际修改系统状态，仅在测试环境执行
    print_section("6. 提供商管理测试")
    print_info("跳过实际切换测试（避免影响生产状态）")
    print_info("如需测试，可以手动调用API:")
    print_info("   POST /api/fallback/strategies/{feature}/providers/{provider}/toggle")
    print_info("   POST /api/fallback/strategies/{feature}/providers/{provider}/reset-circuit")

    # 总结
    elapsed_time = (datetime.now() - start_time).total_seconds()
    print_section("测试总结")
    print_success(f"所有基础测试完成，耗时: {elapsed_time:.2f}秒")
    print_info("\n可用的API端点:")
    print_info("   GET  /api/fallback/status")
    print_info("   GET  /api/fallback/strategies")
    print_info("   GET  /api/fallback/strategies/{{feature_name}}")
    print_info("   POST /api/fallback/strategies/{{feature_name}}/providers/{{provider_name}}/toggle")
    print_info("   POST /api/fallback/strategies/{{feature_name}}/providers/{{provider_name}}/reset-circuit")
    print_info("   GET  /api/fallback/health")
    print_info("\n访问 API 文档: http://localhost:8005/docs")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
