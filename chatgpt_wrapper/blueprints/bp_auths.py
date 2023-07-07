from flask import Blueprint, g, request
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_inputs import Inputs
from flask_inputs.validators import JsonSchema
from chatgpt_wrapper.backends.openai.api import OpenAIAPI
# from chatgpt_wrapper.backends.openai.orm import User

from chatgpt_wrapper.blueprints.json_schemas import user_login_schema
from chatgpt_wrapper.blueprints.response_handlers import default_error_handler, success_json_response
from chatgpt_wrapper.decorators.validation import input_validator
from fastapi import APIRouter
from chatgpt_wrapper.model import User
from chatgpt_wrapper.profiles.config_loader import load_gpt_config

from chatgpt_wrapper.schema.forms.auth import LoginForm

auth_router = APIRouter(prefix='/api/v1/auth')

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
    return User.get_user(user_id)

@login_manager.unauthorized_handler
def unauthorized_handler():
    return default_error_handler('Unauthorized access', 401)

@auth_router.post('/login')
# @input_validator(LoginInputs)
async def login(form: LoginForm):
    user = await User.get_user_by_name_or_email(
        username=form.email,
        email=form.email,
    )
    return user.to_json()
    # data = request.get_json()
    # identifier = data.get('email') or data.get('username')
    # password = data.get('password')

    # success, user, msg = g.gpt.um.login(form.email, form.password)
    # if success and login_user(user, force=True):
    #     return success_json_response({'current_user_id': current_user.id})
    # else:
    #     return default_error_handler(msg, 401)

@auth_router.post('/logout')
async def logout(form: LoginForm):
    user: User = await User.get_user_by_name_or_email(
        username=form.email,
        email=form.email,
    )
    
    await user.soft_delete()
    return user.is_deleted
    # logout_user()
    # return success_json_response(None, message='You have been logged out successfully.')
