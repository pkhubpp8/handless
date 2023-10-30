import logging
import datetime

class myLogger:
    def __init__(self, appName, log_path = "", date = False):
        # 配置日志记录器
        if date:
            current_time = datetime.datetime.now()
            log_path = log_path + f"_{current_time.strftime('%Y%m%d')}.log"
        else:
            log_path = log_path + ".log"
        self.logger = logging.getLogger(appName)
        self.logger.setLevel(logging.INFO)  # 设置日志级别为 INFO 或更高级别
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def getLogger(self):
        return self.logger
