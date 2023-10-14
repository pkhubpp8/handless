import os
import sys
from init import firefox_profile
from init import myLogger
from helper import listHelper
from helper import moduleImport


# 可否使用这个过cf验证？
# import undetected_chromedriver as uc
# from selenium import webdriver

# options = webdriver.ChromeOptions()
# options.add_argument("start-maximized")
# driver = uc.Chrome(options=options)
# driver.get(url)

# 使用os.path.exists()函数检查路径是否存在
logPath = 'log/'
if not os.path.exists(logPath):
    # 如果路径不存在，使用os.makedirs()函数创建它
    os.makedirs(logPath)

geckodriver_log_path = logPath + 'geckodriver.log'
sign_log_path = logPath + 'sign.log'

logger = myLogger.myLogger('sign', sign_log_path).getLogger()

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
# from selenium.webdriver.support.wait import WebDriverWait

ffOptions = Options()

ffOptions.add_argument("-profile")
profile_dir = firefox_profile.getDefaultProfilePath()
if profile_dir:
    ffOptions.add_argument(profile_dir)
else:
    tempDriver = firefox_profile.startTempDriver(geckodriver_log_path)
    profile_dir = firefox_profile.getProfilePath(tempDriver)
    firefox_profile.stopTempDriver(tempDriver)
    if profile_dir:
        ffOptions.add_argument(profile_dir)
    else:
        logger.error(f"无法获取profile")
        sys.exit(-1)


service = webdriver.firefox.service.Service(log_path=geckodriver_log_path)
driver = webdriver.Firefox(options=ffOptions, service=service)
logger.info(driver.execute_script("return navigator.userAgent"))

'''
WebDriverWait(driver, 10).until(
        lambda wd: driver.execute_script("return document.readyState") == 'complete',
        "Page taking too long to load"
    )
'''


# 获取目录下.py文件的文件名
target_directory = 'target'
data = moduleImport.load_target_json(target_directory, 'sign_site.json')
if 'all' in data and data['all'] != True and "signSite" in data:
    sign_queue = moduleImport.import_modules(all = False, dir = target_directory, sites = data['signSite'], driver = driver)
else:
    logger.info("import所有模块")
    sign_queue = moduleImport.import_modules(all = True, dir = target_directory, sites = [], driver = driver)


# 支持访问每个request请求的selenium
# https://pypi.org/project/selenium-wire/
# pip install selenium-wire

succeedList = []
failedList = []
while not sign_queue.empty():
    sign = sign_queue.get()
    logger.info(f"开始{sign.indexUrl}")
    if hasattr(sign, 'accessIndex') and callable(getattr(sign, 'accessIndex')):
        sign.accessIndex()
    if hasattr(sign, 'sign') and callable(getattr(sign, 'sign')):
        sign.sign()
    if hasattr(sign, 'msgCheck') and callable(getattr(sign, 'msgCheck')):
        sign.msgCheck()
    if hasattr(sign, 'validSign') and callable(getattr(sign, 'validSign')):
        if sign.validSign():
            succeedList.append(sign.indexUrl)
        else:
            failedList.append(sign.indexUrl)
    else:
        failedList.append(sign.indexUrl)
    sign.exit()
    if hasattr(sign, 'logResult') and callable(getattr(sign, 'logResult')):
        sign.logResult()

logger.info("签到成功列表：")
listHelper.printList(succeedList, logger)

logger.info("签到失败列表：")
listHelper.printList(failedList, logger)

driver.quit()