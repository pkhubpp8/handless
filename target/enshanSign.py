from selenium.webdriver.common.by import By
import re
import logging
import time
from ._BASE import signBase

logger = logging.getLogger('sign')

class signClass(signBase):
    def __init__(self, url = 'https://www.right.com.cn/forum/', module_name: str = 'enshanSign'):
        self.indexUrl = url
        self.module_name = module_name
        super().__init__("enshan")
    def accessIndex(self):
        self.driver.get(self.indexUrl)  # 打开链接
        time.sleep(6)
    def valid_access(self):
        return True
        self.access_result = False
        self.access_result_info = f"未登录"
        return False
    def sign(self):
        pass
    def validSign(self):
        if not re.search('恩山无线论坛', self.driver.title):
            self.sign_result = False
            self.sign_result_info = f"标题异常：{self.driver.title}"
            return False
        self.sign_result = True
        self.sign_result_info = f""
        return True
    def collect_info(self) -> dict:
        t = time.time()
        self.result = {
            "module_name": self.module_name,
            "site_name": self.site_name,
            "site_url": self.indexUrl,
            "sign_result": self.sign_result,
            "sign_result_info": self.sign_result_info,
            "timestamp": int(t),
            "timestring": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t)),
            "new_message": self.new_message,
            "extra_info": self.extra_info
        }
        return self.result
