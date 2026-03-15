"""
旅行系统数据库连接管理

提供 PostgreSQL 连接池和会话管理
"""

import os
from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import QueuePool
import logging

from app.models.travel import Base

logger = logging.getLogger(__name__)


# ============================================================
# 数据库配置
# ============================================================

class DatabaseConfig:
    """数据库配置类"""

    def __init__(
        self,
        host: str = None,
        port: int = None,
        database: str = None,
        user: str = None,
        password: str = None,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        echo: bool = False
    ):
        self.host = host or os.getenv('POSTGRES_HOST', 'localhost')
        self.port = port or int(os.getenv('POSTGRES_PORT', 5432))
        self.database = database or os.getenv('POSTGRES_DB', 'travelagents')
        self.user = user or os.getenv('POSTGRES_USER', 'postgres')
        self.password = password or os.getenv('POSTGRES_PASSWORD', 'postgres')

        # 连接池配置
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.echo = echo

    @property
    def url(self) -> str:
        """生成数据库连接 URL"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """从环境变量创建配置"""
        return cls(
            host=os.getenv('POSTGRES_HOST'),
            port=int(os.getenv('POSTGRES_PORT', 5432)),
            database=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            echo=os.getenv('POSTGRES_ECHO', 'false').lower() == 'true'
        )


# ============================================================
# 数据库引擎管理
# ============================================================

class DatabaseManager:
    """
    数据库管理器

    管理数据库引擎、会话工厂和连接池
    """

    _engine: Optional[Engine] = None
    _session_factory: Optional[sessionmaker] = None
    _scoped_session_factory: Optional[scoped_session] = None

    @classmethod
    def initialize(
        cls,
        config: DatabaseConfig = None,
        engine: Engine = None
    ) -> Engine:
        """
        初始化数据库连接

        Args:
            config: 数据库配置
            engine: 已存在的引擎（用于测试）

        Returns:
            SQLAlchemy Engine 实例
        """
        if cls._engine is not None:
            logger.warning("数据库引擎已经初始化")
            return cls._engine

        if engine:
            cls._engine = engine
        elif config:
            cls._engine = create_engine(
                config.url,
                poolclass=QueuePool,
                pool_size=config.pool_size,
                max_overflow=config.max_overflow,
                pool_timeout=config.pool_timeout,
                pool_recycle=config.pool_recycle,
                pool_pre_ping=True,  # 检查连接有效性
                echo=config.echo,
                # PostgreSQL 优化
                connect_args={
                    "options": "-c timezone=utc"
                }
            )
        else:
            config = DatabaseConfig.from_env()
            return cls.initialize(config)

        # 创建会话工厂
        cls._session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=cls._engine
        )

        # 创建线程安全的会话工厂
        cls._scoped_session_factory = scoped_session(cls._session_factory)

        logger.info(f"数据库连接初始化成功: {config.url}")

        return cls._engine

    @classmethod
    def get_engine(cls) -> Engine:
        """获取数据库引擎"""
        if cls._engine is None:
            cls.initialize()
        return cls._engine

    @classmethod
    def get_session_factory(cls) -> sessionmaker:
        """获取会话工厂"""
        if cls._session_factory is None:
            cls.initialize()
        return cls._session_factory

    @classmethod
    @contextmanager
    def get_session(cls) -> Generator[Session, None, None]:
        """
        获取数据库会话（上下文管理器）

        用法:
            with DatabaseManager.get_session() as session:
                # 使用 session
                pass
        """
        if cls._scoped_session_factory is None:
            cls.initialize()

        session = cls._scoped_session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @classmethod
    def create_session(cls) -> Session:
        """
        创建新的数据库会话

        注意: 使用后需要手动关闭或使用 commit/rollback

        Returns:
            Session 对象
        """
        if cls._session_factory is None:
            cls.initialize()
        return cls._session_factory()

    @classmethod
    def close(cls):
        """关闭数据库连接"""
        if cls._scoped_session_factory:
            cls._scoped_session_factory.remove()

        if cls._engine:
            cls._engine.dispose()
            cls._engine = None

        logger.info("数据库连接已关闭")

    @classmethod
    def init_tables(cls, engine: Engine = None):
        """
        创建所有表（用于开发/测试）

        Args:
            engine: 可选的引擎，默认使用初始化的引擎
        """
        eng = engine or cls.get_engine()
        Base.metadata.create_all(eng)
        logger.info("数据库表创建完成")

    @classmethod
    def drop_tables(cls, engine: Engine = None):
        """
        删除所有表（危险操作！）

        Args:
            engine: 可选的引擎，默认使用初始化的引擎
        """
        eng = engine or cls.get_engine()
        Base.metadata.drop_all(eng)
        logger.warning("所有数据库表已删除")


# ============================================================
# 便捷函数
# ============================================================

def get_db_session() -> Session:
    """
    获取数据库会话的便捷函数

    Returns:
        Session 对象
    """
    return DatabaseManager.create_session()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    获取数据库会话上下文的便捷函数

    用法:
        with get_db_context() as session:
            guides = session.query(TravelGuide).all()
    """
    with DatabaseManager.get_session() as session:
        yield session


def init_database(config: DatabaseConfig = None):
    """
    初始化数据库连接

    Args:
        config: 数据库配置，默认从环境变量读取
    """
    if config:
        DatabaseManager.initialize(config)
    else:
        DatabaseManager.initialize()


def close_database():
    """关闭数据库连接"""
    DatabaseManager.close()


# ============================================================
# FastAPI 依赖
# ============================================================

def get_db():
    """
    FastAPI 依赖注入函数

    用法:
        @router.get("/guides")
        def get_guides(db: Session = Depends(get_db)):
            return db.query(TravelGuide).all()
    """
    session = DatabaseManager.create_session()
    try:
        yield session
    finally:
        session.close()


# ============================================================
# 测试辅助
# ============================================================

class TestDatabaseManager:
    """测试数据库管理器"""

    @staticmethod
    def create_test_engine(
        database: str = "test_travelagents",
        **kwargs
    ) -> Engine:
        """
        创建测试数据库引擎

        Args:
            database: 测试数据库名
            **kwargs: 其他配置

        Returns:
            Engine 实例
        """
        config = DatabaseConfig(
            host=kwargs.get('host', 'localhost'),
            port=kwargs.get('port', 5432),
            database=database,
            user=kwargs.get('user', 'postgres'),
            password=kwargs.get('password', 'postgres'),
            pool_size=1,
            max_overflow=0,
            echo=False
        )

        # 创建测试数据库
        import psycopg2
        from psycopg2 import sql
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

        conn = psycopg2.connect(
            host=config.host,
            port=config.port,
            user=config.user,
            password=config.password,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # 删除已存在的测试数据库
        cursor.execute(
            sql.SQL("DROP DATABASE IF EXISTS {}").format(
                sql.Identifier(database)
            )
        )
        # 创建新的测试数据库
        cursor.execute(
            sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(database)
            )
        )

        cursor.close()
        conn.close()

        # 创建引擎
        engine = create_engine(
            config.url,
            poolclass=QueuePool,
            pool_size=1,
            max_overflow=0,
            echo=False
        )

        # 创建表
        Base.metadata.create_all(engine)

        return engine

    @staticmethod
    def cleanup_test_engine(engine: Engine, database: str = None):
        """
        清理测试数据库

        Args:
            engine: 引擎实例
            database: 数据库名
        """
        engine.dispose()

        if database:
            import psycopg2
            from psycopg2 import sql
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

            config = DatabaseConfig.from_env()

            conn = psycopg2.connect(
                host=config.host,
                port=config.port,
                user=config.user,
                password=config.password,
                database='postgres'
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            cursor.execute(
                sql.SQL("DROP DATABASE IF EXISTS {}").format(
                    sql.Identifier(database)
                )
            )

            cursor.close()
            conn.close()


# ============================================================
# 导出
# ============================================================

__all__ = [
    'DatabaseConfig',
    'DatabaseManager',
    'get_db_session',
    'get_db_context',
    'init_database',
    'close_database',
    'get_db',
    'TestDatabaseManager',
]
