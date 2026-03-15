#!/usr/bin/env python
"""
Redis缓存功能测试脚本

测试内容:
1. Redis连接测试
2. 缓存读写测试
3. TTL过期测试
4. 缓存统计测试
5. 缓存清理测试
6. 自动降级测试
"""

import os
import sys
import time
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()


def test_redis_connection():
    """测试1: Redis连接"""
    print("\n" + "="*60)
    print("测试1: Redis连接测试")
    print("="*60)

    try:
        import redis

        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        redis_password = os.getenv("REDIS_PASSWORD", "")

        # 创建连接
        if redis_password:
            client = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                decode_responses=True,
                socket_connect_timeout=5
            )
        else:
            client = redis.Redis(
                host=redis_host,
                port=redis_port,
                decode_responses=True,
                socket_connect_timeout=5
            )

        # 测试ping
        result = client.ping()
        if result:
            print(f"✅ Redis连接成功: {redis_host}:{redis_port}")
            print(f"   Redis版本: {client.info()['redis_version']}")
            return client
        else:
            print("❌ Redis连接失败")
            return None

    except ImportError:
        print("❌ redis模块未安装，请运行: pip install redis")
        return None
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        return None


def test_cache_write_read(redis_client):
    """测试2: 缓存读写"""
    print("\n" + "="*60)
    print("测试2: 缓存读写测试")
    print("="*60)

    try:
        from tradingagents.utils.redis_cache import RedisCacheManager

        cache_manager = RedisCacheManager()

        # 测试数据
        test_data = {
            "tool_name": "test_weather",
            "params": {"city": "北京", "days": 3},
            "result": [
                {"date": "2026-03-14", "temp": "15°C", "weather": "晴"},
                {"date": "2026-03-15", "temp": "16°C", "weather": "多云"},
                {"date": "2026-03-16", "temp": "14°C", "weather": "小雨"}
            ]
        }

        # 写入缓存
        print(f"📝 写入缓存: {test_data['tool_name']}")
        cache_manager.set(
            test_data["tool_name"],
            test_data["params"],
            test_data["result"],
            ttl=60
        )

        # 读取缓存
        print(f"📖 读取缓存: {test_data['tool_name']}")
        cached_result = cache_manager.get(
            test_data["tool_name"],
            test_data["params"]
        )

        if cached_result:
            print(f"✅ 缓存读取成功: {len(cached_result)} 条记录")
            print(f"   数据: {json.dumps(cached_result, ensure_ascii=False, indent=2)}")
            return True
        else:
            print("❌ 缓存读取失败")
            return False

    except Exception as e:
        print(f"❌ 缓存读写测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_ttl(redis_client):
    """测试3: TTL过期"""
    print("\n" + "="*60)
    print("测试3: TTL过期测试")
    print("="*60)

    try:
        from tradingagents.utils.redis_cache import RedisCacheManager

        cache_manager = RedisCacheManager()

        # 写入短期缓存 (5秒TTL)
        test_key = "test_ttl"
        test_params = {"test": "ttl"}
        test_result = {"data": "将在5秒后过期"}

        print(f"📝 写入短期缓存 (TTL=5秒)")
        cache_manager.set(test_key, test_params, test_result, ttl=5)

        # 立即读取
        result1 = cache_manager.get(test_key, test_params)
        if result1:
            print(f"✅ 立即读取成功: {result1}")
        else:
            print("❌ 立即读取失败")
            return False

        # 等待6秒后读取
        print(f"⏳ 等待6秒...")
        time.sleep(6)

        result2 = cache_manager.get(test_key, test_params)
        if result2 is None:
            print(f"✅ 缓存已过期 (符合预期)")
            return True
        else:
            print(f"❌ 缓存未过期 (不符合预期): {result2}")
            return False

    except Exception as e:
        print(f"❌ TTL测试失败: {e}")
        return False


def test_cache_stats(redis_client):
    """测试4: 缓存统计"""
    print("\n" + "="*60)
    print("测试4: 缓存统计测试")
    print("="*60)

    try:
        from tradingagents.utils.redis_cache import RedisCacheManager

        cache_manager = RedisCacheManager()

        # 清空缓存
        cache_manager.clear()

        # 执行多次操作
        print("📝 执行测试操作...")

        # 第1次 - 未命中
        cache_manager.get("test_stats", {"key": "1"})

        # 写入
        cache_manager.set("test_stats", {"key": "1"}, {"data": "test1"}, ttl=60)

        # 第2次 - 命中
        cache_manager.get("test_stats", {"key": "1"})

        # 第3次 - 未命中（不同参数）
        cache_manager.get("test_stats", {"key": "2"})

        # 获取统计
        stats = cache_manager.get_stats()

        print(f"📊 缓存统计:")
        print(f"   缓存类型: {stats.get('cache_type', 'redis')}")
        print(f"   总请求数: {stats.get('total_requests', 0)}")
        print(f"   命中次数: {stats.get('hits', 0)}")
        print(f"   未命中次数: {stats.get('misses', 0)}")
        print(f"   命中率: {stats.get('hit_rate', '0%')}")
        print(f"   缓存大小: {stats.get('cache_size', 0)}")

        if stats.get('total_requests', 0) > 0:
            print(f"\n✅ 缓存统计正常")
            return True
        else:
            print(f"\n❌ 缓存统计异常")
            return False

    except Exception as e:
        print(f"❌ 缓存统计测试失败: {e}")
        return False


def test_cache_clear(redis_client):
    """测试5: 缓存清理"""
    print("\n" + "="*60)
    print("测试5: 缓存清理测试")
    print("="*60)

    try:
        from tradingagents.utils.redis_cache import RedisCacheManager

        cache_manager = RedisCacheManager()

        # 写入测试数据
        print("📝 写入测试数据...")
        cache_manager.set("test_clear_1", {}, {"data": "1"}, ttl=60)
        cache_manager.set("test_clear_2", {}, {"data": "2"}, ttl=60)
        cache_manager.set("other_key", {}, {"data": "3"}, ttl=60)

        # 获取清理前大小
        stats_before = cache_manager.get_stats()
        size_before = stats_before.get('cache_size', 0)
        print(f"   缓存大小: {size_before}")

        # 清理特定模式的缓存
        print("🧹 清理 'test_clear' 模式的缓存...")
        count = cache_manager.clear(pattern="test_clear")
        print(f"   清理了 {count} 条缓存")

        # 获取清理后大小
        stats_after = cache_manager.get_stats()
        size_after = stats_after.get('cache_size', 0)
        print(f"   缓存大小: {size_after}")

        if size_after < size_before:
            print(f"✅ 缓存清理成功 (减少了 {size_before - size_after} 条)")
            return True
        else:
            print(f"❌ 缓存清理失败")
            return False

    except Exception as e:
        print(f"❌ 缓存清理测试失败: {e}")
        return False


def test_cache_auto_fallback():
    """测试6: 自动降级"""
    print("\n" + "="*60)
    print("测试6: 自动降级测试")
    print("="*60)

    try:
        from tradingagents.utils.cache_init import init_cache_system, get_cache_manager

        # 初始化缓存系统
        print("🔧 初始化缓存系统...")
        cache_status = init_cache_system()

        print(f"   缓存类型: {cache_status.get('cache_type', 'unknown')}")
        print(f"   消息: {cache_status.get('message', '')}")

        # 获取缓存管理器
        cache_manager = get_cache_manager()

        # 测试读写
        print("📝 测试缓存读写...")
        cache_manager.set("fallback_test", {}, {"data": "test"}, ttl=60)
        result = cache_manager.get("fallback_test", {})

        if result:
            print(f"✅ 缓存系统正常工作 (类型: {cache_status.get('cache_type')})")
            return True
        else:
            print(f"❌ 缓存系统异常")
            return False

    except Exception as e:
        print(f"❌ 自动降级测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoints():
    """测试7: API端点"""
    print("\n" + "="*60)
    print("测试7: API端点测试")
    print("="*60)

    import requests

    base_url = "http://localhost:8005"

    try:
        # 测试系统状态端点
        print("📡 测试系统状态端点...")
        response = requests.get(f"{base_url}/api/debug/system/status", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 系统状态端点正常")

            # 显示缓存信息
            if 'cache' in data:
                cache_info = data['cache']
                print(f"   缓存类型: {cache_info.get('cache_backend', 'unknown')}")
                print(f"   命中率: {cache_info.get('hit_rate', 'N/A')}")
                print(f"   缓存大小: {cache_info.get('cache_size', 0)}")

            return True
        else:
            print(f"❌ 系统状态端点返回: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("⚠️  后端未运行，跳过API测试")
        print("   请先启动后端: python app/travel_main.py")
        return None
    except Exception as e:
        print(f"❌ API端点测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("TravelAgents-CN Redis缓存功能测试")
    print("="*60)

    results = []

    # 测试1: Redis连接
    redis_client = test_redis_connection()
    results.append(("Redis连接", redis_client is not None))

    if redis_client is None:
        print("\n⚠️  Redis未连接，仅测试自动降级功能")
        results.append(("自动降级", test_cache_auto_fallback()))
    else:
        # 测试2-6: 需要Redis连接
        results.append(("缓存读写", test_cache_write_read(redis_client)))
        results.append(("TTL过期", test_cache_ttl(redis_client)))
        results.append(("缓存统计", test_cache_stats(redis_client)))
        results.append(("缓存清理", test_cache_clear(redis_client)))
        results.append(("自动降级", test_cache_auto_fallback()))

    # 测试7: API端点
    api_result = test_api_endpoints()
    if api_result is not None:
        results.append(("API端点", api_result))

    # 输出测试结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        if result is None:
            status = "⚠️  跳过"
        print(f"{name:15} {status}")

    # 统计
    passed = sum(1 for _, r in results if r is True)
    failed = sum(1 for _, r in results if r is False)
    skipped = sum(1 for _, r in results if r is None)

    print(f"\n总计: {len(results)} 项测试")
    print(f"通过: {passed}  |  失败: {failed}  |  跳过: {skipped}")

    if failed == 0:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {failed} 项测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
