from selenium.webdriver.common.by import By
import re
import logging
import time
from ._BASE import signBase

logger = logging.getLogger('sign')

class signClass(signBase):
    def __init__(self, url = 'https://www.manhuabudangbbs.com/index.php', module_name: str = 'bdbbsSign'):
        self.indexUrl = url
        self.orig_index = 'https://www.manhuabudangbbs.com/'
        self.module_name = module_name
        super().__init__("manhuabudangbbs")
    def accessIndex(self):
        self.driver.get(self.indexUrl)  # 打开链接
        time.sleep(1)
        elements = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "每日打卡")
        for element in elements:
            if element.get_attribute("href") == (self.orig_index + 'u.php'):
                element.click()
                time.sleep(1)
                break
    def valid_access(self):
        if not re.search('Powered by phpwind', self.driver.title):
            self.access_result = False
            self.access_result_info = f"标题异常：{self.driver.title}"
            return False
        elements = self.element = self.driver.find_elements(By.ID, 'td_userinfomore')
        for element in elements:
            if element.text:
                self.access_result = True
                self.access_result_info = ""
                return True
        self.access_result = False
        self.access_result_info = f"未登录"
        return False
    def sign(self):
        elements = self.driver.find_elements(By.CSS_SELECTOR, "div.card.card_old.fr")
        if len(elements) > 0:
            for element in elements:
                match = re.search(r'连续(\d+)天打卡', element.text)
                if match:
                    logger.info('已打卡，无需打卡')
                    return
        # elements = self.driver.find_elements(By.CSS_SELECTOR, "div.card.fr")
        # 不知为何，sign的时候用By.CSS_SELECTOR, "div.card.fr"的结果会是"未曾打卡2"
        # elements = self.driver.find_elements(By.ID, "punch")
        elements = self.driver.find_elements(By.CSS_SELECTOR, "div.card.fr")
        for element in elements:
            logger.warning(f"this is only for test: {element.text}")
            match = re.search(r'每日打卡|\d+天未打卡', element.text)
            if match:
                element.click()
                time.sleep(1)
                self.driver.refresh()
                time.sleep(1)
                return
        logger.warning('打卡过程异常')
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
            match = re.search(r'连续(\d+)天打卡', element.text)
            if match:
                self.sign_result = True
                self.sign_result_info = f"已经签到过了。连续{match.group(1)}天打卡"
                return True
            if re.search(r'每日打卡|\d+天未打卡', element.text):
                self.sign_result = False
                self.sign_result_info = f"未曾打卡1"
                return False
        elements = self.driver.find_elements(By.CSS_SELECTOR, "div.card.fr")
        for element in elements:
            if re.search(r'每日打卡|\d+天未打卡', element.text):
                self.sign_result = False
                self.sign_result_info = f"未曾打卡2"
                return False
        self.sign_result = False
        self.sign_result_info = f"未知异常"
        return False
    def collect_info(self) -> dict:
        t = time.time()
        self.result = {
            "module_name": self.module_name,
            "site_name": self.site_name,
            "site_url": self.indexUrl,
            "access_result": self.access_result,
            "access_result_info": self.access_result_info,
            "sign_result": self.sign_result,
            "sign_result_info": self.sign_result_info,
            "timestamp": int(t),
            "timestring": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t)),
            "new_message": self.new_message,
            "extra_info": self.extra_info
        }
        return self.result
