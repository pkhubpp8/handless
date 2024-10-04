from selenium.webdriver.common.by import By
import re
import logging
import time
from ._BASE import signBase

logger = logging.getLogger('sign')

class signClass(signBase):
    def __init__(self, url = 'https://pt.btschool.club/index.php', module_name: str = 'btschoolSign'):
        self.indexUrl = url
        self.module_name = module_name
        super().__init__("btschool")
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
        elements = self.driver.find_elements(By.LINK_TEXT, "每日签到")
        for element in elements:
            if 'addbonus' in element.get_attribute("href"):
                element.click()
                break
    def validSign(self):
        # 'BTSCHOOL :: 首页 比特校园PT小乐园 - Powered by NexusPHP'
        # https://pt.btschool.club/index.php?action=addbonus
        if re.search('(请稍后|Just a moment)...', self.driver.title):
            logger.info(f"标题异常：{self.driver.title}，尝试直接签到")
            self.driver.get(self.indexUrl + "?action=addbonus")
            time.sleep(5)
        if not re.search('BTSCHOOL.*NexusPHP', self.driver.title):
            self.sign_result = False
            self.sign_result_info = f"标题异常：{self.driver.title}"
            return False
        elements = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "今天签到")
        for element in elements:
            match = re.search(r'今天签到您获得(\d+)点魔力值', element.text)
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
        t = time.time()
        self.result = {
            "module_name": self.module_name,
            "site_name": self.site_name,
            "site_url": self.indexUrl,
            "sign_result": self.sign_result,
            "sign_result_info": self.sign_result_info,
            "timestamp": int(t),
            "timestrimg": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t)),
            "new_message": self.new_message,
            "extra_info": self.extra_info
        }
        return self.result
