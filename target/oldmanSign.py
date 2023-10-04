from selenium.webdriver.common.by import By
import re
import logging

logger = logging.getLogger('sign')

class signClass:
    def __init__(self, driver, url = 'https://bbs.oldmantvg.net/'):
        self.indexUrl = url
        self.driver = driver
    def accessIndex(self):
        self.driver.execute_script("window.open('', '_blank');")  # 打开新标签页
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
        self.driver.get(self.indexUrl)  # 打开链接
    def sign(self):
        elements = self.driver.find_elements(By.ID, "sign_title")
        for element in elements:
            if element.text == '签到':
                element.click()
                return
    def validSign(self):
        if not re.search('老男人游戏网配套论坛', self.driver.title):
            logger.info(f"标题异常：{self.driver.title}")
            return False
        elements = self.driver.find_elements(By.CLASS_NAME, "modal-body")
        for element in elements:
            match = re.search('签到成功！您是第(\d+)名签到！\n\[连签奖励\]\n经验:(\d+)、蘑菇:(\d+)、鲜花:(\d+)', element.text)
            if match:
                logger.info(f"第{match.group(1)}名签到. 经验:{match.group(2)}、蘑菇:{match.group(3)}、鲜花:{match.group(4)}")
                return True
        elements = self.driver.find_elements(By.ID, "sign_title")
        for element in elements:
            if element.text == '已签':
                logger.info('已经签到过了。')
                return True
            if element.text == '签到':
                return False
        logger.info(f"未知异常。")
        return False
    def exit(self):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页