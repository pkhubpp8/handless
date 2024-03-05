from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoAlertPresentException
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
        elements = self.driver.find_elements(By.CLASS_NAME, "ab-item")
        for element in elements:
            if element.text == '打卡签到':
                element.click()
    def valid_access(self):
        if not re.search('游戏怀旧灌水', self.driver.title):
            self.access_result = False
            self.access_result_info = f"标题异常：{self.driver.title}"
            return False
        elements = self.driver.find_elements(By.CLASS_NAME, "ab-item")
        for element in elements:
            name = element.find_elements(By.CLASS_NAME, "display-name")
            if name:
                for n in name:
                    if n.text:
                        self.access_result = True
                        self.access_result_info = f""
                        return
        return True
    def sign(self):
        elements = self.driver.find_elements(By.CLASS_NAME, "mycred-points-link")
        for element in elements:
            if element.text == '每日魔晶盲盒[打卡]':
                element.click()
                return
    def validSign(self):
        try:
            alert = self.driver.switch_to.alert
            self.alert_text = alert.text
            alert.accept()
            self.driver.switch_to.default_content()
        except NoAlertPresentException:
            logger.info("没有弹出alert")
            self.sign_result = True
            self.sign_result_info = f"可能已经签到过了"
            return True
        if hasattr(self, 'alert_text') and self.alert_text is not None:
            match = re.search('抽到魔晶 (\d+)，明日再来', self.alert_text)
            if match:
                self.sign_result = True
                self.sign_result_info = f"获得魔晶{match.group(1)}"
                return True
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
            "need_resign": self.need_resign,
            "new_message": self.new_message,
            "extra_info": self.extra_info
        }
        return self.result
    def exit(self):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
