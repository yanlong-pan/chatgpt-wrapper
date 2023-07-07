import os
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import databases


SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL', default=f'mysql+aiomysql://pyl:pyl123456@localhost/gpt_chatter')

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)

# 创建异步Session
async_session = sessionmaker(bind=engine, class_=AsyncSession)

# 用于异步连接
database = databases.Database(SQLALCHEMY_DATABASE_URL)

# ORM的基类
Base = declarative_base()
