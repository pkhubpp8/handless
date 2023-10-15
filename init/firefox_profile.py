import logging
import re
import os
import sys

def checkEnv():
    exe = "geckodriver.exe"
    # 获取系统的环境变量PATH，并将其拆分成一个列表
    path = os.environ.get("PATH")
    path_list = path.split(os.pathsep)

    # 遍历每个路径，检查是否存在可执行文件
    for folder in path_list:
        exe_path = os.path.join(folder, exe)
        if os.path.isfile(exe_path):
            logging.info(f"{exe}路径为{exe_path}")
            return exe_path
    logging.info(f"未找到 {exe}")
    return None


def startTempDriver(log_path: str):
    if not checkEnv():
        return None

    from selenium import webdriver
    if log_path:
        service = webdriver.firefox.service.Service(log_path = log_path)
        driver = webdriver.Firefox(service=service)
    else:
        driver = webdriver.Firefox()
    return driver

def stopTempDriver(driver = None):
    if driver:
        driver.quit()


def getDefaultProfilePath():
    appdata_path = os.path.expandvars('%AppData%')
    file_path = os.path.join(appdata_path, r'Mozilla\Firefox\Profiles') # \xhvtyp4t.default-release-1583421326042')
    if os.path.exists(file_path):
        print(f'路径 {file_path} 存在')
        subdirectories = [d for d in os.listdir(file_path) if os.path.isdir(os.path.join(file_path, d))]
        if len(subdirectories) == 1:
            profile_dir = os.path.join(appdata_path, r'Mozilla\Firefox\Profiles', subdirectories[0])
            return profile_dir
    return None


def getProfilePath(driver = None):
    if not driver:
        return None

    driver.get("about:profiles")
    # 使用CSS选择器定位所有 "默认配置文件" 为 "是" 的元素以及对应的根目录元素

    from selenium.webdriver.common.by import By
    config_elements = driver.find_elements(By.CSS_SELECTOR, "th[data-l10n-id='profiles-is-default'] + td")
    root_dir_elements = driver.find_elements(By.CSS_SELECTOR, "th[data-l10n-id='profiles-rootdir'] + td")
    open_folder_button = driver.find_element(By.CSS_SELECTOR, "button[data-l10n-id='profiles-opendir']")

    # 初始化根目录
    root_dir_element = None

    # 遍历所有 "默认配置文件" 元素，查找文本内容为 "是" 的元素，并获取对应的根目录
    for i in range(len(config_elements)):
        if config_elements[i].text == "是":
            root_dir_element = root_dir_elements[i]
            break  # 找到匹配的元素后退出循环

    if root_dir_element:
        profile_path = re.sub(re.escape(open_folder_button.text), '', root_dir_element.text)
        return profile_path
    else:
        return None


def getUA(driver = None):
    if not driver:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0"
    return driver.execute_script("return navigator.userAgent")


def create_firefox_with_user_profile(webdriver_log_path: str):
    from selenium.webdriver.firefox.options import Options
    ffOptions = Options()

    ffOptions.add_argument("-profile")
    profile_dir = getDefaultProfilePath()
    if profile_dir:
        ffOptions.add_argument(profile_dir)
    else:
        tempDriver = startTempDriver(webdriver_log_path)
        profile_dir = getProfilePath(tempDriver)
        stopTempDriver(tempDriver)
        if profile_dir:
            ffOptions.add_argument(profile_dir)
        else:
            logging.error(f"无法获取profile")
            sys.exit(-1)
    from selenium import webdriver
    service = webdriver.firefox.service.Service(log_path = webdriver_log_path)
    driver = webdriver.Firefox(options = ffOptions, service = service)
    logging.info(driver.execute_script("return navigator.userAgent"))
    return driver