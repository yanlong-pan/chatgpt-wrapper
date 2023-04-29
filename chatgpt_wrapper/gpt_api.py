import argparse
import logging

from flask import Flask
from flask_login import LoginManager
from chatgpt_wrapper.backends.openai.api import OpenAIAPI
from chatgpt_wrapper.core.config import Config
from chatgpt_wrapper.blueprints.bp_users import users_bp
from chatgpt_wrapper.blueprints.bp_conversations import conversations_bp

def create_application(name, config=None, timeout=60, proxy=None):
    config = config or Config()
    config.set('debug.log.enabled', True)
    gpt = OpenAIAPI(config)
    app = Flask(name)
    app.gpt = gpt
    app.register_blueprint(users_bp)
    app.register_blueprint(conversations_bp)
    app.config['SECRET_KEY'] = 'b0f2657da6300cf6df8d65653f303556d54004a9e3e3cbf53e38426712c4bc4a'

    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(logging.StreamHandler())
    # gpt.user_manager.orm.log.setLevel(logging.DEBUG)
    # gpt.user_manager.orm.log.addHandler(logging.StreamHandler())
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
  
    # Define a custom user loader function
    @login_manager.user_loader
    def load_user(user_id):
        # return Orm(config).get_user(user_id)
        return gpt.user_manager.orm.get_user(user_id)
   
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
