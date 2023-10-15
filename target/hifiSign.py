from selenium.webdriver.common.by import By
import re
import logging
import time

logger = logging.getLogger('sign')

class signClass:
    def __init__(self, driver, url = 'https://www.hifini.com/', module_name: str = 'hifiSign'):
        self.indexUrl = url
        self.driver = driver
        self.module_name = module_name
    def accessIndex(self):
        self.driver.execute_script("window.open('', '_blank');")  # 打开新标签页
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
        self.driver.get(self.indexUrl)  # 打开链接
    def sign(self):
        elements = self.driver.find_elements(By.ID, "sign")
        for element in elements:
            if element.text == '签到':
                # 去除delay跳转部分
                sign_script = '''
var postdata = sg_sign.serialize();
$.xpost(xn.url('sg_sign'), postdata, function(code, message) {
    $.alert(message);
});
                '''
                self.driver.execute_script(sign_script)
                time.sleep(2)
                return
    def validSign(self):
        if not re.search('HiFiNi', self.driver.title):
            logger.info(f"标题异常：{self.driver.title}")
            return False
        elements = self.driver.find_elements(By.CLASS_NAME, "modal-body")
        for element in elements:
            match = re.search('成功签到！今日排名(\d+)，连续签到超过\d+天额外奖励\d+金币，总奖励(\d+)金币！', element.text)
            if match:
                logger.info(f"第{match.group(1)}名签到. 奖励金币:{match.group(2)}")
                return True
        elements = self.driver.find_elements(By.ID, "sign")
        for element in elements:
            if element.text == '已签':
                logger.info('已经签到过了。')
                return True
            if element.text == '签到':
                logger.info(f"未签到。")
                return False
        logger.info(f"未知异常。")
        return False
    def exit(self):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])  # 切换到新标签页
        self.driver = None