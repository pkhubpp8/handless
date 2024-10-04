from selenium.webdriver.common.by import By
import re
import logging
import time
from ._BASE import signBase

logger = logging.getLogger('sign')

class signClass(signBase):
    def __init__(self, url = 'https://pt.upxin.net/index.php', module_name: str = 'upxinSign'):
        self.indexUrl = url
        self.module_name = module_name
        super().__init__("upxin")
    def accessIndex(self):
        self.driver.get(self.indexUrl)  # 打开链接
    def sign(self):
        elements = self.driver.find_elements(By.ID, "qiandao")
        for element in elements:
            if element.text == '[签到]':
                element.click()
                time.sleep(3)
                break
    def validSign(self):
        if not re.search('HDU.*Torrents', self.driver.title):
            self.sign_result = False
            self.sign_result_info = f"标题异常：{self.driver.title}"
            return False
        elements = self.driver.find_elements(By.ID, "yiqiandao")
        for element in elements:
            if element.text == '[已签到]':
                self.sign_result = True
                self.sign_result_info = f"已经签到过了。"
                return True
            if element.text == '[签到]':
                self.sign_result = False
                self.sign_result_info = f"未签到"
                return False
        self.sign_result = False
        self.sign_result_info = f"未知异常。"
        return False
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
