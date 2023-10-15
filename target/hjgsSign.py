from selenium.webdriver.common.by import By
import re
import logging
import time
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger('sign')

class signClass:
    def __init__(self, driver, url = 'https://www.yxhjgs.com/', module_name: str = 'hjgsSign'):
        self.indexUrl = url
        self.driver = driver
        self.module_name = module_name
    def accessIndex(self):
        self.driver.execute_script("window.open('', '_blank');")  # 打开新标签页
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
        self.driver.get(self.indexUrl)  # 打开链接
        time.sleep(3)
    def sign(self):
        # 没有显式签到方法
        # 仅访问主页似乎没有增加魔力
        pass
    def validSign(self):
        if not re.search('游戏怀旧灌水', self.driver.title):
            logger.info(f"标题异常：{self.driver.title}")
            return False
        return True
    def exit(self):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
        self.driver = None