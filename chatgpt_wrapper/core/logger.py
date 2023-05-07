import logging

from chatgpt_wrapper.core.config import Config
from chatgpt_wrapper.profiles.config_loader import load_gpt_config

class Logger():

    def __new__(cls, name, config=None):
        config = config or load_gpt_config()
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        log_console_handler = logging.StreamHandler()
        log_console_handler.setFormatter(logging.Formatter(config.get('log.console.format')))
        log_console_handler.setLevel(config.get('log.console.level'))
        logger.addHandler(log_console_handler)
        if config.get('debug.log.enabled'):
            log_file_handler = logging.FileHandler(config.get('debug.log.filepath'))
            log_file_handler.setFormatter(logging.Formatter(config.get('debug.log.format')))
            log_file_handler.setLevel(config.get('debug.log.level'))
            logger.addHandler(log_file_handler)
        return logger
