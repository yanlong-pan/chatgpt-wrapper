from flask import jsonify
from flask_inputs import Inputs


def default_error_handler(message, status_code=500):
    return jsonify({'success': False, 'message': str(message)}), status_code

def validation_error_handler(inputs: Inputs, status_code=422):
    return jsonify({'success': False, 'message': 'invalid input data', 'errors': inputs.errors}), status_code

def unauthorised_request_handler(message='Unauthorized operation'):
    return default_error_handler(message, 403)