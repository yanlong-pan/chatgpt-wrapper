from flask import g
from flask_login import current_user
from chatgpt_wrapper.backends.openai.api import OpenAIAPI

from chatgpt_wrapper.profiles.config_loader import load_gpt_config

def before_request_callback():
    if current_user.is_authenticated and not hasattr(g, 'gpt'):
        g.gpt = OpenAIAPI(load_gpt_config(), default_user_id=current_user.id)

def teardown_request_callback(exception=None):
    for attr in dir(g):
        if attr == 'gpt':
            setattr(g, attr, None)
