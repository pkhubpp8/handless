import logging


def initialLog():
    # 配置日志记录器
    logger = logging.getLogger('sign')
    logger.setLevel(logging.INFO)  # 设置日志级别为 INFO 或更高级别
    file_handler = logging.FileHandler('sign.log')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger