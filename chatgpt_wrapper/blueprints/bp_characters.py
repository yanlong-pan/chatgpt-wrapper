from flask import Blueprint, jsonify
from flask_login import login_required

from chatgpt_wrapper.utils.cache import get_cached_character_names

characters_bp = Blueprint('characters', __name__, url_prefix='/api/v1/characters')

@characters_bp.route('/', methods=['GET'])
@login_required
def list_characters():
    return jsonify(get_cached_character_names()), 201
   

    
