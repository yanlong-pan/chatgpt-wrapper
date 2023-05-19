from flask import Blueprint, jsonify, request
from flask_login import login_required
from chatgpt_wrapper.blueprints.response_handlers import success_json_response

from chatgpt_wrapper.utils.cache import get_cached_characters

characters_bp = Blueprint('characters', __name__, url_prefix='/api/v1/characters')

def concat_resource_url(path):
    return request.host_url + path if path else ''

@characters_bp.route('/', methods=['GET'])
@login_required
def list_characters():
    characters = [
        {key: {
            'avatar': concat_resource_url(value.get('avatar')),
            'voice': concat_resource_url(value.get('voice')),
        }} 
        for item in get_cached_characters() 
        for key, value in item.items() 
    ]
    return success_json_response({'characters': characters})
   

    
