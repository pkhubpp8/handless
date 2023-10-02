from selenium.webdriver.common.by import By
import re
import logging

logger = logging.getLogger('sign')

class signClass:
    def __init__(self, driver, url = 'https://dicmusic.com/index.php'):
        self.indexUrl = url
        self.driver = driver
    def accessIndex(self):
        self.driver.execute_script("window.open('', '_blank');")  # 打开新标签页
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
        self.driver.get(self.indexUrl)  # 打开链接
    def sign(self):
        pass
    def validSign(self):
        if not re.search('DIC', self.driver.title):
            logger.info(f"标题异常：{self.driver.title}")
            return False
        elements = self.driver.find_elements(By.CLASS_NAME, "noty_text")
        for element in elements:
            if '新信息' in element.text:
                logger.info(element.text)
        return True
    def exit(self):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页