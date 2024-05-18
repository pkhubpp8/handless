from selenium.webdriver.common.by import By
import re
import logging
import time
from ._BASE import signBase

logger = logging.getLogger('sign')

class signClass(signBase):
    def __init__(self, url = 'https://bbs.oldmantvg.net/', module_name: str = 'oldmanSign'):
        self.indexUrl = url
        self.module_name = module_name
        super().__init__("oldmantvg")
    def accessIndex(self):
        self.driver.get(self.indexUrl)  # 打开链接
    def msgCheck(self) -> bool:
        elements = self.driver.find_elements(By.ID, "nav-usernotice")
        if len(elements) == 1:
            match = re.search(r'消息\s*(\d)', elements[0].text)
            if match:
                self.new_message = f"消息 {match.group(1)}"
                return True
            else:
                return False
        elif len(elements) == 0:
            self.new_message = "warning: 未登录"
            logger.warning(f"找到elements长度{len(elements)}异常")
            return False
        else:
            self.new_message = "warning: " + elements[0].text.strip()
            logger.warning(f"找到elements长度{len(elements)}异常")
            return True
    def sign(self):
        elements = self.driver.find_elements(By.ID, "sign_title")
        for element in elements:
            if element.text == '签到':
                element.click()
                time.sleep(3)
                return
    def validSign(self):
        if not re.search('老男人游戏网配套论坛', self.driver.title):
            self.sign_result = False
            self.sign_result_info = f"标题异常：{self.driver.title}"
            return False
        elements = self.driver.find_elements(By.CLASS_NAME, "modal-body")
        for element in elements:
            logger.debug(f"oldman sign1 result: {element.text}")
            match = re.search(r'签到成功！您是第(\d+)名签到！(.*|\n|\r\n)\[连签奖励\](.*|\n|\r\n)经验:(\d+)、蘑菇:(\d+)、鲜花:(\d+)', element.text)
            if match:
                self.sign_result = True
                self.sign_result_info = f"第{match.group(1)}名签到. 经验:{match.group(4)}、蘑菇:{match.group(5)}、鲜花:{match.group(6)}"
                return True
        logger.debug("sleep 1秒")
        time.sleep(1)
        elements = self.driver.find_elements(By.CLASS_NAME, "modal-body")
        for element in elements:
            logger.debug(f"oldman sign2 result: {element.text}")
            match = re.search(r'签到成功！您是第(\d+)名签到！(.*|\n|\r\n)\[连签奖励\](.*|\n|\r\n)经验:(\d+)、蘑菇:(\d+)、鲜花:(\d+)', element.text)
            if match:
                self.sign_result = True
                self.sign_result_info = f"第{match.group(1)}名签到. 经验:{match.group(4)}、蘑菇:{match.group(5)}、鲜花:{match.group(6)}"
                return True
        elements = self.driver.find_elements(By.ID, "sign_title")
        for element in elements:
            if element.text == '已签':
                self.sign_result = True
                self.sign_result_info = '已经签到过了。'
                return True
            if element.text == '签到':
                self.sign_result = False
                self.sign_result_info = "还未签到。"
                return False
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
