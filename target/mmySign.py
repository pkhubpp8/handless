from selenium.webdriver.common.by import By
import re
import logging
import time
import random
from ._BASE import signBase

logger = logging.getLogger('sign')

class signClass(signBase):
    def __init__(self, driver, url: str = 'https://www.mmybt.com/', module_name: str = 'mmySign'):
        self.indexUrl = url
        self.driver = driver
        self.module_name = module_name
        super().__init__("mmybt")
    def accessIndex(self):
        self.driver.execute_script("window.open('', '_blank');")  # 打开新标签页
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
        self.driver.get(self.indexUrl)  # 打开链接

        self.sign_is_clicked = False
        time.sleep(2)
    def valid_access(self):
        if not re.search('慢慢游社区', self.driver.title):
            self.access_result = False
            self.access_result_info = f"标题异常：{self.driver.title}"
            return False
        # medium left
        elements = self.driver.find_elements(By.XPATH, '//strong[contains(@class, "vwmy")]')
        for element in elements:
            if element.text:
                self.access_result = True
                self.access_result_info = ""
                return True
        self.access_result = False
        self.access_result_info = f"未登录"
        return False
    def sign(self):
        elements = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "签到领奖!")
        if len(elements) == 0:
            logger.warning(f"签到按钮获取失败{len(elements)}")
            return
        elif len(elements) > 1:
            logger.warning(f"签到按钮获取长度异常{len(elements)}")
        elements[0].click()
        time.sleep(2)
        emo = [
            self.driver.find_elements(By.ID, "kx"),
            self.driver.find_elements(By.ID, "ng"),
            self.driver.find_elements(By.ID, "ym"),
            self.driver.find_elements(By.ID, "wl"),
            self.driver.find_elements(By.ID, "nu"),
            self.driver.find_elements(By.ID, "ch"),
            self.driver.find_elements(By.ID, "fd"),
            self.driver.find_elements(By.ID, "yl"),
        ]
        index = random.randint(0, len(emo) - 1)
        while (len(emo) > 0 and len(emo[index]) != 1):
            emo.pop(index)
            index = random.randint(0, len(emo) - 1)
        if len(emo) == 0 or len(emo[index]) != 1:
            logger.warning(f"签到心情获取异常")
            return
        emo[index][0].click()

        elements = self.driver.find_elements(By.XPATH, "//label[contains(text(), '不想填写')]")
        if len(elements) == 0:
            logger.warning(f"想说模式获取失败")
            return
        if len(elements) > 1:
            logger.warning(f"想说模式获取异常")
            return
        elements[0].click()

        click_me_to_signs = self.driver.find_elements(By.CLASS_NAME, "pn.pnc")
        for element in click_me_to_signs:
            if element.text == '点我签到!':
                element.click()
                self.sign_is_clicked = True
                time.sleep(10)
                return
    def validSign(self):
        if not re.search('慢慢游社区', self.driver.title):
            self.sign_result = False
            self.sign_result_info = f"标题异常：{self.driver.title}"
            return False
        if self.sign_is_clicked == True:
            self.sign_result = True
            self.sign_result_info = f"签到成功"
        else:
            self.sign_result = False
            self.sign_result_info = f"未曾签到"
        return False
    def collect_info(self) -> dict:
        self.result = {
            "module_name": self.module_name,
            "site_name": self.site_name,
            "site_url": self.indexUrl,
            "access_result": self.access_result,
            "access_result_info": self.access_result_info,
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
