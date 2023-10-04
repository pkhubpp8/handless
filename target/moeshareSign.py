from selenium.webdriver.common.by import By
import re
import logging
import time
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger('sign')

class signClass:
    def __init__(self, driver, url = 'https://moeshare.cc/index.php'):
        self.indexUrl = url
        self.driver = driver
    def accessIndex(self):
        self.driver.execute_script("window.open('', '_blank');")  # 打开新标签页
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
        self.driver.get(self.indexUrl)  # 打开链接
        time.sleep(1)
    def sign(self):
        self.driver.get('https://moeshare.cc/u.php')
        time.sleep(1)
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
            if element.text == '每日打卡' and self.liveness >= 10:
                element.click()
                time.sleep(1)
                self.driver.refresh()
                time.sleep(1)
                return
    def validSign(self):
        if not re.search('Powered by phpwind', self.driver.title):
            logger.info(f"标题异常：{self.driver.title}")
            return False
        elements = self.driver.find_elements(By.CLASS_NAME, "mb5")
        remainLiveness = 0
        for element in elements:
            match = re.search('活跃度：(\d+)', element.text)
            if match:
                remainLiveness = int(match.group(1))
                break
        if not hasattr(self, 'liveness'):
            logger.info(f"请先执行sign方法")
            return False
        if remainLiveness < self.liveness:
            myMB = 0
            for element in elements:
                match = re.search('MB：(\d+)', element.text)
                if match:
                    myMB = int(match.group(1))
                    break
            logger.info(f"签到成功。剩余活跃度：{remainLiveness}，当前MB：{myMB}")
            return True
        if remainLiveness == self.liveness and remainLiveness >= 10:
            logger.info(f"已经签到过了。")
            return True
        if remainLiveness == self.liveness and remainLiveness < 10:
            logger.info(f"未知是否签到")
            # todo 如何判断是否已签到？
            return False
        logger.info(f"未知异常。")
        return False
    def exit(self):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页