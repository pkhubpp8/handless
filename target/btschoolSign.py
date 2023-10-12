from selenium.webdriver.common.by import By
import re
import logging

logger = logging.getLogger('sign')

class signClass:
    def __init__(self, driver, url = 'https://pt.btschool.club/index.php'):
        self.indexUrl = url
        self.driver = driver
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
        elements = self.driver.find_elements(By.LINK_TEXT, "每日签到")
        for element in elements:
            if 'addbonus' in element.get_attribute("href"):
                element.click()
                break
    def validSign(self):
        if not re.search('BTSCHOOL.*NexusPHP', self.driver.title):
            logger.info(f"标题异常：{self.driver.title}")
            return False
        elements = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "今天签到")
        for element in elements:
            match = re.search('今天签到您获得(\d+)点魔力值', element.text)
            if match:
                logger.info(f"今天签到您获得{match.group(1)}点魔力值")
                return True
        elements = self.driver.find_elements(By.LINK_TEXT, "每日签到")
        if not elements:
            logger.info('已经签到过了。')
            return True
        logger.info(f"未知异常。")
        return False
    def exit(self):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页