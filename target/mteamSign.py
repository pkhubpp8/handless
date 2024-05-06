from selenium.webdriver.common.by import By
import re
import logging
import time
from ._BASE import signBase

logger = logging.getLogger('sign')

class signClass(signBase):
    def __init__(self, url = 'https://kp.m-team.cc', module_name: str = 'mteamSign'):
        self.indexUrl = url
        self.module_name = module_name
        super().__init__("m-team")
    def accessIndex(self):
        self.driver.get(self.indexUrl)  # 打开链接
        time.sleep(10)
    def sign(self):
        pass
    def validSign(self):
        if not re.search('M-Team.*Powered by', self.driver.title):
            self.sign_result = False
            self.sign_result_info = f"标题异常：{self.driver.title}"
            return False
        # todo: verify login status

        pass
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
