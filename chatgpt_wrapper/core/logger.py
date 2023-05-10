import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logging():
    # 根据需要自定义日志格式
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 创建一个定时循环文件处理器，每天创建一个新文件
    file_handler = TimedRotatingFileHandler("/logs/app", when='D', interval=1)
    file_handler.setFormatter(log_format)
    
    # 创建一个新的日志记录器
    logger = logging.getLogger("app")
    logger.setLevel(logging.DEBUG)  # 设置日志级别
    logger.addHandler(file_handler)

    return logger

logger = setup_logging()
