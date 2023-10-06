import logging


def initialLog(log_path):
    # 配置日志记录器
    logger = logging.getLogger('sign')
    logger.setLevel(logging.INFO)  # 设置日志级别为 INFO 或更高级别
    file_handler = logging.FileHandler(log_path)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger