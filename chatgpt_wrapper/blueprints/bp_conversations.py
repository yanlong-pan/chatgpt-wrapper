
import time
from flask import Blueprint, jsonify, request
from flask_login import current_user
from flask_inputs import Inputs
from flask_inputs.validators import JsonSchema
from chatgpt_wrapper.blueprints.json_schemas import chat_schema



from chatgpt_wrapper.blueprints.error_handlers import default_error_handler
from chatgpt_wrapper.decorators.validation import input_validator

class ChatInputs(Inputs):
    json = [JsonSchema(schema=chat_schema)]

conversations_bp = Blueprint('conversations', __name__, url_prefix='/api/v1/conversations')

@conversations_bp.route("/", methods=["POST"])
@input_validator(ChatInputs)
def ask():
    """
    Have a chat.

    Path:
        POST /conversations

    Request Body:
        JSON:
            {
                "user_input": String,
                "system_message": String
            }

    Returns:
        STRING:
            Some response.
    """
    
    start_time = time.time()
    data = request.get_json()
    if data.get('system_message'):
        model_customizations = {
            "system_message": data["system_message"]
        }
    else:
        model_customizations = {}
    success, result, user_message = current_user.gpt.ask(
        prompt=data['user_input'],
        model_customizations=model_customizations
    )
    end_time = time.time()
    execution_time = end_time - start_time
    return jsonify({"execution_time": execution_time, "result": result})

@conversations_bp.route("/<string:conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id):
    """
    Delete a conversation.

    Path:
        DELETE /conversations/:conversation_id

    Parameters:
        conversation_id (str): The ID of the conversation to delete.

    Returns:
        JSON:
            {
                "success": true,
            }

        JSON:
            {
                "success": false,
                "error": "Failed to delete conversation"
            }
    """
    success, result, user_message = current_user.gpt.delete_conversation(conversation_id)
    if success:
        return user_message
    else:
        return default_error_handler(user_message)

@conversations_bp.route("/<string:conversation_id>/set-title", methods=["PATCH"])
def set_title(conversation_id):
    """
    Set the title of a conversation.

    Path:
        PATCH /conversations/:conversation_id/set-title

    Parameters:
        conversation_id (str): The ID of the conversation to set the title for.

    Request Body:
        JSON:
            {
                "title": "New Title"
            }

    Returns:
        JSON:
            {
                "success": true,
            }

        JSON:
            {
                "success": false,
                "error": "Failed to set title"
            }
    """
    json = request.get_json()
    title = json["title"]
    success, conversation, user_message = current_user.gpt.set_title(title, conversation_id)
    if success:
        return jsonify(current_user.gpt.conversation.orm.object_as_dict(conversation))
    else:
        return default_error_handler("Failed to set title")

@conversations_bp.route("/history/<int:user_id>", methods=["GET"])
def get_history(user_id):
    """
    Retrieve conversation history for a user.

    Path:
        GET /history/:user_id

    Query Parameters:
        limit (int, optional): The maximum number of conversations to return (default is 20).
        offset (int, optional): The number of conversations to skip before starting to return results (default is 0).

    Returns:
        JSON:
            {
                ":conversation_id": {
                    "id": "abc123",
                    "title": "Conversation Title",
                    ...
                },
                ...
            }

        JSON:
            {
                "error": "Failed to get history"
            }
    """
    limit = request.args.get("limit", 20)
    offset = request.args.get("offset", 0)
    success, result, user_message = current_user.gpt.get_history(limit=limit, offset=offset, user_id=user_id)
    if result:
        return jsonify(result)
    else:
        return default_error_handler("Failed to get history")
