from selenium.webdriver.common.by import By
import re
import logging
from ._BASE import signBase

logger = logging.getLogger('sign')

class signClass(signBase):
    def __init__(self, driver, url = 'https://kp.m-team.cc/index.php', module_name: str = 'mteamSign'):
        self.indexUrl = url
        self.driver = driver
        self.module_name = module_name
        super().__init__("m-team")
    def accessIndex(self):
        self.driver.execute_script("window.open('', '_blank');")  # 打开新标签页
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
        self.driver.get(self.indexUrl)  # 打开链接
    def sign(self):
        pass
    def validSign(self):
        if not re.search('M-Team.*NexusPHP', self.driver.title):
            logger.info(f"标题异常：{self.driver.title}")
            return False
        return True
    def exit(self):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
        self.driver = None