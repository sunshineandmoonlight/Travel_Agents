"""
测试 PostgreSQL 数据库设置

验证数据库连接和模型创建
"""

import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from sqlalchemy import text
from app.db.travel_db import DatabaseManager, DatabaseConfig, get_db_context
from app.models.travel import (
    Base, User, TravelGuide, UserBookmark, GuideReview,
    GuideLike, GuideShare, GuideVersion, Attraction,
    GuideTemplate, GuideRecommendation
)


def test_connection(config: DatabaseConfig):
    """测试数据库连接"""
    print(f"测试数据库连接: {config.url}")

    try:
        # 初始化数据库
        engine = DatabaseManager.initialize(config)

        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"  数据库版本: {version[:50]}...")

        print("  连接成功!")
        return True

    except Exception as e:
        print(f"  连接失败: {e}")
        return False


def test_models():
    """测试模型创建"""
    print("\n测试模型创建...")

    try:
        # 创建所有表
        engine = DatabaseManager.get_engine()
        Base.metadata.create_all(engine)

        print("  所有表创建成功!")

        # 列出所有表
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
            """))
            tables = [row[0] for row in result.fetchall()]

        print(f"  创建了 {len(tables)} 张表:")
        for table in tables:
            print(f"    - {table}")

        return True

    except Exception as e:
        print(f"  模型创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_operations():
    """测试会话操作"""
    print("\n测试会话操作...")

    try:
        with get_db_context() as session:
            # 测试查询
            user_count = session.query(User).count()
            guide_count = session.query(TravelGuide).count()

            print(f"  用户数: {user_count}")
            print(f"  攻略数: {guide_count}")

        print("  会话操作成功!")
        return True

    except Exception as e:
        print(f"  会话操作失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sample_data():
    """测试插入示例数据"""
    print("\n测试插入示例数据...")

    try:
        with get_db_context() as session:
            # 检查是否已有测试用户
            existing_user = session.query(User).filter_by(username='test_user').first()
            if existing_user:
                print("  测试用户已存在，跳过创建")
                return True

            # 创建测试用户
            user = User(
                username='test_user',
                email='test@example.com',
                password_hash='test_hash',
                nickname='测试用户',
                role='user'
            )
            session.add(user)
            session.flush()

            # 创建测试攻略
            guide = TravelGuide(
                title='北京5日深度游',
                description='探索北京的历史文化',
                destination='北京',
                destination_type='domestic',
                days=5,
                budget_level='medium',
                travelers_count=2,
                travel_style='immersive',
                interest_tags=['历史', '文化', '美食'],
                user_id=user.id,
                username='test_user',
                status='published'
            )
            session.add(guide)
            session.flush()

            print(f"  创建用户: {user.username} (ID: {user.id})")
            print(f"  创建攻略: {guide.title} (ID: {guide.id})")

        print("  示例数据插入成功!")
        return True

    except Exception as e:
        print(f"  示例数据插入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("PostgreSQL 数据库设置测试")
    print("=" * 60)

    # 从环境变量获取配置
    config = DatabaseConfig(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_PORT', 5432)),
        database=os.getenv('POSTGRES_DB', 'travelagents'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'postgres')
    )

    results = []

    # 测试连接
    results.append(('数据库连接', test_connection(config)))

    if results[0][1]:  # 连接成功才继续测试
        # 测试模型
        results.append(('模型创建', test_models()))

        # 测试会话操作
        results.append(('会话操作', test_session_operations()))

        # 测试示例数据
        results.append(('示例数据', test_sample_data()))

    # 输出结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    for name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"  [{status}] {name}")

    # 关闭连接
    DatabaseManager.close()

    # 返回结果
    all_passed = all(r[1] for r in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("所有测试通过!")
    else:
        print("部分测试失败，请检查配置")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
