from selenium.webdriver.common.by import By
import re
import logging
import time
from ._BASE import signBase

logger = logging.getLogger('sign')

class signClass(signBase):
    def __init__(self, url = 'https://www.okpt.net/index.php', module_name: str = 'okptSign'):
        self.indexUrl = url
        self.module_name = module_name
        super().__init__("okpt")
    def accessIndex(self):
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
        elements = self.driver.find_elements(By.CLASS_NAME, "faqlink")
        for element in elements:
            if element.text == '[签到得魔力]' and 'attendance.php' in element.get_attribute("href"):
                element.click()
                break
    def validSign(self):
        if not re.search('OKPT.*NexusPHP', self.driver.title):
            self.sign_result = False
            self.sign_result_info = f"标题异常：{self.driver.title}"
            return False
        elements = self.driver.find_elements(By.CLASS_NAME, "text")
        for element in elements:
            match = re.search(r'这是[你您]的第\s+(\d+)\s+次签到.*已连续签到\s+(\d+)\s+天.*本次签到获得\s+(\d+)\s+个魔力值', element.text)
            if match:
                self.sign_result = True
                self.sign_result_info = f"第{match.group(1)}次签到，连续签到{match.group(2)}，获得魔力{match.group(3)}"
                return True
        elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[class=""]')
        for element in elements:
            match = re.search(r'\[签到已得(\d+), 补签卡:\s*\d+\]', element.text)
            if match:
                self.sign_result = True
                self.sign_result_info = f"已经签到过了。签到已得{match.group(1)}"
                return True
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
