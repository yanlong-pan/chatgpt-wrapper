from flask import g
from chatgpt_wrapper.backends.openai.api import OpenAIAPI

from chatgpt_wrapper.profiles.config_loader import load_gpt_config

def before_request_callback():
    g.gpt = OpenAIAPI(load_gpt_config())

def teardown_request_callback(exception=None):
    setattr(g, 'gpt', None)
