from sqlalchemy import JSON, Boolean, Column, DateTime, Index, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy import func, select
from chatgpt_wrapper.backends.openai.orm import Orm
from chatgpt_wrapper.database import Base, async_session

class BaseModel(Base):
    __abstract__ = True
    is_deleted = Column(Boolean, default=False)
    
    async def soft_delete(self):
        async with async_session.begin() as session:
            self.is_deleted = True
            await session.flush()

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



class User(BaseModel):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    default_model = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    last_login_at = Column(DateTime, nullable=False)
    preferences = Column(JSON, nullable=False)

    # conversations = relationship('Conversation', backref='user', passive_deletes=True)

    __table_args__ = (
        Index('user_username_idx', username, unique=True),
        Index('user_email_idx', email, unique=True),
        Index('user_created_at_idx', created_at),
        Index('user_last_login_at', last_login_at),
    )
    
    @classmethod
    async def get_user_by_name_or_email(cls, username, email, strict_match=True):
        username_filter = cls.username == username
        email_filter = cls.email == email
        if not strict_match:
            username_filter |= cls.email == username
            email_filter |= cls.username == email

        async with async_session.begin() as session:
            results = await session.execute(select(cls).where(username_filter | email_filter))
            return results.scalar()