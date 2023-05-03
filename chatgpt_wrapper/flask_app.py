import argparse
import logging
from pprint import pprint

from flask import Flask
from flask_login import LoginManager
from chatgpt_wrapper.backends.openai.api import OpenAIAPI
from chatgpt_wrapper.backends.openai.orm import Orm
from chatgpt_wrapper.backends.openai.user import UserManager
from chatgpt_wrapper.profiles.config_loader import load_flask_config, load_gpt_config
from chatgpt_wrapper.blueprints.bp_users import users_bp
from chatgpt_wrapper.blueprints.bp_conversations import conversations_bp

def create_application(name, env='dev', timeout=60, proxy=None):
    app = Flask(name)
    app.config['ENV'] = env
    load_flask_config(app)
    
    app.user_manager = UserManager(load_gpt_config(env))
    
    # gpt_config = load_gpt_config(app, env)
    # app.gpt = OpenAIAPI(gpt_config)
    
    app.register_blueprint(users_bp)
    app.register_blueprint(conversations_bp)

    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(logging.StreamHandler())
    
    login_manager = LoginManager()
    login_manager.init_app(app)
  
    @login_manager.user_loader
    def load_user(user_id):
        return app.user_manager.orm.get_user(user_id)
        # return app.gpt.user_manager.orm.get_user(user_id)
   
    # app.logger.debug(gpt_config.config_file)
    # app.logger.debug(pprint(gpt_config.config))
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
