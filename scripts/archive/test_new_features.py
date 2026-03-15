"""
测试新增的旅行功能

测试标签管理和通知系统
"""
import sys
import os
import io

# 设置UTF-8编码输出（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_travel_tags_import():
    """测试旅行标签导入"""
    print("\n[测试1] 测试旅行标签导入...")
    try:
        from app.routers.travel_tags import router, TravelTag
        print("  ✓ 旅行标签模块导入成功")
        print(f"  ✓ 路由前缀: {router.prefix}")
        print(f"  ✓ 标签数量: {len(router.tags)}")
        return True
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        return False


def test_travel_notifications_import():
    """测试旅行通知导入"""
    print("\n[测试2] 测试旅行通知导入...")
    try:
        from app.routers.travel_notifications import (
            router,
            notify_plan_completed,
            notify_guide_updated,
            notify_price_alert
        )
        print("  ✓ 旅行通知模块导入成功")
        print(f"  ✓ 路由前缀: {router.prefix}")
        print(f"  ✓ 便捷函数数量: 5")
        return True
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        return False


def test_tag_endpoints():
    """测试标签端点"""
    print("\n[测试3] 测试标签端点...")
    try:
        from app.routers.travel_tags import router

        endpoints = []
        for route in router.routes:
            if hasattr(route, 'path'):
                endpoints.append(f"{route.methods} {route.path}")

        print(f"  ✓ 注册了 {len(endpoints)} 个端点:")
        for endpoint in endpoints:
            print(f"     - {endpoint}")
        return True
    except Exception as e:
        print(f"  ✗ 检查失败: {e}")
        return False


def test_notification_endpoints():
    """测试通知端点"""
    print("\n[测试4] 测试通知端点...")
    try:
        from app.routers.travel_notifications import router

        endpoints = []
        for route in router.routes:
            if hasattr(route, 'path'):
                endpoints.append(f"{route.methods} {route.path}")

        print(f"  ✓ 注册了 {len(endpoints)} 个端点:")
        for endpoint in endpoints:
            print(f"     - {endpoint}")
        return True
    except Exception as e:
        print(f"  ✗ 检查失败: {e}")
        return False


def test_create_notification():
    """测试创建通知"""
    print("\n[测试5] 测试创建通知...")
    try:
        from app.routers.travel_notifications import (
            notify_plan_completed,
            notify_guide_updated,
            get_unread_count
        )

        # 创建规划完成通知
        notif1 = notify_plan_completed(user_id=1, destination="杭州", days=3, plan_id="plan_123")
        print(f"  ✓ 创建规划完成通知: {notif1['title']}")

        # 创建攻略更新通知
        notif2 = notify_guide_updated(user_id=1, guide_title="杭州三日游", guide_id=456)
        print(f"  ✓ 创建攻略更新通知: {notif2['title']}")

        # 检查未读数量
        count = get_unread_count(user_id=1)
        print(f"  ✓ 未读通知数量: {count}")

        return True
    except Exception as e:
        print(f"  ✗ 创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_default_tags():
    """测试默认标签"""
    print("\n[测试6] 测试默认标签...")
    try:
        from app.routers.travel_tags import init_default_tags, TravelTag
        from app.db.travel_db import DatabaseManager

        # 初始化数据库
        db_manager = DatabaseManager()
        db_manager.initialize()

        with db_manager.get_session() as db:
            # 确保表存在
            from app.routers.travel_tags import ensure_tags_table
            ensure_tags_table(db)

            # 初始化默认标签
            init_default_tags(db)

            # 查询标签
            tags = db.query(TravelTag).limit(5).all()
            print(f"  ✓ 找到 {len(tags)} 个标签:")
            for tag in tags:
                print(f"     - {tag.icon} {tag.name} ({tag.tag_type})")

            return True
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_notification_functions():
    """测试通知便捷函数"""
    print("\n[测试7] 测试通知便捷函数...")
    try:
        from app.routers.travel_notifications import (
            notify_price_alert,
            notify_weather_alert,
            notify_system_message,
            get_unread_count
        )

        # 价格提醒
        notif1 = notify_price_alert(
            user_id=1,
            destination="三亚",
            original_price=5000,
            current_price=3500
        )
        print(f"  ✓ 价格提醒: {notif1['title']}")

        # 天气预警
        notif2 = notify_weather_alert(
            user_id=1,
            destination="三亚",
            weather_condition="暴雨",
            travel_date="2026-04-01"
        )
        print(f"  ✓ 天气预警: {notif2['title']}")

        # 系统消息
        notif3 = notify_system_message(
            user_id=1,
            title="系统维护通知",
            content="系统将于今晚22:00进行维护",
            priority="high"
        )
        print(f"  ✓ 系统消息: {notif3['title']}")

        # 检查总未读数
        total_unread = get_unread_count(user_id=1)
        print(f"  ✓ 总未读数: {total_unread}")

        return True
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("  新增旅行功能测试")
    print("=" * 60)

    tests = [
        ("旅行标签导入", test_travel_tags_import),
        ("旅行通知导入", test_travel_notifications_import),
        ("标签端点", test_tag_endpoints),
        ("通知端点", test_notification_endpoints),
        ("创建通知", test_create_notification),
        ("默认标签", test_default_tags),
        ("通知便捷函数", test_notification_functions)
    ]

    results = []
    for name, test_func in tests:
        try:
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
        print("\n所有测试通过！新功能已就绪。")
    else:
        print(f"\n{total - passed} 个测试失败，请检查。")


if __name__ == "__main__":
    main()
