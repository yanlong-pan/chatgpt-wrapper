from sqlalchemy.exc import SQLAlchemyError

from chatgpt_wrapper.backends.openai.orm import Conversation, Manager

class ConversationManager(Manager):
    def get_conversations(self, user_id, limit=None, offset=None, order_desc=True):
        try:
            user = Conversation.get_user(user_id)
            conversations = Conversation.get_conversations(user, limit, offset, order_desc)
            return True, conversations, "Conversations retrieved successfully."
        except SQLAlchemyError as e:
            return self._handle_error(f"Failed to retrieve conversations: {str(e)}")

    def add_conversation(self, user_id, character_id, title=None, model="default", hidden=False):
        try:
            conversation = Conversation.add_conversation(user_id, character_id, title, model, hidden)
            return True, conversation, "Conversation created successfully."
        except SQLAlchemyError as e:
            return self._handle_error(f"Failed to create conversation: {str(e)}")

    def get_conversation(self, conversation_id):
        try:
            conversation = Conversation.get_conversation(conversation_id)
            if conversation:
                return True, conversation, "Conversation retrieved successfully."
            else:
                return False, None, "Conversation not found."
        except SQLAlchemyError as e:
            return self._handle_error(f"Failed to retrieve conversation: {str(e)}")

    def get_conversation_by_user_and_character(self, user_id, character_id):
        try:
            conversation = Conversation.query.filter_by(user_id=user_id, character_id=character_id).first()
            if conversation:
                return True, conversation, "Conversation retrieved successfully."
            else:
                return False, None, "Conversation not found."
        except Exception as e:
            return self._handle_error(f"Failed to retrieve conversation: {str(e)}")

    def edit_conversation(self, conversation_id, **kwargs):
        success, conversation, message = self.get_conversation(conversation_id)
        if not success:
            return success, conversation, message
        if not conversation:
            return False, None, "Conversation not found"
        try:
            updated_conversation = Conversation.edit_conversation(conversation, **kwargs)
        except SQLAlchemyError as e:
            return self._handle_error(f"Failed to edit conversation: {str(e)}")
        return True, updated_conversation, "Conversation edited successfully"

    def edit_conversation_title(self, conversation_id, new_title):
        success, conversation, message = self.get_conversation(conversation_id)
        if not success:
            return success, conversation, message
        try:
            updated_conversation = Conversation.edit_conversation(conversation, title=new_title)
        except SQLAlchemyError as e:
            return self._handle_error(f"Failed to update conversation title: {str(e)}")
        return True, updated_conversation, "Conversation title updated successfully."

    def hide_conversation(self, conversation_id):
        success, conversation, message = self.get_conversation(conversation_id)
        if not success:
            return success, conversation, message
        try:
            updated_conversation = Conversation.edit_conversation(conversation, hidden=True)
        except SQLAlchemyError as e:
            return self._handle_error(f"Failed to hide conversation: {str(e)}")
        return True, updated_conversation, "Conversation hidden successfully."

    def unhide_conversation(self, conversation_id):
        success, conversation, message = self.get_conversation(conversation_id)
        if not success:
            return success, conversation, message
        try:
            updated_conversation = Conversation.edit_conversation(conversation, hidden=False)
        except SQLAlchemyError as e:
            return self._handle_error(f"Failed to unhide conversation: {str(e)}")
        return True, updated_conversation, "Conversation unhidden successfully."

    def delete_conversation(self, user_id, conversation_id):
        conversation = Conversation.get_user_conversation(user_id, conversation_id)
        if not conversation:
            return False, conversation, "Conversation not found"
        try:
            Conversation.delete_conversation(conversation)
        except SQLAlchemyError as e:
            return self._handle_error(f"Failed to delete conversation: {str(e)}")
        return True, None, "Conversation deleted successfully."
