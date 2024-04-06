from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.by import By
import re
import logging
import time
from ._BASE import signBase

logger = logging.getLogger('sign')

class signClass(signBase):
    def __init__(self, driver, url = 'https://hdarea.club/index.php', module_name: str = 'hdareaSign'):
        self.indexUrl = url
        self.driver = driver
        self.module_name = module_name
        super().__init__("hdarea")
    def accessIndex(self):
        self.driver.execute_script("window.open('', '_blank');")  # 打开新标签页
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
        self.driver.get(self.indexUrl)  # 打开链接
    def msgCheck(self) -> bool:
        elements = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "条新短讯！点击查看")
        if len(elements) == 1:
            self.new_message = elements[0].text.strip()
            return True
        elif len(elements) == 0:
            return False
        else:
            self.new_message = "warning: " + elements[0].text.strip()
            logger.warning(f"找到elements长度{len(elements)}异常")
            return True
    def sign(self):
        elements = self.driver.find_elements(By.ID, "sign_in")
        for element in elements:
            if element.text == '[签到]':
                element.click()
                time.sleep(3)
                # driver.execute_script('alert("已连续签到46天，此次签到您获得了56魔力值奖励!")')
                try:
                    alert = self.driver.switch_to.alert
                    self.alert_text = alert.text
                    alert.accept()
                    self.driver.switch_to.default_content()
                except NoAlertPresentException:
                    logger.info("没有弹出alert")
                break
    def validSign(self):
        if not re.search('HDArea.*NexusPHP', self.driver.title):
            self.sign_result = False
            self.sign_result_info = f"标题异常：{self.driver.title}"
            return False
        if hasattr(self, 'alert_text') and self.alert_text is not None:
            match = re.search(r'已连续签到(\d+)天，此次签到您获得了(\d+)魔力值奖励!', self.alert_text)
            if match:
                self.sign_result = True
                self.sign_result_info = f"连续签到{match.group(1)}，获得魔力{match.group(2)}"
                return True
        elements = self.driver.find_elements(By.ID, "sign_in_done")
        for element in elements:
            if element.text == '[已签到]':
                self.sign_result = True
                self.sign_result_info = f"已经签到过了。"
                return True
        self.sign_result = False
        self.sign_result_info = f"未知异常。"
        return False
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
