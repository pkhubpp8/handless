import sqlite3
import os
import logging

logger = logging.getLogger('default')

def setLogger(logger_):
    global logger
    logger = logger_

class Sql:
    def __init__(self, profile_file_path = ""):
        if profile_file_path:
            firefox_profile_path = profile_file_path
        else:
            # 获取当前用户的应用数据文件夹路径
            appdata_folder = os.getenv('APPDATA')

            # 构建Firefox配置文件夹路径
            firefox_profile_folder = os.path.join(appdata_folder, 'Mozilla', 'Firefox', 'Profiles')

            # 列出Firefox配置文件夹中的所有子文件夹
            profile_folders = os.listdir(firefox_profile_folder)

            # 假设使用第一个配置文件夹
            if profile_folders:
                first_profile_folder = profile_folders[0]
                firefox_profile_path = os.path.join(firefox_profile_folder, first_profile_folder)
                logger.info(f"Firefox配置文件路径: {firefox_profile_path}")
            else:
                logger.info("找不到Firefox配置文件路径")

        cookie_db_path = os.path.join(firefox_profile_path, 'cookies.sqlite')
        self.conn = sqlite3.connect(cookie_db_path)
        self.cursor = self.conn.cursor()

    def getCookieByUrlAndName(self, url, name):
        self.cursor.execute(f"SELECT value FROM moz_cookies WHERE host='{url}' AND name='{name}'")
        result = self.cursor.fetchone()
        r = result[0] if result is not None else ''
        return r

    def __del__(self):
        # 关闭数据库连接
        self.cursor.close()
        self.conn.close()