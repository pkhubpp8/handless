from selenium.webdriver.common.by import By
import re
import logging
import time

logger = logging.getLogger('sign')

class signClass:
    def __init__(self, driver, url = 'https://moeshare.cc/'):
        self.indexUrl = url
        self.driver = driver
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
    def msgCheck(self) -> bool:
        elements = self.driver.find_elements(By.ID, "message_remind")
        if len(elements) == 1:
            match = re.search('(.*新消息)\n.*', elements[0].text)
            if match:
                logger.info(match.group(1))
            else:
                logger.warning("message_remind")
            return True
        elif len(elements) == 0:
            return False
        else:
            logger.info(elements[0].text)
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
            logger.info(f"标题异常：{self.driver.title}")
            return False
        elements = self.driver.find_elements(By.CLASS_NAME, "card")
        for element in elements:
            if element.text == '每日打卡' and element.get_attribute("disabled") == 'true':
                logger.info(f"已经签到过了。")
                return True
            elif element.text == '每日打卡' and element.get_attribute("disabled") != 'true':
                if hasattr(self, 'liveness') and self.liveness < 10:
                    logger.info(f"未签到。活跃度不够: {self.liveness}")
                else:
                    logger.info(f"未签到。先调用sign")
                return False
            # 这是未打卡。无论活跃度多少
            # <button id="punch" type="button" onclick="punchJob();" class="card">每日打卡</button>
            # 这是已打卡。无论活跃度多少
            # <button id="punch" type="button" onclick="punchJob();" class="card card_old" disabled="">每日打卡</button>
            # 这是打完卡，重新进来
            # <button type="button" class="card card_old" disabled="">每日打卡</button>
        logger.info(f"未知异常。")
        return False
    def exit(self):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页