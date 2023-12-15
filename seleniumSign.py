import os
import sys
from selenium.webdriver.common.by import By
import queue
import traceback
import time
# from selenium.webdriver.support.wait import WebDriverWait

from init import firefox_profile
from init import myLogger
from init import config_init
from helper import moduleImport

def printList(sign_list: [], logger, is_detail: bool):
    if not sign_list:
        logger.info("空")
    else:
        for sign in sign_list:
            if is_detail:
                if sign.result:
                    if sign.result.get('access_result_info'):
                        logger.info(f"{sign.indexUrl}: {sign.result.get('access_result_info')}")
                    elif sign.result.get('sign_result_info'):
                        logger.info(f"{sign.indexUrl}: {sign.result.get('sign_result_info')}")
                else:
                    logger.info(f"{sign.indexUrl}: no result")
            else:
                logger.info(f"{sign.indexUrl}")

def print_extra_info(sign_s_list: [], sign_f_list: []):
    logger.info("start print extra info")
    if not sign_s_list and not sign_f_list:
        logger.info("空")
        return
    for sign in sign_s_list:
        if sign.result:
            if sign.result.get('extra_info') or sign.result.get('new_message'):
                logger.info(f"s. {sign.indexUrl}; extra info: {sign.result.get('extra_info')}; new message: {sign.result.get('new_message')}")
    for sign in sign_f_list:
        if sign.result:
            if sign.result.get('extra_info') or sign.result.get('new_message'):
                logger.info(f"f. {sign.indexUrl}; extra info: {sign.result.get('extra_info')}; new message: {sign.result.get('new_message')}")


def get_sign_queue(driver):
    # 获取目录下.py文件的文件名
    target_directory = 'target'
    data = moduleImport.load_target_json(target_directory, 'sign_site.json')
    if 'all' in data and data['all'] != True and "module_list" in data:
        sign_queue = moduleImport.import_modules(all = False, dir = target_directory, sites = data['module_list'], driver = driver)
    else:
        logger.info("import所有模块")
        sign_queue = moduleImport.import_modules(all = True, dir = target_directory, sites = [], driver = driver)
    return sign_queue

def do_sign(sign_queue: queue.Queue, logger, driver) -> []:
    succeedList = []
    failedList = []
    while not sign_queue.empty():
        sign = sign_queue.get()
        logger.info(f"开始{sign.indexUrl}")

        try:
            if hasattr(sign, 'accessIndex') and callable(getattr(sign, 'accessIndex')):
                sign.accessIndex()
            if hasattr(sign, 'valid_access') and callable(getattr(sign, 'valid_access')):
                if not sign.valid_access():
                    if hasattr(sign, 'collect_info') and callable(getattr(sign, 'collect_info')):
                        logger.info(sign.collect_info())
                    failedList.append(sign)
                    sign.exit()
                    continue
            if hasattr(sign, 'sign') and callable(getattr(sign, 'sign')):
                sign.sign()
            if hasattr(sign, 'msgCheck') and callable(getattr(sign, 'msgCheck')):
                sign.msgCheck()
            if hasattr(sign, 'validSign') and callable(getattr(sign, 'validSign')):
                if sign.validSign():
                    succeedList.append(sign)
                else:
                    failedList.append(sign)
                    driver.save_screenshot('log/' + sign.module_name + '_snapshot.png')
                    with open('log/' + sign.module_name + '_page.html', 'w', encoding='utf-8') as file:
                        file.write(driver.page_source)
            else:
                failedList.append(sign)
            if hasattr(sign, 'collect_info') and callable(getattr(sign, 'collect_info')):
                logger.info(sign.collect_info())
        except Exception as e:
            logger.error(f"something error: {e}")
            logger.warning(traceback.format_exc())
            failedList.append(sign)
        sign.exit()

    return succeedList, failedList


def get_web_driver_and_logger():
    config_data = config_init.get_config_for_sign()
    log_path = config_data['log_path']
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    sign_log_path = os.path.join(log_path, 'sign')
    logger = myLogger.myLogger('sign', sign_log_path, True).getLogger()

    browser = config_data['browser']
    if browser == 'firefox':
        geckodriver_log_path = os.path.join(log_path, 'geckodriver.log')
        driver = firefox_profile.create_firefox_with_user_profile(geckodriver_log_path)
    elif browser == 'chrome':
        logger.error(f"当前不支持")
        sys.exit(-1)

    return driver, logger

def resign(fs, logger, driver):
    logger.info(f"失败{len(fs)}。尝试再次签到失败网站")
    sign_queue = queue.Queue()
    for f in fs:
        sign_queue.put(f)
    ss, fs = do_sign(sign_queue, logger, driver)
    return ss, fs

if __name__ == "__main__":
    driver, logger = get_web_driver_and_logger()
    '''
    WebDriverWait(driver, 10).until(
            lambda wd: driver.execute_script("return document.readyState") == 'complete',
            "Page taking too long to load"
        )
    '''
    if driver and logger:
        sign_queue = get_sign_queue(driver)
        ss, fs = do_sign(sign_queue, logger, driver)

        ss2 = []
        fs2 = []
        if fs:
            time.sleep(5)
            ss2, fs2 = resign(fs, logger, driver)
            logger.info(f"重新签到1, 成功{len(fs) - len(fs2)}, {len(ss2)}")

        ss3 = []
        fs3 = []
        if fs2:
            time.sleep(5)
            ss3, fs3 = resign(fs2, logger, driver)
            logger.info(f"重新签到2, 成功{len(fs2) - len(fs3)}, {len(ss3)}")

        logger.info("签到失败 列表：")
        printList(fs3, logger, True)

        print_extra_info(ss + ss2 + ss3, fs3)

        driver.quit()
    else:
        logger.error(f"webdriver 初始化失败")
        sys.exit(-1)