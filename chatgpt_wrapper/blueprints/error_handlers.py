from flask import jsonify
from flask_inputs import Inputs


def default_error_handler(message, status_code=500):
    return jsonify({"success": False, "error": str(message)}), status_code

def validation_error_handler(inputs: Inputs, status_code=422):
    return jsonify({'message': 'invalid input data', 'errors': inputs.errors}), status_code