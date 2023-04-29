import argparse
import logging
import time

from flask import Flask, jsonify, request
from flask_login import LoginManager, current_user, login_required, login_user
from chatgpt_wrapper.backends.openai.api import OpenAIAPI
from chatgpt_wrapper.core.config import Config

def create_application(name, config=None, timeout=60, proxy=None):
    config = config or Config()
    config.set('debug.log.enabled', True)
    gpt = OpenAIAPI(config)
    app = Flask(name)
    app.config['SECRET_KEY'] = 'b0f2657da6300cf6df8d65653f303556d54004a9e3e3cbf53e38426712c4bc4a'

    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(logging.StreamHandler())
    gpt.user_manager.orm.log.setLevel(logging.DEBUG)
    gpt.user_manager.orm.log.addHandler(logging.StreamHandler())
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
  
    # Define a custom user loader function
    @login_manager.user_loader
    def load_user(user_id):
        # return MyUser.query.get(int(user_id))
        return gpt.user_manager.orm.get_user(user_id)
    
    
    
    def _error_handler(message, status_code=500):
        return jsonify({"success": False, "error": str(message)}), status_code

    @app.route('/api/v1/users', methods=['POST'])
    def create_user():
        data = request.get_json()
        _, user, _ = gpt.user_manager.register(email=data['email'],
                    username=data['username'],
                    password=data['password'])
        
        return jsonify(gpt.user_manager.orm.object_as_dict(user)), 201

    @app.route('/api/v1/users/<int:user_id>', methods=["GET"])
    @login_required
    def get_user(user_id):
        # Check if the requested user ID matches the authenticated user's ID
        if user_id != current_user.id:
            # If the user IDs do not match, return a 403 Forbidden response
            return jsonify({'error': 'Forbidden', 'current_user_id': current_user.id}), 403
        _, user, _ = gpt.user_manager.get_by_user_id(user_id)
        if user:
            return jsonify(gpt.user_manager.orm.object_as_dict(user))
        else:
            return jsonify({'message': 'User not found'}), 404

    # Define API endpoints for user authentication
    @app.route('/api/v1/login', methods=['POST'])
    def login():
        # Extract the user data from the request body
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Find the user with the given email address
        _, user, msg = gpt.user_manager.login(email, password)

        # Verify the user's password
        if user:
            # Login the user and create a session
            login_user(user, force=True)

            # Return a JSON response indicating success
            return jsonify({'success': True, 'current_user_id': current_user.id})
        else:
            # Return a JSON response indicating failure
            return jsonify({'success': False, 'reason': msg}), 401
        
    @app.route("/conversations", methods=["POST"])
    def ask():
        """
        Ask a question.

        Path:
            POST /conversations

        Request Body:
            JSON:
                {
                    "question": String,
                    "system_message": String
                }

        Returns:
            STRING:
                Some response.
        """
        
        start_time = time.time()
        data = request.get_json()
        # prompt = request.get_data().decode("utf-8")
        success, result, user_message = gpt.ask(
            prompt=data['question'],
            model_customizations={
                "system_message": data["system_message"]
            }
        )
        end_time = time.time()
        execution_time = end_time - start_time
        return jsonify({"execution_time": execution_time, "result": result})

    @app.route("/conversations/new", methods=["POST"])
    def new_conversation():
        """
        Start a new conversation.

        Path:
            POST /conversations/new

        Returns:
            JSON:
                {
                    "success": true,
                }

            JSON:
                {
                    "success": false,
                    "error": "Failed to start new conversation"
                }
        """
        gpt.new_conversation()
        return jsonify({"success": True, "parent_message_id": gpt.parent_message_id})

    @app.route("/conversations/<string:conversation_id>", methods=["DELETE"])
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
        success, result, user_message = gpt.delete_conversation(conversation_id)
        if success:
            return user_message
        else:
            return _error_handler(user_message)

    @app.route("/conversations/<string:conversation_id>/set-title", methods=["PATCH"])
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
        success, conversation, user_message = gpt.set_title(title, conversation_id)
        if success:
            return jsonify(gpt.conversation.orm.object_as_dict(conversation))
        else:
            return _error_handler("Failed to set title")

    @app.route("/history/<int:user_id>", methods=["GET"])
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
        success, result, user_message = gpt.get_history(limit=limit, offset=offset, user_id=user_id)
        if result:
            return jsonify(result)
        else:
            return _error_handler("Failed to get history")

    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    app = create_application("chatgpt")
    app.debug = True
    app.run(host="0.0.0.0", port=args.port, threaded=False, use_reloader=True)

else:
    app = create_application("chatgpt")
