import datetime
from fastapi import Depends
from sqlalchemy import JSON, Boolean, Column, DateTime, Index, Integer, String
from sqlalchemy import func, select
from sqlalchemy.orm import mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from chatgpt_wrapper.database import Base, async_session, get_async_session
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncAttrs
from chatgpt_wrapper.core.logger import console_logger


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

class BaseModel(AsyncAttrs, Base):
    __abstract__ = True
    is_deleted = Column(Boolean, default=False)
    
    async def soft_delete(self):
        async with async_session.begin() as session:
            self.is_deleted = True
            await session.merge(self)

    @classmethod
    def _apply_limit_offset(cls, query, limit, offset):
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        return query

    def to_json(self, fields=None):
        if fields is None:
            fields = self.__table__.columns.keys()
        return {field: getattr(self, field) for field in fields}



class User(SQLAlchemyBaseUserTable[int], BaseModel):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())
    last_login_at = Column(DateTime, nullable=False)

    # conversations = relationship('Conversation', backref='user', passive_deletes=True)

    __table_args__ = (
        Index('user_email_idx', email, unique=True),
        Index('user_created_at_idx', created_at),
        Index('user_last_login_at', last_login_at),
    )
    
    @classmethod
    async def add_user(cls, email, password):
        now = datetime.datetime.now()
        user = cls(hashed_password=password, email=email, created_at=now, last_login_at=now)
        async with async_session.begin() as session:
            session.add(user)
        console_logger.info(f'Added User with email {email}')
        return user
    
    @classmethod
    async def get_user_by_email(cls, email):
        async with async_session.begin() as session:
            results = await session.execute(select(cls).where(cls.email == email))
            return results.scalars().one()