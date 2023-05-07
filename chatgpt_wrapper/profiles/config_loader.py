import os
from flask import Flask

from chatgpt_wrapper.core.config import Config

dir_path = os.path.dirname(os.path.realpath(__file__))

def load_flask_config(app: Flask) -> None:
    for env in ['test', 'dev', 'prod']:
        file_path = f'{dir_path}/{env}/flask_config.py'
        if env in os.environ.get('FLASK_APP_ENV', 'dev').lower() and os.path.exists(file_path):
            app.config.from_pyfile(file_path)
            break
    else:
        raise ValueError('Invalid config name')
    
def load_gpt_config(environment: str = None) -> Config:
    environment = environment or os.environ.get('FLASK_APP_ENV', 'dev')
    for env in ['test', 'dev', 'prod']:
        config_dir = dir_path.rstrip("profiles")
        filename = 'gpt_config.yaml'
        if env in environment.lower():
            config = Config(config_dir=config_dir, profile=env)
            if os.path.exists(os.path.join(config.config_profile_dir, filename)):
                config.load_from_file(filename)
                return config
            else:
                raise FileNotFoundError()
    else:
        raise ValueError('Invalid config name')