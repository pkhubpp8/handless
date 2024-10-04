from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import re
import logging
import time
import random
from ._BASE import signBase

logger = logging.getLogger('sign')

class signClass(signBase):
    def __init__(self, url = 'https://www.hifini.com/sg_sign.htm', module_name: str = 'hifiSign'):
        self.indexUrl = url
        self.module_name = module_name
        super().__init__("hifi")
    def accessIndex(self):
        self.driver.get(self.indexUrl)  # 打开链接
        time.sleep(10)
    def _simulate_human(self):
        # 定位要拖动的元素
        draggable_elements = self.driver.find_elements(By.XPATH, '//div[@class="handler handler_bg"]')
        if len(draggable_elements) != 1:
            logger.info(f"寻找到了{len(draggable_elements)}个draggable元素")
            return False

        # 定位拖动的目标位置
        target_elements = self.driver.find_elements(By.XPATH, '//div[@class="drag_text"]')
        if len(target_elements) != 1:
            logger.info(f"寻找到了{len(target_elements)}个target元素")
            return False
        else:
            if target_elements[0].text == '拖动滑块验证':
                logger.info('获取到了target元素')
            else:
                logger.info(f'没有获取到target元素: {target_elements[0].text}')
                return False
        x_offset = target_elements[0].size['width'] + random.randint(0, 5)
        y_offset = 0 + random.randint(0, 5)

        # 开始拖动
        action_chains = ActionChains(self.driver)
        action_chains.click_and_hold(draggable_elements[0]).perform()       # 起始
        time.sleep(0.1 + round(random.uniform(-0.1, 0.1) / 0.01) * 0.01)    # 增加随机0.1 + [-0.1, 0.1]的延迟，模拟拖动速度
        action_chains.move_by_offset(x_offset / 2, y_offset / 2).perform()  # 中点
        time.sleep(0.1 + round(random.uniform(-0.1, 0.1) / 0.01) * 0.01)    # 增加随机0.1 + [-0.1, 0.1]的延迟，模拟拖动速度
        action_chains.move_by_offset(x_offset, y_offset).perform()          # 结束
        time.sleep(0.1 + round(random.uniform(-0.1, 0.1) / 0.01) * 0.01)    # 增加随机0.1 + [-0.1, 0.1]的延迟，模拟拖动速度
        action_chains.release().perform()                                   # 释放
        time.sleep(5)
        if not re.search('HiFiNi', self.driver.title):
            return False
        return True

    def valid_access(self):
        if re.search('滑动验证', self.driver.title):
            if self._simulate_human():
                self.access_result = True
                self.access_result_info = f"人机验证成功"
                logger.info('continue')
            else:
                self.access_result = False
                self.access_result_info = f"标题异常：{self.driver.title}，且人机验证失败"
                return False
        if not re.search('HiFiNi', self.driver.title):
            self.access_result = False
            self.access_result_info = f"标题异常：{self.driver.title}"
            return False
        elements = self.driver.find_elements(By.XPATH, '//li[@class="nav-item username"]')
        for element in elements:
            if element.text:
                self.access_result = True
                if self.access_result_info:
                    self.access_result_info = self.access_result_info + ", 登录成功"
                else:
                    self.access_result_info = "登录成功"
                return True
        self.access_result = False
        self.access_result_info = f"未登录"
        return False
    def sign(self):
        sign_special_value = None
        script_elements = self.driver.find_elements(By.TAG_NAME, "script")
        for script_element in script_elements:
            match = re.search(r'var sign = "(\w+)";', script_element.get_attribute("outerHTML"))
            if match:
                sign_special_value = match.group(1)
                logger.info(f'sign_special_value = {sign_special_value}')
                break
        elements = self.driver.find_elements(By.ID, "sign")
        for element in elements:
            if element.text == '签到':
                # 去除delay跳转部分
                # todo, 最好自动从网页上获取
                sign_script = '''
var sign = "{special_value}";
$.xpost(xn.url('sg_sign'), {{'sign':  sign}}, function(code, message) {{
    $.alert(message);
}});
'''
                if sign_special_value:
                    formatted_script = sign_script.format(special_value=sign_special_value)
                    self.driver.execute_script(formatted_script)
                else:
                    logger.warning(f'格式化失败，不执行脚本')
                time.sleep(2)
                return
    def validSign(self):
        if not re.search('HiFiNi', self.driver.title):
            self.sign_result = False
            self.sign_result_info = f"标题异常：{self.driver.title}"
            return False
        elements = self.driver.find_elements(By.CLASS_NAME, "modal-body")
        for element in elements:
            # 成功签到！今日排名1234，总奖励(\d+)金币！
            # 成功签到！今日排名1234，连续签到超过\d+天额外奖励\d+金币，总奖励(\d+)金币！
            # 成功签到！今日排名1234，连续签到3天额外奖励\d+金币，总奖励(\d+)金币！
            match = re.search(r'成功签到！今日排名(\d+).*总奖励(\d+)金币！', element.text)
            if match:
                self.sign_result = True
                self.sign_result_info = f"第{match.group(1)}名签到. 奖励金币:{match.group(2)}"
                return True
        elements = self.driver.find_elements(By.ID, "sign")
        for element in elements:
            if element.text == '已签':
                self.sign_result = True
                self.sign_result_info = '已经签到过了。'
                return True
            if element.text == '签到':
                self.driver.refresh()
                time.sleep(2)
                es = self.driver.find_elements(By.ID, "sign")
                if len(es) == 1 and es[0].text == '已签':
                    self.sign_result = True
                    self.sign_result_info = "异常未弹窗。已经签到过了。"
                    return True
                self.sign_result = False
                self.sign_result_info = "确实未签到。"
                return False
        self.sign_result = False
        self.sign_result_info = f"未知异常。"
        return False
    def collect_info(self) -> dict:
        t = time.time()
        self.result = {
            "module_name": self.module_name,
            "site_name": self.site_name,
            "site_url": self.indexUrl,
            "access_result": self.access_result,
            "access_result_info": self.access_result_info,
            "sign_result": self.sign_result,
            "sign_result_info": self.sign_result_info,
            "timestamp": int(t),
            "timestring": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t)),
            "new_message": self.new_message,
            "extra_info": self.extra_info
        }
        return self.result
