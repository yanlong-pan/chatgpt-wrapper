# app/auth/__init__.py
from flask import Blueprint, current_app, jsonify, request
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_inputs import Inputs
from flask_inputs.validators import JsonSchema
from chatgpt_wrapper.backends.openai.api import OpenAIAPI

from chatgpt_wrapper.blueprints.json_schemas import user_login_schema
from chatgpt_wrapper.decorators.validation import input_validator
from chatgpt_wrapper.profiles.config_loader import load_gpt_config

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')
login_manager = LoginManager()

class LoginInputs(Inputs):
    json = [JsonSchema(schema=user_login_schema)]

@auth_bp.record_once
def on_load(state):
    global login_manager
    login_manager.init_app(state.app)

@login_manager.user_loader
def load_user(user_id):
    return current_app.user_manager.orm.get_user(user_id)

@login_manager.unauthorized_handler
def unauthorized_handler():
    return jsonify({'error': 'Unauthorized access'}), 401

@auth_bp.route('/login', methods=['POST'])
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
        user.gpt = OpenAIAPI(load_gpt_config(current_app.config['ENV']), default_user_id=user.id)
        return jsonify({'success': True, 'current_user_id': current_user.id})
    else:
        return jsonify({'success': False, 'reason': msg}), 401

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'You have been logged out successfully.'}), 200
