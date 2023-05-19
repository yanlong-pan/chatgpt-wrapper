from flask import Blueprint, g, jsonify, request
from flask_inputs import Inputs
from flask_inputs.validators import JsonSchema
from flask_login import login_required

from chatgpt_wrapper.blueprints.response_handlers import default_error_handler
from chatgpt_wrapper.blueprints.json_schemas import user_registration_schema
from chatgpt_wrapper.decorators.validation import input_validator, current_user_restricted

users_bp = Blueprint('users', __name__, url_prefix='/api/v1/users')

class RegisterInputs(Inputs):
    json = [JsonSchema(schema=user_registration_schema)]

@users_bp.route('/', methods=['POST'])
@input_validator(RegisterInputs)
def create_user():
    data = request.get_json()
    success, user, msg = g.gpt.um.register(email=data['email'],
                username=data['username'],
                password=data['password'])

    if success:
        return jsonify(user.to_json()), 201
    else:
        return default_error_handler(msg)

@users_bp.route('<int:user_id>', methods=["GET"])
@login_required
@current_user_restricted()
def get_user(user_id):
    success, user, msg = g.gpt.um.get_by_user_id(user_id)
    if success:
        return jsonify(user.to_json())
    else:
        return default_error_handler(msg, status_code=404)
    
