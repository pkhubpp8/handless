from selenium.webdriver.common.by import By
import re
import logging
import time
from ._BASE import signBase

logger = logging.getLogger('sign')

class signClass(signBase):
    def __init__(self, driver, url = 'https://www.manhuabudangbbs.com/', module_name: str = 'bdbbsSign'):
        self.indexUrl = url
        self.driver = driver
        self.module_name = module_name
        super().__init__("manhuabudangbbs")
    def accessIndex(self):
        self.driver.execute_script("window.open('', '_blank');")  # 打开新标签页
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
        self.driver.get(self.indexUrl)  # 打开链接
        time.sleep(1)
        elements = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "每日打卡")
        for element in elements:
            if element.get_attribute("href") == (self.indexUrl + 'u.php'):
                element.click()
                time.sleep(1)
                break
    def sign(self):
        elements = self.driver.find_elements(By.CSS_SELECTOR, "div.card.card_old.fr")
        if len(elements) > 0:
            for element in elements:
                match = re.search('连续(\d+)天打卡', element.text)
                if match:
                    return
        elements = self.driver.find_elements(By.CSS_SELECTOR, "div.card.fr")
        for element in elements:
            match = re.search('每日打卡|\d+天未打卡', element.text)
            if match:
                element.click()
                time.sleep(1)
                self.driver.refresh()
                time.sleep(1)
                return
    def validSign(self):
        if not re.search('Powered by phpwind', self.driver.title):
            self.sign_result_info = f"标题异常：{self.driver.title}"
            return False
        # 未打卡            <div class="card fr" id="punch" onclick="if (!window.__cfRLUnblockHandlers) return false; punchJob(86);"><span>每日打卡</span></div>
        # 第一天打卡(刷新)   <div class="card fr card_old"><span>连续1天打卡</span></div>
        #                   <div class="card fr card_old"><span>连续2天打卡</span></div>
        # 第二天打卡(未刷新) <div class="card card_old fr" id="punch" onclick="if (!window.__cfRLUnblockHandlers) return false; punchJob(86);" style=""><span>连续2天打卡</span></div>
        # 断签？                2天未打卡
        elements = self.driver.find_elements(By.CSS_SELECTOR, "div.card.card_old.fr")
        for element in elements:
            match = re.search('连续(\d+)天打卡', element.text)
            if match:
                self.sign_result = True
                self.sign_result_info = f"已经签到过了。连续{match.group(1)}天打卡"
                return True
            if re.search('每日打卡|\d+天未打卡', element.text):
                self.sign_result_info = f"未曾打卡"
                return False
        logger.info(f"未知异常。")
        self.sign_result_info = f"未知异常"
        return False
    def collect_info(self) -> dict:
        self.result = {
            "module_name": self.module_name,
            "site_name": self.site_name,
            "site_url": self.indexUrl,
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