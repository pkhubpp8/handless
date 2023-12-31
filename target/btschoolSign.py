from selenium.webdriver.common.by import By
import re
import logging
import time
from ._BASE import signBase

logger = logging.getLogger('sign')

class signClass(signBase):
    def __init__(self, driver, url = 'https://pt.btschool.club/index.php', module_name: str = 'btschoolSign'):
        self.indexUrl = url
        self.driver = driver
        self.module_name = module_name
        super().__init__("btschool")
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
            return False
    def sign(self):
        elements = self.driver.find_elements(By.LINK_TEXT, "每日签到")
        for element in elements:
            if 'addbonus' in element.get_attribute("href"):
                element.click()
                break
    def validSign(self):
        # 'BTSCHOOL :: 首页 比特校园PT小乐园 - Powered by NexusPHP'
        if not re.search('BTSCHOOL.*NexusPHP', self.driver.title):
            self.sign_result = False
            self.sign_result_info = f"标题异常：{self.driver.title}"
            return False
        elements = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "今天签到")
        for element in elements:
            match = re.search('今天签到您获得(\d+)点魔力值', element.text)
            if match:
                self.sign_result = True
                self.sign_result_info = f"今天签到您获得{match.group(1)}点魔力值"
                return True
        elements = self.driver.find_elements(By.LINK_TEXT, "每日签到")
        if not elements:
            self.sign_result = True
            self.sign_result_info = f"已经签到过了。"
            return True
        self.sign_result_info = f"未知异常。"
        self.sign_result = False
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
