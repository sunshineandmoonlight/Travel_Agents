"""
旅行系统 API 直接测试

使用 TestClient 直接测试 FastAPI 应用，无需启动服务器
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from fastapi.testclient import TestClient
from app.main import app

# 创建测试客户端
client = TestClient(app)


def print_section(title: str):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_health():
    """测试健康检查"""
    print_section("健康检查")
    response = client.get("/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    return response.status_code == 200


def test_travel_api_docs():
    """测试旅行API文档可访问"""
    print_section("API文档")
    response = client.get("/docs")
    print(f"API文档状态: {response.status_code}")
    return response.status_code == 200


def test_travel_stats():
    """测试获取统计数据"""
    print_section("获取统计数据")
    response = client.get("/api/travel/stats")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"总攻略数: {data.get('total_guides')}")
        print(f"已发布: {data.get('published_guides')}")
        print(f"总浏览: {data.get('total_views')}")
        print(f"总点赞: {data.get('total_likes')}")
        return True
    else:
        print(f"错误: {response.text}")
        return False


def test_get_guides():
    """测试获取攻略列表"""
    print_section("获取攻略列表")
    response = client.get("/api/travel/guides?page=1&page_size=5")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"总数: {data.get('total')}")
        print(f"当前页: {data.get('page')}")
        print(f"攻略数: {len(data.get('items', []))}")

        if data.get('items'):
            print(f"\n第一个攻略:")
            item = data['items'][0]
            print(f"  - 标题: {item.get('title')}")
            print(f"  - 目的地: {item.get('destination')}")
            print(f"  - 天数: {item.get('days')}")
            print(f"  - 状态: {item.get('status')}")
        return True
    else:
        print(f"错误: {response.text}")
        return False


def test_search_guides():
    """测试搜索攻略"""
    print_section("搜索攻略")
    response = client.get("/api/travel/guides/search/fulltext?keyword=北京&page=1&page_size=3")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"搜索结果: {data.get('total')} 条")

        if data.get('items'):
            print(f"\n匹配的攻略:")
            for item in data['items'][:3]:
                print(f"  - {item.get('title')} ({item.get('destination')})")
        return True
    else:
        print(f"错误: {response.text}")
        return False


def test_create_travel_plan():
    """测试创建旅行规划"""
    print_section("创建旅行规划 (AI生成)")

    data = {
        "destination": "杭州",
        "days": 3,
        "budget": "medium",
        "travelers": 2,
        "interest_type": "自然",
        "selected_style": "relaxed",
        "save_as_guide": False  # 不保存，只测试生成
    }

    print(f"请求参数: 目的地={data['destination']}, 天数={data['days']}, 预算={data['budget']}")

    try:
        response = client.post("/api/travel/plan", json=data)
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"成功: {result.get('success')}")
            print(f"消息: {result.get('message')}")

            if result.get('data'):
                plan = result['data']
                print(f"\n规划结果:")
                print(f"  - 目的地: {plan.get('destination')}")
                print(f"  - 类型: {plan.get('destination_type')}")
                print(f"  - 天数: {plan.get('days')}")
                print(f"  - 风格: {plan.get('travel_style')}")
                print(f"  - 预算: {plan.get('budget_breakdown', {}).get('total_budget')} 元")
                print(f"  - 日均: {plan.get('budget_breakdown', {}).get('daily_average')} 元")
                print(f"  - 人均: {plan.get('budget_breakdown', {}).get('per_person_average')} 元")
            return True
        else:
            print(f"错误: {response.text}")
            return False

    except Exception as e:
        print(f"请求异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_create_guide():
    """测试创建攻略"""
    print_section("创建攻略")

    data = {
        "title": "测试攻略 - 上海三日游",
        "description": "这是一个测试攻略",
        "destination": "上海",
        "destination_type": "domestic",
        "days": 3,
        "budget_level": "medium",
        "travelers_count": 2,
        "travel_style": "exploration",
        "interest_tags": ["购物", "美食", "文化"]
    }

    response = client.post("/api/travel/guides", json=data)
    print(f"状态码: {response.status_code}")

    if response.status_code == 201:
        guide = response.json()
        print(f"攻略创建成功!")
        print(f"  - ID: {guide.get('id')}")
        print(f"  - UUID: {guide.get('uuid')}")
        print(f"  - 标题: {guide.get('title')}")
        print(f"  - 状态: {guide.get('status')}")
        return guide.get('id'), True
    else:
        print(f"错误: {response.text}")
        return None, False


def test_get_guide_detail(guide_id: int):
    """测试获取攻略详情"""
    print_section(f"获取攻略详情 (ID: {guide_id})")

    response = client.get(f"/api/travel/guides/{guide_id}")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        guide = response.json()
        print(f"攻略详情:")
        print(f"  - 标题: {guide.get('title')}")
        print(f"  - 目的地: {guide.get('destination')}")
        print(f"  - 天数: {guide.get('days')}")
        print(f"  - 预算级别: {guide.get('budget_level')}")
        print(f"  - 风格: {guide.get('travel_style')}")
        print(f"  - 浏览量: {guide.get('view_count')}")
        print(f"  - 点赞数: {guide.get('like_count')}")
        print(f"  - 收藏数: {guide.get('bookmark_count')}")
        return True
    else:
        print(f"错误: {response.text}")
        return False


def test_like_guide(guide_id: int):
    """测试点赞功能"""
    print_section(f"测试点赞 (ID: {guide_id})")

    # 第一次点赞
    response = client.post(f"/api/travel/guides/{guide_id}/like")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"点赞后: 已点赞={result.get('is_liked')}, 点赞数={result.get('like_count')}")

        # 获取点赞状态
        status_resp = client.get(f"/api/travel/guides/{guide_id}/like/status")
        if status_resp.status_code == 200:
            status = status_resp.json()
            print(f"当前状态: 已点赞={status.get('is_liked')}, 点赞数={status.get('like_count')}")

        # 取消点赞
        unlike_resp = client.post(f"/api/travel/guides/{guide_id}/like")
        if unlike_resp.status_code == 200:
            unlike_result = unlike_resp.json()
            print(f"取消后: 已点赞={unlike_result.get('is_liked')}, 点赞数={unlike_result.get('like_count')}")

        return True
    else:
        print(f"错误: {response.text}")
        return False


def test_bookmark_guide(guide_id: int):
    """测试收藏功能"""
    print_section(f"测试收藏 (ID: {guide_id})")

    data = {
        "notes": "这是一个测试收藏备注",
        "folder_name": "测试收藏夹"
    }

    # 添加收藏
    response = client.post(f"/api/travel/guides/{guide_id}/bookmark", json=data)
    print(f"状态码: {response.status_code}")

    if response.status_code == 201:
        bookmark = response.json()
        print(f"收藏成功!")
        print(f"  - 收藏ID: {bookmark.get('id')}")
        print(f"  - 备注: {bookmark.get('notes')}")
        print(f"  - 收藏夹: {bookmark.get('folder_name')}")

        # 取消收藏
        delete_resp = client.delete(f"/api/travel/guides/{guide_id}/bookmark")
        if delete_resp.status_code == 200:
            print("取消收藏成功!")

        return True
    else:
        print(f"错误: {response.text}")
        return False


def test_recommendations(guide_id: int):
    """测试推荐功能"""
    print_section(f"获取相似攻略推荐 (ID: {guide_id})")

    response = client.get(f"/api/travel/guides/{guide_id}/recommendations?limit=5")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        guides = response.json()
        print(f"推荐数量: {len(guides)}")

        if guides:
            print(f"\n推荐攻略:")
            for guide in guides[:3]:
                print(f"  - {guide.get('title')} ({guide.get('destination')})")
        return True
    else:
        print(f"错误: {response.text}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("*" * 60)
    print("  旅行系统 API 测试")
    print("*" * 60)

    results = []

    # 基础测试
    results.append(("健康检查", test_health()))
    results.append(("API文档", test_travel_api_docs()))

    # API测试
    results.append(("统计数据", test_travel_stats()))
    results.append(("攻略列表", test_get_guides()))
    results.append(("搜索攻略", test_search_guides()))

    # 创建测试攻略
    guide_id, success = test_create_guide()
    results.append(("创建攻略", success))

    if guide_id:
        # 使用创建的攻略ID进行后续测试
        results.append(("攻略详情", test_get_guide_detail(guide_id)))
        results.append(("点赞功能", test_like_guide(guide_id)))
        results.append(("收藏功能", test_bookmark_guide(guide_id)))
        results.append(("相似推荐", test_recommendations(guide_id)))

    # AI规划测试（可能较慢）
    results.append(("AI旅行规划", test_create_travel_plan()))

    # 输出结果
    print_section("测试结果汇总")

    passed = 0
    failed = 0

    for name, success in results:
        status = "[PASS] " if success else "[FAIL] "
        print(f"{status}{name}")
        if success:
            passed += 1
        else:
            failed += 1

    print("\n" + "-" * 60)
    print(f"总计: {len(results)} 个测试")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"通过率: {passed/len(results)*100:.1f}%")
    print("-" * 60)

    return failed == 0


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
