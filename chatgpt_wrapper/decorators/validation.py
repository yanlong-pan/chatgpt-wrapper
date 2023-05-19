import functools
from flask import request
from flask_inputs import Inputs
from flask_login import current_user

from chatgpt_wrapper.blueprints.error_handlers import unauthorised_request_handler, validation_error_handler

def input_validator(cls: Inputs):
    def outer(func):
        @functools.wraps(func)
        def wrapper(*args, **kargs):
            inputs = cls(request)
            if inputs.validate():
                return func(*args, **kargs)
            else:
                return validation_error_handler(inputs)
        return wrapper
    return outer

def current_user_restricted(user_id_field='user_id'):
    def outer(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            user_id = request.view_args.get(user_id_field)
            if current_user.id == user_id:
                return func(*args, **kwargs)
            else:
                return unauthorised_request_handler()
        return wrapper
    return outer
