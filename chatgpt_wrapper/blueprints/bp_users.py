from flask import Blueprint, current_app, jsonify, request
from flask_inputs import Inputs
from flask_inputs.validators import JsonSchema
from flask_login import current_user, login_required, login_user
from chatgpt_wrapper.backends.openai.api import OpenAIAPI

from chatgpt_wrapper.blueprints.error_handlers import default_error_handler
from chatgpt_wrapper.blueprints.json_schemas import user_registration_schema, user_login_schema
from chatgpt_wrapper.decorators.validation import input_validator
from chatgpt_wrapper.profiles.config_loader import load_gpt_config

users_bp = Blueprint('users', __name__, url_prefix='/api/v1/users')

class RegisterInputs(Inputs):
    json = [JsonSchema(schema=user_registration_schema)]
    
class LoginInputs(Inputs):
    json = [JsonSchema(schema=user_login_schema)]

@users_bp.route('/', methods=['POST'])
@input_validator(RegisterInputs)
def create_user():
    data = request.get_json()
    success, user, msg = current_app.user_manager.register(email=data['email'],
                username=data['username'],
                password=data['password'])

    if success:
        return jsonify(current_app.user_manager.orm.object_as_dict(user)), 201
    else:
        return default_error_handler(msg)

@users_bp.route('<int:user_id>', methods=["GET"])
@login_required
def get_user(user_id):
    # Check if the requested user ID matches the authenticated user's ID
    if user_id != current_user.id:
        return jsonify({'error': 'Forbidden', 'current_user_id': current_user.id}), 403
    success, user, msg = current_app.user_manager.get_by_user_id(user_id)
    if success:
        return jsonify(current_app.user_manager.orm.object_as_dict(user))
    else:
        return default_error_handler(msg, status_code=404)

# Define API endpoints for user authentication
@users_bp.route('login', methods=['POST'])
@input_validator(LoginInputs)
def login():
    data = request.get_json()
    identifier = data.get('email') or data.get('username')
    password = data.get('password')

    success, user, msg = current_app.user_manager.login(identifier, password)
    if success:
        # Login the user and create a session
        login_user(user, force=True)
        # bind a gpt instance to the user
        user.gpt = OpenAIAPI(load_gpt_config(current_app.config['ENV']))
        return jsonify({'success': True, 'current_user_id': current_user.id})
    else:
        return jsonify({'success': False, 'reason': msg}), 401
    
