import os
from typing import AsyncGenerator
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base, DeclarativeMeta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
# import databases

SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL', default=f'mysql+aiomysql://root:admin@localhost/fastapi_gpt_chatter')
# SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL', default=f'mysql+aiomysql://pyl:pyl123456@localhost/gpt_chatter')

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)

# 创建异步Session
async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# 用于异步连接
# database = databases.Database(SQLALCHEMY_DATABASE_URL)

# ORM的基类
# Base = declarative_base()

# metadata = MetaData()
# Base: DeclarativeMeta = declarative_base(metadata=metadata)
Base: DeclarativeMeta = declarative_base()

# Asynchronously create all tables
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session