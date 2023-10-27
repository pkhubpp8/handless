from selenium.webdriver.common.by import By
import re
import logging
import time
from ._BASE import signBase

logger = logging.getLogger('sign')

class signClass(signBase):
    def __init__(self, driver, url = 'https://www.52pojie.cn/', module_name: str = '52pojieSign'):
        self.indexUrl = url
        self.driver = driver
        self.module_name = module_name
        super().__init__("52pojie")
    def accessIndex(self):
        self.driver.execute_script("window.open('', '_blank');")  # 打开新标签页
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
        self.driver.get(self.indexUrl)  # 打开链接
    def valid_access(self):
        if not re.search('吾爱破解', self.driver.title):
            self.access_result = False
            self.access_result_info = f"标题异常：{self.driver.title}"
            return False
        elements = self.element = self.driver.find_elements(By.XPATH, '//strong[contains(@class, "vwmy qq")]')
        for element in elements:
            if element.text:
                self.access_result = True
                self.access_result_info = ""
                return True
        self.access_result = False
        self.access_result_info = f"未登录"
        return False
    def sign(self):
        # <a href="home.php?mod=task&amp;do=apply&amp;id=2&amp;referer=%2F">
        # <img src="https://static.52pojie.cn/static/image/common/qds.png" class="qq_bind" align="absmiddle" alt="">
        # </a>
        sign_src = '/static/image/common/qds.png'
        elements = self.driver.find_elements(By.CLASS_NAME, 'qq_bind')
        for element in elements:
            if isinstance(element.get_attribute('src'), str):
                if sign_src in element.get_attribute('src'):
                    element.click()
                    time.sleep(5)
                    return
    def validSign(self):
        if not re.search('吾爱破解', self.driver.title):
            self.sign_result = False
            self.sign_result_info = f"标题异常：{self.driver.title}"
            return False
        # https://static.52pojie.cn/static/image/common/qds.png
        # https://static.52pojie.cn/static/image/common/wbs.png
        # match = re.search(r'(https?://)?([^/]+\.)?([^/]+\.[^/]+)/.*', self.indexUrl)
        sign_src = '/static/image/common/qds.png'
        sign_done_src = '/static/image/common/wbs.png'
        elements = self.driver.find_elements(By.CLASS_NAME, 'qq_bind')
        for element in elements:
            if isinstance(element.get_attribute('src'), str):
                if sign_src in element.get_attribute('src'):
                    self.sign_result = False
                    self.sign_result_info = f"还未签到"
                    return True
                if sign_done_src in element.get_attribute('src'):
                    self.sign_result = False
                    self.sign_result_info = f"还未签到"
                    return False
        self.sign_result = False
        self.sign_result_info = f"未知异常。"
        return False
    def collect_info(self) -> dict:
        self.result = {
            "module_name": self.module_name,
            "site_name": self.site_name,
            "site_url": self.indexUrl,
            "access_result": self.access_result,
            "access_result_info": self.access_result_info,
            "sign_result": self.sign_result,
            "sign_result_info": self.sign_result_info,
            "date_and_time": int(time.time()),
            "need_resign": False,
            "new_message": self.new_message,
            "extra_info": self.extra_info
        }
        return self.result
    def exit(self):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
        self.driver = None