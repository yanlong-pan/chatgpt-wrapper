import hashlib
import datetime
from sqlalchemy import func

from sqlalchemy.exc import SQLAlchemyError

from chatgpt_wrapper.backends.openai.orm import Manager, Character

class CharacterManager(Manager):

    def character_found_message(self, character):
        found = "found" if character else "not found"
        return f"Character {found}."

    def get_by_name(self, character_name):
        try:
            character = Character.get_character_by_name(character_name)
        except SQLAlchemyError as e:
            return self._handle_error(f"Failed to get character: {str(e)}")
        return True, character, self.character_found_message(character)