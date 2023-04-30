import functools
from flask import request
from flask_inputs import Inputs

from chatgpt_wrapper.blueprints.error_handlers import validation_error_handler

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