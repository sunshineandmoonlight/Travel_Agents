"""
测试迁移的功能

测试所有从原项目迁移过来的功能：
- 操作日志
- 任务队列
- 缓存管理
- 消息中心
- 报告管理
"""
import sys
import os
import io
import asyncio

# 设置UTF-8编码输出（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_operation_logs():
    """测试操作日志"""
    print("\n[测试1] 操作日志功能...")
    try:
        from app.routers.travel_operation_logs import (
            router,
            log_plan_created,
            log_guide_saved,
            get_stats
        )

        # 创建一些日志
        log_plan_created(1, "test_user", "杭州", 3, "plan_123", 1500)
        log_guide_saved(1, "test_user", "杭州三日游", 456)

        # 获取统计
        stats = get_stats(30)
        print(f"  ✓ 操作日志模块导入成功")
        print(f"  ✓ 路由前缀: {router.prefix}")
        print(f"  ✓ 创建了 {stats['total_operations']} 条日志")
        print(f"  ✓ 操作类型分布: {stats['operations_by_type']}")
        return True
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False


def test_task_queue():
    """测试任务队列"""
    print("\n[测试2] 任务队列功能...")
    try:
        from app.routers.travel_queue import (
            router,
            create_plan_generation_task,
            create_guide_export_task,
            get_task_stats
        )

        # 创建任务
        task_id1 = create_plan_generation_task(1, "杭州", 3, "medium", 2)
        task_id2 = create_guide_export_task(1, 456, "杭州三日游", "pdf")

        # 获取统计
        stats = get_task_stats()
        print(f"  ✓ 任务队列模块导入成功")
        print(f"  ✓ 路由前缀: {router.prefix}")
        print(f"  ✓ 创建了 {stats['total_tasks']} 个任务")
        print(f"  ✓ 任务ID: {task_id1}, {task_id2}")
        print(f"  ✓ 状态分布: {stats['status_distribution']}")
        return True
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False


def test_cache_management():
    """测试缓存管理"""
    print("\n[测试3] 缓存管理功能...")
    try:
        from app.routers.travel_cache import (
            router,
            cache_attraction_data,
            get_attraction_data,
            cache_weather_data,
            get_weather_data,
            _cache
        )

        # 测试缓存
        attraction_data = {"name": "西湖", "description": "著名景点"}
        cache_attraction_data("杭州", attraction_data, ttl=3600)

        cached = get_attraction_data("杭州")
        assert cached is not None

        weather_data = {"temp": 25, "condition": "晴"}
        cache_weather_data("杭州", weather_data, ttl=1800)

        # 获取统计
        stats = _cache.get_stats()
        print(f"  ✓ 缓存管理模块导入成功")
        print(f"  ✓ 路由前缀: {router.prefix}")
        print(f"  ✓ 缓存条目数: {stats['total_entries']}")
        print(f"  ✓ 缓存大小: {stats['total_size_mb']:.2f}MB")
        print(f"  ✓ 类型分布: {stats['by_type']}")
        return True
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_message_center():
    """测试消息中心"""
    print("\n[测试4] 消息中心功能...")
    try:
        from app.routers.travel_messages import (
            router,
            send_travel_tip,
            send_destination_alert,
            send_promotion,
            get_message_stats,
            init_default_messages
        )

        # 初始化默认消息
        init_default_messages()

        # 发送测试消息
        send_travel_tip("行李打包技巧", "轻装上阵，带上必需品")
        send_destination_alert("三亚", "weather", "台风预警", "近期有台风，请注意安全")
        send_promotion("春季特惠", "立减500元")

        # 获取统计
        stats = get_message_stats()
        print(f"  ✓ 消息中心模块导入成功")
        print(f"  ✓ 路由前缀: {router.prefix}")
        print(f"  ✓ 消息总数: {stats['total_messages']}")
        print(f"  ✓ 未读数: {stats['unread_count']}")
        print(f"  ✓ 类型分布: {stats['by_type']}")
        return True
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_reports():
    """测试报告管理"""
    print("\n[测试5] 报告管理功能...")
    try:
        from app.routers.travel_reports import (
            router,
            create_plan_report,
            create_guide_report,
            get_token_stats
        )

        # 创建测试报告
        plan_data = {"destination": "杭州", "days": 3, "itinerary": {}}
        agent_logs = []
        token_usage = {"deepseek-chat": 1500}

        report_id = create_plan_report(
            user_id=1,
            username="test_user",
            destination="杭州",
            days=3,
            budget="medium",
            plan_data=plan_data,
            agent_logs=agent_logs,
            token_usage=token_usage
        )

        # 获取Token统计
        token_stats = get_token_stats(30)
        print(f"  ✓ 报告管理模块导入成功")
        print(f"  ✓ 路由前缀: {router.prefix}")
        print(f"  ✓ 创建报告: {report_id}")
        print(f"  ✓ Token使用: {token_stats['total_tokens']}")
        return True
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_endpoints():
    """测试所有端点"""
    print("\n[测试6] 检查所有API端点...")
    try:
        from app.routers import (
            travel_operation_logs,
            travel_queue,
            travel_cache,
            travel_messages,
            travel_reports
        )

        modules = [
            ("操作日志", travel_operation_logs),
            ("任务队列", travel_queue),
            ("缓存管理", travel_cache),
            ("消息中心", travel_messages),
            ("报告管理", travel_reports)
        ]

        total_endpoints = 0
        for name, module in modules:
            count = len([r for r in module.router.routes if hasattr(r, 'path')])
            total_endpoints += count
            print(f"  ✓ {name}: {count} 个端点")

        print(f"  ✓ 总计: {total_endpoints} 个API端点")
        return True
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False


def test_integration():
    """测试功能集成"""
    print("\n[测试7] 功能集成测试...")
    try:
        from app.routers.travel_operation_logs import log_plan_completed
        from app.routers.travel_queue import create_plan_generation_task, update_task_progress, complete_task
        from app.routers.travel_notifications import notify_plan_completed
        from app.routers.travel_cache import cache_attraction_data
        from app.routers.travel_reports import create_plan_report

        # 模拟一个完整的规划流程
        user_id = 1
        destination = "杭州"
        days = 3

        # 1. 创建任务
        task_id = create_plan_generation_task(user_id, destination, days, "medium", 2)
        print(f"  ✓ 创建任务: {task_id}")

        # 2. 更新进度
        update_task_progress(task_id, 50, "正在规划行程")
        print(f"  ✓ 更新进度: 50%")

        # 3. 缓存数据
        cache_attraction_data(destination, {"西湖": "景点"}, 3600)
        print(f"  ✓ 缓存景点数据")

        # 4. 发送通知
        notify_plan_completed(user_id, destination, days, task_id)
        print(f"  ✓ 发送完成通知")

        # 5. 记录日志
        log_plan_completed(user_id, "test_user", destination, days, task_id, 5000)
        print(f"  ✓ 记录操作日志")

        # 6. 创建报告
        report_id = create_plan_report(
            user_id=user_id,
            username="test_user",
            destination=destination,
            days=days,
            budget="medium",
            plan_data={},
            agent_logs=[],
            token_usage={"deepseek-chat": 5000}
        )
        print(f"  ✓ 创建报告: {report_id}")

        # 7. 完成任务
        complete_task(task_id, {"result": "success"})
        print(f"  ✓ 完成任务")

        print(f"  ✓ 集成测试通过，各功能协同工作正常")
        return True
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("  迁移功能测试")
    print("=" * 60)

    tests = [
        ("操作日志", test_operation_logs),
        ("任务队列", test_task_queue),
        ("缓存管理", test_cache_management),
        ("消息中心", test_message_center),
        ("报告管理", test_reports),
        ("API端点", test_endpoints),
        ("功能集成", test_integration)
    ]

    results = []

    for name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = asyncio.run(test_func())
            else:
                result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ 测试 '{name}' 发生异常: {e}")
            results.append((name, False))

    # 汇总结果
    print("\n" + "=" * 60)
    print("  测试结果汇总")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {status}: {name}")

    print(f"\n总计: {passed}/{total} 通过")
    print("=" * 60)

    if passed == total:
        print("\n🎉 所有测试通过！迁移功能已就绪。")
    else:
        print(f"\n⚠ {total - passed} 个测试失败，请检查。")


if __name__ == "__main__":
    main()
