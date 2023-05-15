import datetime
import gc
import threading
from typing import List
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, func
from chatgpt_wrapper.core import constants
from chatgpt_wrapper.core.logger import logger

db = SQLAlchemy()

class Orm(object):
    
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


class Base(db.Model, Orm):
    __abstract__ = True

    is_deleted = db.Column(db.Boolean, default=False)
    
    def soft_delete(self):
        self.is_deleted = True
        db.session.commit()
    
class User(Base, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    default_model = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    last_login_at = db.Column(db.DateTime, nullable=False)
    preferences = db.Column(db.JSON, nullable=False)

    conversations = db.relationship('Conversation', backref='user', passive_deletes=True)

    __table_args__ = (
        db.Index('user_username_idx', username, unique=True),
        db.Index('user_email_idx', email, unique=True),
        db.Index('user_created_at_idx', created_at),
        db.Index('user_last_login_at', last_login_at),
    )

    @classmethod
    def add_user(cls, username, password, email, default_model="default", preferences={}):
        now = datetime.datetime.now()
        user = cls(username=username, password=password, email=email, default_model=default_model, created_at=now, last_login_at=now, preferences=preferences)
        db.session.add(user)
        db.session.commit()
        logger.info(f'Added User with username {username}')
        return user
    
    @classmethod
    def get_user(cls, user_id):
        logger.debug(f'Retrieving User with id {user_id} {threading.current_thread().name}')
        user = cls.query.get(user_id)
        return user

    @classmethod
    def get_user_by_name_or_email(cls, username, email, strict_match=True):
        username_filter = cls.username == username
        email_filter = cls.email == email
        if not strict_match:
            username_filter |= cls.email == username
            email_filter |= cls.username == email
        return cls.query.filter(username_filter | email_filter).first()
        
    @classmethod
    def edit_user(cls, user, **kwargs):
        for key, value in kwargs.items():
            setattr(user, key, value)
        db.session.commit()
        logger.info(f'Edited User with id {user.id}')
        return user
        
class Character(Base):
    __tablename__ = 'character'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    avatar = db.Column(db.String(255), unique=True, nullable=True)
    voice = db.Column(db.String(255), unique=True, nullable=True)
    profile = db.Column(db.Text, nullable=False)

    __table_args__ = (
        db.Index('character_name_idx', name, unique=True),
    )
    
    conversations = db.relationship('Conversation', backref='character', lazy=True, passive_deletes=True)
    
    @classmethod
    def get_characters(cls, limit=None, offset=None):
        logger.debug('Retrieving character information')
        query = cls.query.with_entities(cls.name, cls.avatar, cls.voice).order_by(cls.name)
        query = cls._apply_limit_offset(query, limit, offset)
        results = query.all()
        character_info = [
            {
                name: {
                    'avatar': avatar,
                    'voice': voice
                }
            }
            for name, avatar, voice in results
        ]
        return character_info

    @classmethod
    def get_character_by_name(cls, character_name: str) -> 'Character':
        return cls.query.filter(func.lower(cls.name) == character_name.lower()).one()

class Conversation(Base):
    __tablename__ = 'conversation'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    model = db.Column(db.String(255), nullable=False)
    created_time = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_time = db.Column(db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now())
    hidden = db.Column(db.Boolean, nullable=False)

    messages = db.relationship('Message', backref='conversation', passive_deletes=True)

    __table_args__ = (
        db.Index('conversation_user_id_idx', user_id),
        db.Index('conversation_character_id_idx', character_id),
        db.Index('conversation_created_time_idx', created_time),
        db.Index('conversation_updated_time_idx', updated_time),
        db.Index('conversation_hidden_idx', hidden),
    )
    
    @classmethod
    def get_conversations(cls, user_id, limit=constants.DEFAULT_HISTORY_LIMIT, offset=None, order_desc=True) -> List['Conversation']:
        logger.debug(f'Retrieving Conversations for User with id {user_id}')
        if order_desc:
            query = cls.query.filter_by(user_id=user_id, is_deleted=False).order_by(desc(cls.id))
        else:
            query = cls.query.order_by(cls.id)
        query = cls._apply_limit_offset(query, limit, offset)
        return query.all()
    
    @classmethod
    def add_conversation(cls, user_id, character_id, title, model="default", hidden=False):
        now = datetime.datetime.now()
        conversation = cls(user_id=user_id, character_id = character_id, title=title, model=model, created_time=now, updated_time=now, hidden=False)
        db.session.add(conversation)
        db.session.commit()
        logger.info(f"Added Conversation with title '{title}' for User {User.get_user(user_id).username}")
        return conversation
    
    @classmethod
    def get_conversation(cls, conversation_id):
        logger.debug(f'Retrieving Conversation with id {conversation_id}')
        conversation = db.session.get(cls, conversation_id)
        return conversation

    @classmethod
    def get_user_conversation(cls, user_id, conversation_id):
        return cls.query.filter_by(user_id=user_id, id=conversation_id).first()
        
    @classmethod
    def edit_conversation(cls, conversation, **kwargs):
        for key, value in kwargs.items():
            setattr(conversation, key, value)
        db.session.commit()
        logger.info(f'Edited Conversation with id {conversation.id}')
        return conversation

    @classmethod
    def delete_conversation(cls, conversation):
        conversation.soft_delete()
        logger.info(f'Deleted Conversation with id {conversation.id}')
        # Soft delete all associated messages
        for message in conversation.messages:
            message.soft_delete()
            logger.info(f'Deleted Message with id {message.id}')

class Message(Base):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id', ondelete='CASCADE'), nullable=False)
    role = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_time = db.Column(db.DateTime, nullable=False, default=db.func.now())
    prompt_tokens = db.Column(db.Integer, nullable=False)
    completion_tokens = db.Column(db.Integer, nullable=False)

    # conversation = db.relationship('Conversation', back_populates='messages')

    __table_args__ = (
        db.Index('message_conversation_id_idx', conversation_id),
        db.Index('message_created_time_idx', created_time),
    )
    
    @classmethod
    def get_messages(cls, conversation_id, limit=None, offset=None, target_id=None) -> List['Message']:
        logger.debug(f'Retrieving Messages for Conversation with id {conversation_id}')
        query = cls.query.filter_by(conversation_id=conversation_id, is_deleted=False).order_by(cls.id)
        query = cls._apply_limit_offset(query, limit, offset)
        if target_id:
            query = query.filter(cls.id <= target_id)
        messages = query.all()
        return messages

    @classmethod
    def add_message(cls, conversation_id, role, message):
        now = datetime.datetime.now()
        message = cls(conversation_id=conversation_id, role=role, message=message, created_time=now, prompt_tokens=0, completion_tokens=0)
        db.session.add(message)
        db.session.commit()
        logger.info(f"Added Message with role '{role}' for Conversation with id {conversation_id}")
        return message
    
    @classmethod
    def add_messages(cls, conversation_id, messages: List[dict]):
        now = datetime.datetime.now()
        msgs = list(map(lambda m: cls(
                conversation_id=conversation_id,
                role=m.get('role'),
                message = m.get('content'),
                created_time=now,
                prompt_tokens=0,
                completion_tokens=0
            ),
            messages))
        logger.debug(messages)
        db.session.add_all(msgs)
        db.session.commit()
        logger.info(f"Added Messages for Conversation with id {conversation_id}")
        return msgs

    @classmethod
    def get_message(cls, message_id):
        logger.debug(f'Retrieving Message with id {message_id}')
        message = db.session.get(cls, message_id)
        return message

    @classmethod
    def edit_message(cls, message, **kwargs):
        for key, value in kwargs.items():
            setattr(message, key, value)
        db.session.commit()
        logger.info(f'Edited Message with id {message.id}')
        return message

    @classmethod
    def delete_message(cls, message):
        message.soft_delete()
        logger.info(f'Deleted Message with id {message.id}')

class Manager:

    def _handle_error(self, message):
        logger.error(message)
        return False, None, message
