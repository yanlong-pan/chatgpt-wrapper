import logging
from logging.handlers import TimedRotatingFileHandler
import os

def setup_logging():
    # 根据需要自定义日志格式
    log_format = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')

    log_path = "/logs"
    os.makedirs(log_path, exist_ok=True)
    # 创建一个定时循环文件处理器，每天创建一个新文件
    file_handler = TimedRotatingFileHandler(f'{log_path}/app.log', when='D', interval=1)
    file_handler.setFormatter(log_format)
    
    # 创建一个新的日志记录器
    logger = logging.getLogger("app")
    logger.setLevel(logging.DEBUG)  # 设置日志级别
    logger.addHandler(file_handler)

    return logger

logger = setup_logging()
