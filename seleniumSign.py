import logging
import sys
import os
import importlib
import re
import time
from init import profile
from init import loginit
from helper import listHelper

# 可否使用这个过cf验证？
# import undetected_chromedriver as uc
# from selenium import webdriver

# options = webdriver.ChromeOptions() 
# options.add_argument("start-maximized")
# driver = uc.Chrome(options=options)
# driver.get(url)

logger = loginit.initialLog()

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
# from selenium.webdriver.support.wait import WebDriverWait

ffOptions = Options()

ffOptions.add_argument("-profile")
ffOptions.add_argument(profile.getProfilePath())
# ffOptions.add_argument(r"C:\Users\ZXW000\AppData\Roaming\Mozilla\Firefox\Profiles\xhvtyp4t.default-release-1583421326042")
driver = webdriver.Firefox(options=ffOptions)
logger.info(driver.execute_script("return navigator.userAgent"))

'''
WebDriverWait(driver, 10).until(
        lambda wd: driver.execute_script("return document.readyState") == 'complete',
        "Page taking too long to load"
    )
'''

# 获取目录下所有.py文件的文件名
target_directory = 'target'
py_files = [f[:-3] for f in os.listdir(target_directory) if f.endswith('.py')]

signList = []
# 动态导入所有.py文件
for module_name in py_files:
    module = importlib.import_module(f'{target_directory}.{module_name}')
    signList.append(module.signClass(driver))


# 支持访问每个request请求的selenium
# https://pypi.org/project/selenium-wire/
# pip install selenium-wire

succeedList = []
failedList = []
for sign in signList:
    logger.info(f"开始{sign.indexUrl}")
    if hasattr(sign, 'accessIndex') and callable(getattr(sign, 'accessIndex')):
        sign.accessIndex()
    if hasattr(sign, 'sign') and callable(getattr(sign, 'sign')):
        sign.sign()
    if hasattr(sign, 'validSign') and callable(getattr(sign, 'validSign')):
        if sign.validSign():
            succeedList.append(sign.indexUrl)
            sign.exit()
            continue
    failedList.append(sign.indexUrl)
    sign.exit()


logger.info("签到成功列表：")
listHelper.printList(succeedList)

logger.info("签到失败列表：")
listHelper.printList(failedList)

driver.quit()