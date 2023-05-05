import hashlib
import datetime

from sqlalchemy.exc import SQLAlchemyError

from chatgpt_wrapper.backends.openai.orm import Manager, Character

class CharacterManager(Manager):

    def character_found_message(self, character):
        found = "found" if character else "not found"
        return f"Character {found}."

    def get_by_name(self, character_name):
        try:
            character_name = character_name.lower()
            character = self.orm.session.query(Character).filter(
                (Character.name == character_name)
            ).first()
        except SQLAlchemyError as e:
            return self._handle_error(f"Failed to get character: {str(e)}")
        return True, character, self.character_found_message(character)
   
    def get_names(self, limit=None, offset=None):
        try:
            characters = self.orm.get_character_names(limit, offset)
        except SQLAlchemyError as e:
            return self._handle_error(f"Failed to get users: {str(e)}")
        return True, characters, "Characters retrieved."