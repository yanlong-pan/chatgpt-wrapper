from flask import Blueprint, current_app, jsonify, request
from flask_inputs import Inputs
from flask_inputs.validators import JsonSchema
from flask_login import current_user, login_required, login_user

from chatgpt_wrapper.blueprints.error_handlers import default_error_handler, validation_error_handler

users_bp = Blueprint('users', __name__, url_prefix='/api/v1/users')

class RegisterInputs(Inputs):
    json = [JsonSchema(schema={
        'type': 'object',
        'properties': {
            'username': {'type': 'string'},
            'email': {'type': 'string', 'format': 'email'},
            'password': {
                'type': 'string',
                'minLength': 8,
                'pattern': '^(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9]+$',
            },
        },
        'required': ['username', 'email', 'password']
    })]

@users_bp.route('/', methods=['POST'])
def create_user():
    inputs = RegisterInputs(request)
    if inputs.validate():
        try:
            data = request.get_json()
            success, user, msg = current_app.gpt.user_manager.register(email=data['email'],
                        username=data['username'],
                        password=data['password'])
        except Exception:
            return default_error_handler('Fail to register') # Not expose the fact that the email is already in use
        else:
            if success:
                return jsonify(current_app.gpt.user_manager.orm.object_as_dict(user)), 201
            else:
                return default_error_handler(msg)
    else:
        return validation_error_handler(inputs)

@users_bp.route('<int:user_id>', methods=["GET"])
@login_required
def get_user(user_id):
    # Check if the requested user ID matches the authenticated user's ID
    if user_id != current_user.id:
        # If the user IDs do not match, return a 403 Forbidden response
        return jsonify({'error': 'Forbidden', 'current_user_id': current_user.id}), 403
    _, user, _ = current_app.gpt.user_manager.get_by_user_id(user_id)
    if user:
        return jsonify(current_app.gpt.user_manager.orm.object_as_dict(user))
    else:
        return jsonify({'message': 'User not found'}), 404

# Define API endpoints for user authentication
@users_bp.route('login', methods=['POST'])
def login():
    # Extract the user data from the request body
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Find the user with the given email address
    _, user, msg = current_app.gpt.user_manager.login(email, password)

    # Verify the user's password
    if user:
        # Login the user and create a session
        login_user(user, force=True)

        # Return a JSON response indicating success
        return jsonify({'success': True, 'current_user_id': current_user.id})
    else:
        # Return a JSON response indicating failure
        return jsonify({'success': False, 'reason': msg}), 401
    
