from selenium.webdriver.common.by import By
import re
import logging
import time
from datetime import datetime
from bs4 import BeautifulSoup
from ._BASE import signBase

logger = logging.getLogger('sign')

class signClass(signBase):
    def __init__(self, driver, url = 'https://www.yxhjgs.com/', module_name: str = 'hjgsSign'):
        self.indexUrl = url
        self.driver = driver
        self.module_name = module_name
        super().__init__("yxhjgs")
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
            self.sign_result = False
            self.sign_result_info = f"标题异常：{self.driver.title}"
            return False
        self.sign_result = True
        self.sign_result_info = f""
        return True
    def collect_info(self) -> dict:
        self.result = {
            "module_name": self.module_name,
            "site_name": self.site_name,
            "site_url": self.indexUrl,
            "sign_result": self.sign_result,
            "sign_result_info": self.sign_result_info,
            "date_and_time": int(time.time()),
            "need_resign": self.need_resign,
            "new_message": self.new_message,
            "extra_info": self.extra_info
        }
        return self.result
    def exit(self):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
