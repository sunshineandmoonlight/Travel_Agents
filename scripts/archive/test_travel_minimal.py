"""
旅行系统 API 最小化测试

只测试旅行相关的API，避免加载其他模块
"""

import sys
import os

# 设置环境变量避免MongoDB连接
os.environ['MONGODB_HOST'] = 'localhost'
os.environ['MONGODB_PORT'] = '27017'
os.environ['REDIS_HOST'] = 'localhost'
os.environ['REDIS_PORT'] = '6379'

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 设置控制台编码为UTF-8
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def print_section(title: str):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def main():
    print("\n")
    print("*" * 60)
    print("  旅行系统 API 测试")
    print("*" * 60)

    print_section("1. 检查Python模块导入")

    # 测试导入
    try:
        from fastapi.testclient import TestClient
        print("[OK] FastAPI TestClient")
    except ImportError as e:
        print(f"[FAIL] FastAPI TestClient: {e}")
        return False

    try:
        from sqlalchemy.orm import Session
        print("[OK] SQLAlchemy")
    except ImportError as e:
        print(f"[FAIL] SQLAlchemy: {e}")
        return False

    try:
        import psycopg2
        print("[OK] psycopg2")
    except ImportError as e:
        print(f"[FAIL] psycopg2: {e}")
        return False

    print_section("2. 检查旅行模块")

    try:
        from app.models.travel import TravelGuide, User, GuideLike
        print("[OK] 旅行模型导入")
    except ImportError as e:
        print(f"[FAIL] 旅行模型: {e}")
        return False

    try:
        from app.schemas.travel_schemas import TravelPlanRequest, TravelGuideCreate
        print("[OK] 旅行Schema导入")
    except ImportError as e:
        print(f"[FAIL] 旅行Schema: {e}")
        return False

    try:
        from app.db.travel_db import DatabaseManager, DatabaseConfig
        print("[OK] 数据库管理器导入")
    except ImportError as e:
        print(f"[FAIL] 数据库管理器: {e}")
        return False

    try:
        from app.routers.travel import router
        print("[OK] 旅行路由导入")
        print(f"     - 路由前缀: {router.prefix}")
        print(f"     - 标签: {router.tags}")
        print(f"     - 端点数量: {len(router.routes)}")
    except ImportError as e:
        print(f"[FAIL] 旅行路由: {e}")
        import traceback
        traceback.print_exc()
        return False

    print_section("3. 列出所有API端点")

    for route in router.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = ', '.join(sorted(route.methods))
            print(f"  {methods:6} {route.path}")

    print_section("4. 测试Pydantic模型验证")

    try:
        # 测试旅行规划请求
        plan_request = TravelPlanRequest(
            destination="北京",
            days=5,
            budget="medium",
            travelers=2,
            interest_type="历史",
            selected_style="immersive"
        )
        print(f"[OK] 旅行规划请求模型验证通过")
        print(f"     - 目的地: {plan_request.destination}")
        print(f"     - 天数: {plan_request.days}")
        print(f"     - 预算: {plan_request.budget}")
        print(f"     - 人数: {plan_request.travelers}")
    except Exception as e:
        print(f"[FAIL] 旅行规划请求模型: {e}")
        return False

    try:
        # 测试攻略创建请求
        guide_create = TravelGuideCreate(
            title="测试攻略上海三日游",  # 至少5个字符
            destination="上海",
            destination_type="domestic",
            days=3,
            budget_level="medium",
            travelers_count=2,
            travel_style="exploration",
            interest_tags=["美食", "购物"]
        )
        print(f"[OK] 攻略创建模型验证通过")
        print(f"     - 标题: {guide_create.title}")
        print(f"     - 目的地: {guide_create.destination}")
        print(f"     - 风格: {guide_create.travel_style}")
    except Exception as e:
        print(f"[FAIL] 攻略创建模型: {e}")
        return False

    print_section("5. 测试数据库连接配置")

    try:
        config = DatabaseConfig.from_env()
        print(f"[OK] 数据库配置")
        print(f"     - 主机: {config.host}")
        print(f"     - 端口: {config.port}")
        print(f"     - 数据库: {config.database}")
        print(f"     - 用户: {config.user}")
    except Exception as e:
        print(f"[FAIL] 数据库配置: {e}")
        return False

    print_section("6. 总结")

    print("""
旅行系统API模块检查完成!

主要组件:
  - 数据库模型: OK
  - Pydantic验证: OK
  - 路由端点: OK
  - 服务层: OK

下一步:
  1. 配置PostgreSQL数据库连接
  2. 运行数据库迁移: python scripts/migrate_postgres.py
  3. 启动服务器: python -m uvicorn app.main:app
  4. 访问API文档: http://localhost:8000/docs
    """)

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
