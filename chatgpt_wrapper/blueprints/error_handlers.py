from flask import jsonify


def default_error_handler(message, status_code=500):
    return jsonify({"success": False, "error": str(message)}), status_code