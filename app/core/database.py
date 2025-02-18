from sqlalchemy import QueuePool, create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, Session


class Database:
    def __init__(self, db_user: str, db_pass: str, db_host: str, db_port: int, db_name: str):
        # 创建数据库引擎（这里使用 SQLite 数据库）
        self.engine = create_engine(
            f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}",
            echo=False,
            poolclass=QueuePool,  # 使用连接池
            pool_size=5,  # 设置连接池大小
            max_overflow=100,  # 设置最大溢出连接数
            execution_options={
                # "compiled_cache": None,  # 禁用编译缓存
            },
        )
        
        # 创建一个全局的 session
        self.session = scoped_session(sessionmaker(bind=self.engine))


# 创建基础类
Base = declarative_base()

# 在 Base 上定义 query_property
# Base.query = Session.query_property()
