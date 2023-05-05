import datetime
from typing import List
from flask_login import UserMixin

from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection
from sqlalchemy import Text, event, MetaData, ForeignKey, Index, Column, Integer, String, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship, declarative_base, scoped_session, sessionmaker
from sqlalchemy import desc, create_engine, inspect

from chatgpt_wrapper.core.config import Config
from chatgpt_wrapper.core.logger import Logger
import chatgpt_wrapper.core.constants as constants

Base = declarative_base()
def _set_sqlite_pragma(conn, _record):
    if isinstance(conn, SQLite3Connection):
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()
event.listen(Engine, "connect", _set_sqlite_pragma)

class User(Base, UserMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    default_model = Column(String, nullable=False)
    created_time = Column(DateTime, nullable=False)
    last_login_time = Column(DateTime, nullable=True)
    preferences = Column(JSON, nullable=False)

    conversations = relationship('Conversation', back_populates='user', passive_deletes=True)

    @property
    def gpt(self):
        return getattr(self, '_gpt', None)

    @gpt.setter
    def gpt(self, value):
        self._gpt = value
    
    __table_args__ = (
        Index('user_username_idx', username, unique=True),
        Index('user_email_idx', email, unique=True),
        Index('user_created_time_idx', created_time),
        Index('user_last_login_time', last_login_time),
    )

class Character(Base):
    __tablename__ = 'character'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    profile = Column(Text, nullable=False)

    __table_args__ = (
        Index('character_name_idx', name, unique=True),
    )
    
    conversations = relationship('Conversation', back_populates='character', passive_deletes=True)
    

class Conversation(Base):
    __tablename__ = 'conversation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    character_id = Column(Integer, ForeignKey('character.id', ondelete='CASCADE'), nullable=False)
    title = Column(String, nullable=True)
    model = Column(String, nullable=False)
    created_time = Column(DateTime, nullable=False)
    updated_time = Column(DateTime, nullable=False)
    hidden = Column(Boolean, nullable=False)

    user = relationship('User', back_populates='conversations')
    character = relationship('Character', back_populates='conversations')
    messages = relationship('Message', back_populates='conversation', passive_deletes=True)
    
    __table_args__ = (
        Index('conversation_user_id_idx', user_id),
        Index('conversation_character_id_idx', character_id),
        Index('conversation_created_time_idx', created_time),
        Index('conversation_updated_time_idx', updated_time),
        Index('conversation_hidden_idx', hidden),
    )

class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey('conversation.id', ondelete='CASCADE'), nullable=False)
    role = Column(String, nullable=False)
    message = Column(String, nullable=False)
    created_time = Column(DateTime, nullable=False)
    prompt_tokens = Column(Integer, nullable=False)
    completion_tokens = Column(Integer, nullable=False)

    conversation = relationship('Conversation', back_populates='messages')

    __table_args__ = (
        Index('message_conversation_id_idx', conversation_id),
        Index('message_created_time_idx', created_time),
    )

class Orm:
    def __init__(self, config=None):
        self.config = config or Config()
        self.log = Logger(self.__class__.__name__, self.config)
        self.database = self.config.get('database')
        self.engine, self.metadata = self.create_engine_and_metadata()
        session = scoped_session(sessionmaker(bind=self.engine))
        self.session = session()

    def _apply_limit_offset(self, query, limit, offset):
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        return query

    def create_engine_and_metadata(self):
        args = ""
        # TODO: check_same_thread is currently needed for SQLite so the
        # separate thread that generates titles can run without error.
        # It would probably be better to work this out with locking or
        # a separate database connection or other fix.
        if self.database.startswith('sqlite'):
            args = "?check_same_thread=False"
        engine = create_engine(f"{self.database}{args}")
        metadata = MetaData()
        metadata.reflect(bind=engine)
        return engine, metadata

    def object_as_dict(self, obj):
        return {c.key: getattr(obj, c.key)
                for c in inspect(obj).mapper.column_attrs}

    def get_users(self, limit=None, offset=None) -> List[User]:
        self.log.debug('Retrieving all Users')
        query = self.session.query(User).order_by(User.username)
        query = self._apply_limit_offset(query, limit, offset)
        users = query.all()
        return users
    
    def get_character_names(self, limit=None, offset=None) -> List[str]:
        self.log.debug('Retrieving all Characters')
        query = self.session.query(Character.name).order_by(Character.name)
        query = self._apply_limit_offset(query, limit, offset)
        names = query.all()
        return [name for (name,) in names]

    def get_conversations(self, user, limit=constants.DEFAULT_HISTORY_LIMIT, offset=None, order_desc=True) -> List[Conversation]:
        self.log.debug(f'Retrieving Conversations for User with id {user.id}')
        if order_desc:
            query = self.session.query(Conversation).filter(Conversation.user_id == user.id).order_by(desc(Conversation.id))
        else:
            query = self.session.query(Conversation).order_by(Conversation.id)
        query = self._apply_limit_offset(query, limit, offset)
        conversations = query.all()
        return conversations

    def get_messages(self, conversation, limit=None, offset=None, target_id=None) -> List[Message]:
        self.log.debug(f'Retrieving Messages for Conversation with id {conversation.id}')
        query = self.session.query(Message).filter(Message.conversation_id == conversation.id).order_by(Message.id)
        query = self._apply_limit_offset(query, limit, offset)
        if target_id:
            query = query.filter(Message.id <= target_id)
        messages = query.all()
        return messages

    def add_user(self, username, password, email, default_model="default", preferences={}):
        now = datetime.datetime.now()
        user = User(username=username, password=password, email=email, default_model=default_model, created_time=now, last_login_time=now, preferences=preferences)
        self.session.add(user)
        self.session.commit()
        self.log.info(f'Added User with username {username}')
        return user

    def add_conversation(self, user, title, model="default", hidden=False):
        now = datetime.datetime.now()
        conversation = Conversation(user_id=user.id, title=title, model=model, created_time=now, updated_time=now, hidden=False)
        self.session.add(conversation)
        self.session.commit()
        self.log.info(f"Added Conversation with title '{title}' for User {user.username}")
        return conversation

    def add_message(self, conversation, role, message):
        now = datetime.datetime.now()
        message = Message(conversation_id=conversation.id, role=role, message=message, created_time=now, prompt_tokens=0, completion_tokens=0)
        self.session.add(message)
        self.session.commit()
        self.log.info(f"Added Message with role '{role}' for Conversation with id {conversation.id}")
        return message

    def get_user(self, user_id):
        self.log.debug(f'Retrieving User with id {user_id}')
        user = self.session.get(User, user_id)
        return user

    def get_conversation(self, conversation_id):
        self.log.debug(f'Retrieving Conversation with id {conversation_id}')
        conversation = self.session.get(Conversation, conversation_id)
        return conversation

    def get_message(self, message_id):
        self.log.debug(f'Retrieving Message with id {message_id}')
        message = self.session.get(Message, message_id)
        return message

    def edit_user(self, user, **kwargs):
        for key, value in kwargs.items():
            setattr(user, key, value)
        self.session.commit()
        self.log.info(f'Edited User with id {user.id}')
        return user

    def edit_conversation(self, conversation, **kwargs):
        for key, value in kwargs.items():
            setattr(conversation, key, value)
        self.session.commit()
        self.log.info(f'Edited Conversation with id {conversation.id}')
        return conversation

    def edit_message(self, message, **kwargs):
        for key, value in kwargs.items():
            setattr(message, key, value)
        self.session.commit()
        self.log.info(f'Edited Message with id {message.id}')
        return message

    def delete_user(self, user):
        self.session.delete(user)
        self.session.commit()
        self.log.info(f'Deleted User with id {user.id}')
        return user

    def delete_conversation(self, conversation):
        self.session.delete(conversation)
        self.session.commit()
        self.log.info(f'Deleted Conversation with id {conversation.id}')

    def delete_message(self, message):
        self.session.delete(message)
        self.session.commit()
        self.log.info(f'Deleted Message with id {message.id}')

class Manager:
    def __init__(self, config=None):
        self.config = config or Config()
        self.log = Logger(self.__class__.__name__, self.config)
        self.orm = Orm(self.config)

    def _handle_error(self, message):
        self.log.error(message)
        return False, None, message
