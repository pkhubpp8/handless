import logging


class myLogger:
    def __init__(self, appName, log_path = ""):
        # 配置日志记录器
        self.logger = logging.getLogger(appName) #'sign')
        self.logger.setLevel(logging.INFO)  # 设置日志级别为 INFO 或更高级别
        file_handler = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def getLogger(self):
        return self.logger
