from selenium.webdriver.common.by import By
import re
import logging
import time
import datetime
from ._BASE import signBase

logger = logging.getLogger('sign')

class signClass(signBase):
    def __init__(self, driver, url = 'https://moeshare.cc/', module_name: str = 'moeshareSign'):
        self.indexUrl = url
        self.driver = driver
        self.module_name = module_name
        super().__init__("moeshare")
    def accessIndex(self):
        self.driver.execute_script("window.open('', '_blank');")  # 打开新标签页
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
        self.driver.get(self.indexUrl)  # 打开链接
        time.sleep(1)
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
                elements = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "每日打卡")
                for element in elements:
                    if element.get_attribute("href") == (self.indexUrl + 'u.php'):
                        element.click()
                        time.sleep(1)
                        break
                return True
        self.access_result = False
        self.access_result_info = f"未登录"
        return False
    def msgCheck(self) -> bool:
        elements = self.driver.find_elements(By.ID, "message_remind")
        if len(elements) == 1:
            match = re.search('(.*新消息)\n.*', elements[0].text)
            if match:
                self.new_message = match.group(1).strip()
            else:
                logger.warning("message_remind")
                self.new_message = "message_remind: " + elements[0].text.strip()
            return True
        elif len(elements) == 0:
            return False
        else:
            self.new_message = "warning: " + elements[0].text.strip()
            logger.warning(f"找到elements长度{len(elements)}异常")
            return False
    def sign(self):
        elements = self.driver.find_elements(By.CLASS_NAME, "mb5")
        self.liveness = 0
        for element in elements:
            match = re.search('活跃度：(\d+)', element.text)
            if match:
                self.liveness = int(match.group(1))
                break
        if self.liveness < 10:
            return
        elements = self.driver.find_elements(By.CLASS_NAME, "card")
        for element in elements:
            if element.text == '每日打卡' and element.get_attribute("disabled") != 'true' and self.liveness >= 10:
                element.click()
                time.sleep(1)
                self.driver.refresh()
                time.sleep(1)
                return
    def validSign(self):
        if not re.search('Powered by phpwind', self.driver.title):
            self.sign_result = False
            self.sign_result_info = f"标题异常：{self.driver.title}"
            return False
        elements = self.driver.find_elements(By.CLASS_NAME, "card")
        for element in elements:
            if element.text == '每日打卡' and element.get_attribute("disabled") == 'true':
                self.sign_result = True
                self.sign_result_info = f"已经签到过了。"
                return True
            elif element.text == '每日打卡' and element.get_attribute("disabled") != 'true':
                self.sign_result = False
                if hasattr(self, 'liveness') and self.liveness < 10:
                    self.sign_result_info = f"未签到。活跃度不够: {self.liveness}"
                else:
                    self.sign_result_info = f"未签到。先调用sign"
                return False
            # 这是未打卡。无论活跃度多少
            # <button id="punch" type="button" onclick="punchJob();" class="card">每日打卡</button>
            # 这是已打卡。无论活跃度多少
            # <button id="punch" type="button" onclick="punchJob();" class="card card_old" disabled="">每日打卡</button>
            # 这是打完卡，重新进来
            # <button type="button" class="card card_old" disabled="">每日打卡</button>
        self.sign_result = False
        self.sign_result_info = f"未知异常。"
        return False
    def auto_reply_for_liveness(self):
        # 10月18日 00:22:25, 新的一天，灌点水，拿点活跃度
        reply_info = f"{datetime.datetime.now().strftime('%m月%d日 %H:%M:%S')}, 新的一天，灌点水，拿点活跃度"
        # todo
    def collect_info(self) -> dict:
        current_date_time = datetime.datetime.now()
        day = current_date_time.day
        if day == 28:
            self.extra_info = "今天可以换取道具了。"
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
