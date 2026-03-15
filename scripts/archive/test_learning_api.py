"""
测试学习中心API

验证学习中心的所有功能是否正常工作
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


def test_learning_router_import():
    """测试学习路由导入"""
    print("\n[测试1] 测试学习路由导入...")
    try:
        from app.routers.learning import router, LEARNING_CATEGORIES, ARTICLES
        print("  ✓ 学习路由导入成功")
        print(f"  ✓ 分类数量: {len(LEARNING_CATEGORIES)}")
        print(f"  ✓ 文章数量: {len(ARTICLES)}")
        return True
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        return False


async def test_get_categories():
    """测试获取分类列表"""
    print("\n[测试2] 测试获取分类列表...")
    try:
        from app.routers.learning import get_learning_categories

        categories = await get_learning_categories()

        if len(categories) > 0:
            print(f"  ✓ 获取到 {len(categories)} 个分类")
            for cat in categories[:3]:
                print(f"     - {cat.display_name} ({cat.article_count}篇)")
            return True
        else:
            print("  ✗ 分类列表为空")
            return False
    except Exception as e:
        print(f"  ✗ 获取失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_get_articles():
    """测试获取文章列表"""
    print("\n[测试3] 测试获取文章列表...")
    try:
        from app.routers.learning import get_articles

        articles = await get_articles(category=None, limit=10)

        if len(articles) > 0:
            print(f"  ✓ 获取到 {len(articles)} 篇文章")
            for art in articles[:3]:
                print(f"     - {art.title} ({art.read_time})")
            return True
        else:
            print("  ✗ 文章列表为空")
            return False
    except Exception as e:
        print(f"  ✗ 获取失败: {e}")
        return False


async def test_get_article_detail():
    """测试获取文章详情"""
    print("\n[测试4] 测试获取文章详情...")
    try:
        from app.routers.learning import get_article

        article = await get_article("what-is-ai-travel")

        if article:
            print(f"  ✓ 文章标题: {article.title}")
            print(f"  ✓ 分类: {article.category_display}")
            print(f"  ✓ 阅读时间: {article.read_time}")
            print(f"  ✓ 难度: {article.difficulty}")
            print(f"  ✓ 浏览量: {article.views}")
            return True
        else:
            print("  ✗ 文章不存在")
            return False
    except Exception as e:
        print(f"  ✗ 获取失败: {e}")
        return False


async def test_search_articles():
    """测试搜索文章"""
    print("\n[测试5] 测试搜索文章...")
    try:
        from app.routers.learning import search_articles

        # 搜索"旅行"（更通用）
        results = await search_articles(keyword="旅行")

        if len(results) > 0:
            print(f"  ✓ 搜索'旅行'找到 {len(results)} 篇文章")
            for art in results[:3]:
                print(f"     - {art.title}")
            return True
        else:
            print("  ✗ 搜索结果为空")
            return False
    except Exception as e:
        print(f"  ✗ 搜索失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_get_recommended():
    """测试获取推荐文章"""
    print("\n[测试6] 测试获取推荐文章...")
    try:
        from app.routers.learning import get_recommended_articles

        articles = await get_recommended_articles(limit=5)

        if len(articles) > 0:
            print(f"  ✓ 获取到 {len(articles)} 篇推荐文章")
            print(f"  ✓ 最受欢迎: {articles[0].title} ({articles[0].views}浏览)")
            return True
        else:
            print("  ✗ 推荐文章为空")
            return False
    except Exception as e:
        print(f"  ✗ 获取失败: {e}")
        return False


async def test_get_stats():
    """测试获取统计信息"""
    print("\n[测试7] 测试获取统计信息...")
    try:
        from app.routers.learning import get_learning_stats

        stats = await get_learning_stats()

        print(f"  ✓ 文章总数: {stats['total_articles']}")
        print(f"  ✓ 总浏览量: {stats['total_views']}")
        print(f"  ✓ 分类数: {stats['total_categories']}")
        print(f"  ✓ 分类统计:")
        for name, count in stats['category_stats'].items():
            print(f"     - {name}: {count}篇")
        return True
    except Exception as e:
        print(f"  ✗ 获取失败: {e}")
        return False


def test_api_endpoints():
    """测试API端点注册"""
    print("\n[测试8] 测试API端点注册...")
    try:
        from app.routers.learning import router

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


def test_article_content():
    """测试文章内容完整性"""
    print("\n[测试9] 测试文章内容完整性...")
    try:
        from app.routers.learning import ARTICLES

        required_fields = [
            'id', 'title', 'category', 'category_display',
            'description', 'read_time', 'difficulty', 'views'
        ]

        all_valid = True
        for article_id, article in ARTICLES.items():
            missing = [f for f in required_fields if f not in article]
            if missing:
                print(f"  ✗ 文章 {article_id} 缺少字段: {missing}")
                all_valid = False

        if all_valid:
            print(f"  ✓ 所有 {len(ARTICLES)} 篇文章字段完整")
            return True
        else:
            return False
    except Exception as e:
        print(f"  ✗ 检查失败: {e}")
        return False


async def test_category_filter():
    """测试分类筛选"""
    print("\n[测试10] 测试分类筛选...")
    try:
        from app.routers.learning import get_articles

        # 筛选"教程"分类
        articles = await get_articles(category="tutorials", limit=10)

        if len(articles) > 0:
            print(f"  ✓ '实战教程'分类有 {len(articles)} 篇文章")
            for art in articles:
                print(f"     - {art.title}")
            return True
        else:
            print("  ✗ 该分类没有文章")
            return False
    except Exception as e:
        print(f"  ✗ 筛选失败: {e}")
        return False


async def run_async_tests():
    """运行异步测试"""
    async_tests = [
        ("获取分类列表", test_get_categories),
        ("获取文章列表", test_get_articles),
        ("获取文章详情", test_get_article_detail),
        ("搜索文章", test_search_articles),
        ("获取推荐文章", test_get_recommended),
        ("获取统计信息", test_get_stats),
        ("分类筛选", test_category_filter)
    ]

    results = []
    for name, test_func in async_tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ 测试 '{name}' 发生异常: {e}")
            results.append((name, False))

    return results


def main():
    """运行所有测试"""
    import asyncio

    print("\n" + "=" * 60)
    print("  学习中心API测试")
    print("=" * 60)

    results = []

    # 同步测试
    sync_tests = [
        ("学习路由导入", test_learning_router_import),
        ("API端点注册", test_api_endpoints),
        ("文章内容完整性", test_article_content)
    ]

    for name, test_func in sync_tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ 测试 '{name}' 发生异常: {e}")
            results.append((name, False))

    # 异步测试
    async_results = asyncio.run(run_async_tests())
    results.extend(async_results)

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
        print("\n🎉 所有测试通过！学习中心API已就绪。")
    else:
        print(f"\n⚠ {total - passed} 个测试失败，请检查。")


if __name__ == "__main__":
    main()
