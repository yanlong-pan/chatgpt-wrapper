import argparse
import logging

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from chatgpt_wrapper.backends.openai.user import UserManager
from chatgpt_wrapper.core.logger import logger
from chatgpt_wrapper.database import create_db_and_tables, drop_db_and_tables
from chatgpt_wrapper.profiles.config_loader import load_flask_config
from chatgpt_wrapper.blueprints.bp_auths import auth_bp, auth_router
from chatgpt_wrapper.blueprints.bp_users import users_bp
from chatgpt_wrapper.blueprints.bp_characters import characters_bp
from chatgpt_wrapper.blueprints.bp_conversations import conversations_bp
from chatgpt_wrapper.utils.cache import cache
from chatgpt_wrapper.backends.openai.orm import db
from chatgpt_wrapper.utils.hooks import before_request_callback, teardown_request_callback
from fastapi import FastAPI
from chatgpt_wrapper.core.logger import console_logger


def create_application(name, timeout=60, proxy=None):
    app = FastAPI(title=name)
    
    app.include_router(auth_router)
    
    @app.on_event("startup")
    async def on_startup():
        # Not needed if you setup a migration system like Alembic
        await create_db_and_tables()
        console_logger.info('db created')
    
    @app.on_event("shutdown")
    async def on_startup():
        # Not needed if you setup a migration system like Alembic
        await drop_db_and_tables()
        console_logger.info('db dropped')
    # load_flask_config(app)
    
    # logger.debug('freshing the applicaiton')
    
    # db.init_app(app)
    # Migrate(app, db)
    
    # CORS(app, resources={r"/api/v1/*": {"origins": "*"}})
    
    # for bp in [auth_bp, users_bp, conversations_bp, characters_bp]:
    #     app.register_blueprint(bp)
    
    # app.before_request(before_request_callback)
    # app.teardown_request(teardown_request_callback)

    # app.logger.setLevel(logging.DEBUG)
    # app.logger.addHandler(logging.StreamHandler())
        
    # cache.init_app(app)
    
    return app


# if __name__ == "__main__":
#     # parser = argparse.ArgumentParser()
#     # parser.add_argument("--port", type=int, default=5000)
#     # args = parser.parse_args()
#     app = create_application("chatgpt")
#     # app.debug = True
#     # app.run(host="0.0.0.0", port=args.port, threaded=False, use_reloader=True)

# else:
    # app = create_application("chatgpt")
app = create_application("chatgpt")

