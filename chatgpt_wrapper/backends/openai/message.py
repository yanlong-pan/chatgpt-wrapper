from sqlalchemy.exc import SQLAlchemyError

from chatgpt_wrapper.backends.openai.orm import Conversation, Manager, Message
from chatgpt_wrapper.backends.openai.conversation import ConversationManager

class MessageManager(Manager):
    def __init__(self):
        super().__init__()

    def get_message(self, message_id):
        try:
            message = Message.query.get(message_id)
        except SQLAlchemyError as e:
            return self._handle_error(f"Failed to retrieve message: {str(e)}")
        if not message:
            return False, None, "Message not found"
        return True, message, "Message retrieved successfully"

    def get_messages(self, conversation_id, limit=None, offset=None, target_id=None):
        try:
            messages = Message.get_messages(conversation_id, limit=limit, offset=offset, target_id=None)
        except SQLAlchemyError as e:
            return self._handle_error(f"Failed to retrieve messages: {str(e)}")
        return True, messages, "Messages retrieved successfully"

    def add_messages(self, conversation_id, messages):
        try:
            msgs = Message.add_messages(conversation_id, messages)
        except SQLAlchemyError as e:
            return self._handle_error(f"Failed to add message: {str(e)}")
        return True, msgs, "Messages added successfully"

    def add_message(self, conversation_id, role, message):
        try:
            message = Message.add_message(conversation_id, role, message)
        except SQLAlchemyError as e:
            return self._handle_error(f"Failed to add message: {str(e)}")
        return True, message, "Message added successfully"

    def edit_message(self, message_id, **kwargs):
        success, message, user_message = self.get_message(message_id)
        if not success:
            return success, message, user_message
        if not message:
            return False, None, "Message not found"
        try:
            updated_message = Message.edit_message(message, **kwargs)
        except SQLAlchemyError as e:
            return self._handle_error(f"Failed to edit message: {str(e)}")
        return True, updated_message, "Message edited successfully"

    def delete_message(self, message_id):
        success, message, user_message = self.get_message(message_id)
        if not success:
            return success, message, user_message
        if not message:
            return False, None, "Message not found"
        try:
            Message.delete_message(message)
        except SQLAlchemyError as e:
            return self._handle_error(f"Failed to delete message: {str(e)}")
        return True, None, "Message deleted successfully"
