from selenium.webdriver.common.by import By
import re
import logging

logger = logging.getLogger('sign')

class signClass:
    def __init__(self, driver, url = 'https://dicmusic.com/index.php', module_name: str = 'dicSign'):
        self.indexUrl = url
        self.driver = driver
        self.module_name = module_name
    def accessIndex(self):
        self.driver.execute_script("window.open('', '_blank');")  # 打开新标签页
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
        self.driver.get(self.indexUrl)  # 打开链接
    def msgCheck(self) -> bool:
        elements = self.driver.find_elements(By.CLASS_NAME, "noty_text")
        if len(elements) == 1:
            if '新信息' in elements[0].text:
                logger.info(elements[0].text)
            else:
                logger.warning(elements[0].text)
            return True
        elif len(elements) == 0:
            return False
        else:
            logger.info(elements[0].text)
            logger.warning(f"找到elements长度{len(elements)}异常")
            return False
    def sign(self):
        pass
    def validSign(self):
        if not re.search('DIC', self.driver.title):
            logger.info(f"标题异常：{self.driver.title}")
            return False
        return True
    def exit(self):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
        self.driver = None