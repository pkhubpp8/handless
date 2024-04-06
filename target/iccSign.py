from selenium.webdriver.common.by import By
import re
import logging
import time
from ._BASE import signBase

logger = logging.getLogger('sign')

class signClass(signBase):
    def __init__(self, driver, url = 'https://www.icc2022.com/index.php', module_name: str = 'iccSign'):
        self.indexUrl = url
        self.driver = driver
        self.module_name = module_name
        super().__init__("icc2022")
    def accessIndex(self):
        self.driver.execute_script("window.open('', '_blank');")  # 打开新标签页
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
        self.driver.get(self.indexUrl)  # 打开链接
    def msgCheck(self) -> bool:
        new_msg_elements = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "条新短讯！点击查看")
        if len(new_msg_elements) == 1:
            self.new_message = new_msg_elements[0].text.strip()
            return True
        new_important_elements = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "条未读的重要消息")
        if len(new_important_elements) == 1:
            self.new_message = new_important_elements[0].text.strip()
            return True

        if len(new_msg_elements) == 0 and len(new_important_elements) == 0:
            return False
        else:
            self.new_message = "warning: new msg size: " + str(len(new_msg_elements))
            self.new_message = self.new_message + ", new important msg size: " + str(len(new_important_elements))
            logger.warning(f"找到elements长度{len(new_msg_elements)}, {len(new_important_elements)}异常")
            return True
    def sign(self):
        if not re.search('ICC.*NexusPHP', self.driver.title):
            logger.info(f"标题异常：{self.driver.title}。尝试切换备用页")
            self.driver.get("https://fangwen2.icc2022.top/index.php")
            if not re.search('ICC.*NexusPHP', self.driver.title):
                self.sign_result = False
                self.sign_result_info = f"标题异常2：{self.driver.title}"
                return
        elements = self.driver.find_elements(By.CLASS_NAME, "faqlink")
        for element in elements:
            if element.text == '[签到得魔力]':
                element.click()
                break
    def validSign(self):
        if not re.search('ICC.*NexusPHP', self.driver.title):
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
            if element.text == '[签到得魔力]':
                self.sign_result = False
                self.sign_result_info = "还未签到。"
                return False
            match = re.search(r'签到已得(\d+), 补签卡: \d+', element.text)
            if match:
                self.sign_result = True
                self.sign_result_info = f"已经签到过了。签到已得{match.group(1)}"
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
