from selenium.webdriver.common.by import By
import re
import logging
import time
from ._BASE import signBase

logger = logging.getLogger('sign')

class signClass(signBase):
    def __init__(self, url = 'https://dicmusic.com/index.php', module_name: str = 'dicSign'):
        self.indexUrl = url
        self.module_name = module_name
        super().__init__("dicmusic")
    def accessIndex(self):
        self.driver.get(self.indexUrl)  # 打开链接
        time.sleep(6)
    def msgCheck(self) -> bool:
        elements = self.driver.find_elements(By.CLASS_NAME, "noty_text")
        if len(elements) == 1:
            if '新信息' in elements[0].text:
                self.new_message = elements[0].text.strip()
            else:
                logger.warning(elements[0].text)
                self.new_message = "warning: " + elements[0].text.strip()
            return True
        elif len(elements) == 0:
            return False
        else:
            self.new_message = "warning: " + elements[0].text.strip()
            logger.warning(f"找到elements长度{len(elements)}异常")
            return True
    def sign(self):
        pass
    def validSign(self):
        if not re.search('DIC', self.driver.title):
            self.sign_result = False
            self.sign_result_info = f"标题异常：{self.driver.title}"
            return False
        self.sign_result = True
        self.sign_result_info = f""
        return True
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
