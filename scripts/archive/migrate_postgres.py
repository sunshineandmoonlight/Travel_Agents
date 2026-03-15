"""
PostgreSQL 数据库迁移脚本

用于初始化和管理旅行系统数据库的迁移
"""

import os
import sys
import asyncio
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('postgres_migration')


class PostgresMigrator:
    """PostgreSQL 数据库迁移管理器"""

    def __init__(self, connection_params: dict):
        """
        初始化迁移管理器

        Args:
            connection_params: 数据库连接参数
                - host: 主机地址
                - port: 端口
                - database: 数据库名
                - user: 用户名
                - password: 密码
        """
        self.connection_params = connection_params
        self.schema_path = project_root / "app" / "schemas" / "travel_schema.sql"

    def _get_connection(self, database: str = None):
        """获取数据库连接"""
        params = self.connection_params.copy()
        if database:
            params['database'] = database

        return psycopg2.connect(**params)

    def create_database_if_not_exists(self):
        """创建数据库（如果不存在）"""
        db_name = self.connection_params.get('database', 'travelagents')

        logger.info(f"检查数据库: {db_name}")

        try:
            # 连接到默认数据库
            conn = self._get_connection(database='postgres')
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            # 检查数据库是否存在
            cursor.execute(
                sql.SQL("SELECT 1 FROM pg_database WHERE datname = {}").format(
                    sql.Literal(db_name)
                )
            )

            if not cursor.fetchone():
                # 创建数据库
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(db_name)
                    )
                )
                logger.info(f"数据库 {db_name} 创建成功")
            else:
                logger.info(f"数据库 {db_name} 已存在")

            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"创建数据库失败: {e}")
            raise

    def execute_schema(self):
        """执行数据库 schema"""
        logger.info("开始执行数据库 schema...")

        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema 文件不存在: {self.schema_path}")

        # 读取 schema 文件
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # 分割 SQL 语句（按分号分隔，但要处理函数内的分号）
        statements = self._split_sql(schema_sql)

        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            executed = 0
            for statement in statements:
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    try:
                        cursor.execute(statement)
                        executed += 1
                    except psycopg2.Error as e:
                        # 忽略 "已存在" 错误
                        if 'already exists' in str(e):
                            logger.debug(f"对象已存在，跳过: {e}")
                        else:
                            logger.warning(f"执行语句失败: {e}")
                            logger.debug(f"语句: {statement[:100]}...")

            conn.commit()
            logger.info(f"Schema 执行完成，执行了 {executed} 条语句")

            cursor.close()
        except Exception as e:
            conn.rollback()
            logger.error(f"执行 schema 失败: {e}")
            raise
        finally:
            conn.close()

    def _split_sql(self, sql_content: str) -> list:
        """
        分割 SQL 语句，处理函数体内的分号

        Args:
            sql_content: SQL 内容

        Returns:
            SQL 语句列表
        """
        statements = []
        current = []
        in_function = False
        paren_count = 0
        dollar_quote = None

        for line in sql_content.split('\n'):
            # 跳过注释和空行
            stripped = line.strip()
            if not stripped or stripped.startswith('--'):
                current.append(line)
                continue

            # 检测 $...$ 引用
            if '$$' in line:
                if dollar_quote is None:
                    dollar_quote = '$$'
                    in_function = True
                else:
                    dollar_quote = None
                current.append(line)
                continue

            # 跟踪括号
            for char in line:
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count = max(0, paren_count - 1)

            current.append(line)

            # 检测语句结束（分号且不在函数内）
            if ';' in line and paren_count == 0 and dollar_quote is None:
                statements.append('\n'.join(current))
                current = []

        # 处理剩余内容
        if current:
            statements.append('\n'.join(current))

        return statements

    def verify_schema(self):
        """验证数据库 schema 是否正确创建"""
        logger.info("验证数据库 schema...")

        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # 检查核心表是否存在
            expected_tables = [
                'users', 'travel_guides', 'user_bookmarks', 'guide_reviews',
                'guide_likes', 'guide_shares', 'guide_versions',
                'attractions_database', 'guide_templates', 'guide_recommendations'
            ]

            cursor.execute("""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
            """)

            existing_tables = {row[0] for row in cursor.fetchall()}
            missing_tables = set(expected_tables) - existing_tables

            if missing_tables:
                logger.warning(f"缺少表: {missing_tables}")
                return False

            # 检查索引
            cursor.execute("""
                SELECT indexname
                FROM pg_indexes
                WHERE schemaname = 'public'
            """)

            index_count = cursor.rowcount
            logger.info(f"已创建 {index_count} 个索引")

            # 检查视图
            cursor.execute("""
                SELECT viewname
                FROM pg_views
                WHERE schemaname = 'public'
            """)

            views = {row[0] for row in cursor.fetchall()}
            expected_views = {'v_published_guides', 'v_user_bookmarks'}
            missing_views = expected_views - views

            if missing_views:
                logger.warning(f"缺少视图: {missing_views}")
                return False

            logger.info("Schema 验证通过")
            return True

        finally:
            conn.close()

    def get_migration_version(self) -> str:
        """获取当前迁移版本"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(
                    (SELECT current_version FROM schema_version LIMIT 1),
                    '0.0.0'
                )
            """)
            version = cursor.fetchone()[0]
            return version
        except Exception:
            return "0.0.0"
        finally:
            conn.close()

    def update_migration_version(self, version: str, description: str = ""):
        """更新迁移版本"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # 创建版本表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    id SERIAL PRIMARY KEY,
                    current_version VARCHAR(20) NOT NULL,
                    description TEXT,
                    migrated_at TIMESTAMP DEFAULT NOW()
                )
            """)

            # 更新版本
            cursor.execute("DELETE FROM schema_version")
            cursor.execute("""
                INSERT INTO schema_version (current_version, description)
                VALUES (%s, %s)
            """, (version, description))

            conn.commit()
            logger.info(f"迁移版本更新: {version} - {description}")

        finally:
            conn.close()

    def run_migration(self):
        """执行完整迁移流程"""
        logger.info("=" * 60)
        logger.info("开始 PostgreSQL 数据库迁移")
        logger.info("=" * 60)

        try:
            # 1. 创建数据库
            self.create_database_if_not_exists()

            # 2. 执行 schema
            self.execute_schema()

            # 3. 验证 schema
            if not self.verify_schema():
                raise Exception("Schema 验证失败")

            # 4. 更新迁移版本
            self.update_migration_version(
                "1.0.0",
                "旅行系统初始 schema - 10张表 + 触发器 + 视图"
            )

            logger.info("=" * 60)
            logger.info("数据库迁移完成！")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"迁移失败: {e}")
            raise


def get_connection_params_from_env() -> dict:
    """从环境变量获取数据库连接参数"""
    return {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', 5432)),
        'database': os.getenv('POSTGRES_DB', 'travelagents'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'postgres')
    }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='PostgreSQL 数据库迁移工具')
    parser.add_argument(
        '--host', default='localhost',
        help='数据库主机'
    )
    parser.add_argument(
        '--port', type=int, default=5432,
        help='数据库端口'
    )
    parser.add_argument(
        '--database', default='travelagents',
        help='数据库名称'
    )
    parser.add_argument(
        '--user', default='postgres',
        help='数据库用户'
    )
    parser.add_argument(
        '--password', default='postgres',
        help='数据库密码'
    )
    parser.add_argument(
        '--verify-only', action='store_true',
        help='仅验证 schema，不执行迁移'
    )
    parser.add_argument(
        '--drop-first', action='store_true',
        help='先删除已存在的数据库（危险操作！）'
    )

    args = parser.parse_args()

    # 构建连接参数
    connection_params = {
        'host': args.host,
        'port': args.port,
        'database': args.database,
        'user': args.user,
        'password': args.password
    }

    migrator = PostgresMigrator(connection_params)

    # 删除数据库（如果指定）
    if args.drop_first:
        logger.warning(f"将删除数据库: {args.database}")
        confirm = input("确认删除？(yes/no): ")
        if confirm.lower() == 'yes':
            conn = migrator._get_connection(database='postgres')
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            cursor.execute(
                sql.SQL("DROP DATABASE IF EXISTS {}").format(
                    sql.Identifier(args.database)
                )
            )
            cursor.close()
            conn.close()
            logger.info(f"数据库 {args.database} 已删除")
        else:
            logger.info("取消操作")
            return

    # 仅验证
    if args.verify_only:
        success = migrator.verify_schema()
        sys.exit(0 if success else 1)

    # 执行迁移
    migrator.run_migration()


if __name__ == '__main__':
    main()
