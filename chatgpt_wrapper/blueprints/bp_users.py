from flask import Blueprint, current_app, g, jsonify, request
from flask_inputs import Inputs
from flask_inputs.validators import JsonSchema
from flask_login import current_user, login_required

from chatgpt_wrapper.blueprints.error_handlers import default_error_handler
from chatgpt_wrapper.blueprints.json_schemas import user_registration_schema
from chatgpt_wrapper.decorators.validation import input_validator

users_bp = Blueprint('users', __name__, url_prefix='/api/v1/users')

class RegisterInputs(Inputs):
    json = [JsonSchema(schema=user_registration_schema)]

@users_bp.route('/', methods=['POST'])
@input_validator(RegisterInputs)
def create_user():
    data = request.get_json()
    success, user, msg = current_app.user_manager.register(email=data['email'],
                username=data['username'],
                password=data['password'])

    if success:
        return jsonify(user.to_json()), 201
    else:
        return default_error_handler(msg)

@users_bp.route('<int:user_id>', methods=["GET"])
@login_required
def get_user(user_id):
    # Check if the requested user ID matches the authenticated user's ID
    if user_id != current_user.id:
        return jsonify({'error': 'Forbidden', 'current_user_id': current_user.id}), 403
    success, user, msg = g.gpt.user_manager.get_by_user_id(user_id)
    # success, user, msg = current_app.user_manager.get_by_user_id(user_id)
    if success:
        return jsonify(user.to_json())
    else:
        return default_error_handler(msg, status_code=404)
    
