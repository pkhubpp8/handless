from selenium.webdriver.common.by import By
import re
import logging

logger = logging.getLogger('sign')

class signClass:
    def __init__(self, driver, url: str = 'https://azusa.wiki/index.php', module_name: str = 'azusaSign'):
        self.indexUrl = url
        self.driver = driver
        self.module_name = module_name
    def accessIndex(self):
        self.driver.execute_script("window.open('', '_blank');")  # 打开新标签页
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
        self.driver.get(self.indexUrl)  # 打开链接
    def msgCheck(self) -> bool:
        elements = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "条新短讯！点击查看")
        if len(elements) == 1:
            logger.info(elements[0].text)
            return True
        elif len(elements) == 0:
            return False
        else:
            logger.info(elements[0].text)
            logger.warning(f"找到elements长度{len(elements)}异常")
            return False
    def sign(self):
        elements = self.driver.find_elements(By.CLASS_NAME, "faqlink")
        for element in elements:
            if element.text == '[签到得魔力]':
                element.click()
                break
    def validSign(self):
        if not re.search('梓喵.*NexusPHP', self.driver.title):
            logger.info(f"标题异常：{self.driver.title}")
            return False
        elements = self.driver.find_elements(By.CLASS_NAME, "text")
        for element in elements:
            match = re.search('这是[你您]的第\s+(\d+)\s+次签到.*已连续签到\s+(\d+)\s+天.*本次签到获得\s+(\d+)\s+个魔力值', element.text)
            if match:
                logger.info(f"第{match.group(1)}次签到，连续签到{match.group(2)}，获得魔力{match.group(3)}")
                return True
        elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[class=""]')
        for element in elements:
            match = re.search('\[签到已得(\d+), 补签卡:\s*\d+\]', element.text)
            if match:
                logger.info(f"已经签到过了。签到已得{match.group(1)}")
                return True
        logger.info(f"未知异常。")
        return False
    def exit(self):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
        self.driver = None