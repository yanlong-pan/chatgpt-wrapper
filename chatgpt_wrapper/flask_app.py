import argparse
import logging

from flask import Flask
from chatgpt_wrapper.backends.openai.user import UserManager
from chatgpt_wrapper.profiles.config_loader import load_flask_config, load_gpt_config
from chatgpt_wrapper.blueprints.bp_users import users_bp
from chatgpt_wrapper.blueprints.bp_conversations import conversations_bp
from chatgpt_wrapper.blueprints.bp_auths import auth_bp
from chatgpt_wrapper.blueprints.bp_characters import characters_bp
from chatgpt_wrapper.utils.cache import cache

def create_application(name, env='dev', timeout=60, proxy=None):
    app = Flask(name)
    app.config['ENV'] = env
    load_flask_config(app)
    
    app.user_manager = UserManager(load_gpt_config(env))

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(conversations_bp)
    app.register_blueprint(characters_bp)

    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(logging.StreamHandler())
    
    cache.init_app(app)
    
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
