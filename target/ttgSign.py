from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoAlertPresentException
import re
import logging
import time
from ._BASE import signBase

logger = logging.getLogger('sign')

class signClass(signBase):
    def __init__(self, url = 'https://totheglory.im/index.php', module_name: str = 'ttgSign'):
        self.indexUrl = url
        self.module_name = module_name
        super().__init__("ttg")
    def accessIndex(self):
        self.driver.get(self.indexUrl)  # 打开链接
    def valid_access(self):
        if not re.search('TTG', self.driver.title):
            self.access_result = False
            self.access_result_info = f"标题异常：{self.driver.title}"
            return False
        elements = self.element = self.driver.find_elements(By.CLASS_NAME, 'smallfont')
        if len(elements) > 0:
            self.access_result = True
            self.access_result_info = f""
            return True
        self.access_result = False
        self.access_result_info = f"未登录"
        return False
    def msgCheck(self) -> bool:
        new_msg_elements = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "个重要短讯")
        if len(new_msg_elements) == 1:
            self.new_message = new_msg_elements[0].text.strip()
            return True
        unread_elements = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "您有新的未读的公告！")
        if len(unread_elements) == 1:
            self.new_message = unread_elements[0].text.strip()

        if len(new_msg_elements) == 0 and len(unread_elements) == 0:
            return False
        else:
            self.new_message = "warning: new msg size: " + str(len(new_msg_elements))
            self.new_message = self.new_message + ", new important msg size: " + str(len(unread_elements))
            logger.warning(f"找到elements长度{len(new_msg_elements)}, {len(unread_elements)}异常")
            return True
    def sign(self):
        elements = self.driver.find_elements(By.ID, "sp_signed")
        for element in elements:
            if element.text == '签到':
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
        if not re.search('TTG', self.driver.title):
            self.sign_result = False
            self.sign_result_info = f"标题异常：{self.driver.title}"
            return False
        if hasattr(self, 'alert_text') and self.alert_text is not None:
            match = re.search(r'您已连续签到(\d+)天，奖励(\d+)积分，明天继续签到将获得\d+积分奖励。', self.alert_text)
            if match:
                self.sign_result = True
                self.sign_result_info = f"连续签到{match.group(1)}，获得积分{match.group(2)}"
                return True
        elements = self.driver.find_elements(By.ID, "sp_signed")
        for element in elements:
            if element.text == '已签到':
                self.sign_result = True
                self.sign_result_info = f"已经签到过了。"
                return True
            if element.text == '签到':
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
