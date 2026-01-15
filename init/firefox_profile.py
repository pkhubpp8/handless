import logging
import re
import os
import sys
import time

logger = logging.getLogger("default")

def setLogger(logger_):
    global logger
    logger = logger_

def checkEnv():
    exe = "geckodriver.exe"
    # 获取系统的环境变量PATH，并将其拆分成一个列表
    path = os.environ.get("PATH")
    path_list = path.split(os.pathsep)

    # 遍历每个路径，检查是否存在可执行文件
    for folder in path_list:
        exe_path = os.path.join(folder, exe)
        if os.path.isfile(exe_path):
            logger.info(f"{exe}路径为{exe_path}")
            return exe_path
    logger.info(f"未找到 {exe}")
    return None


def startTempDriver(log_path: str):
    exe_path = checkEnv()
    if not exe_path:
        return None

    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options
    
    try:
        ffOptions = Options()
        ffOptions.add_argument("--no-remote")
        ffOptions.add_argument("--new-instance")
        
        if log_path:
            service = webdriver.firefox.service.Service(executable_path=exe_path, log_path=log_path)
        else:
            service = webdriver.firefox.service.Service(executable_path=exe_path)
        
        driver = webdriver.Firefox(options=ffOptions, service=service)
        driver.set_page_load_timeout(30)
        return driver
    except Exception as e:
        logger.error(f"启动临时驱动失败: {str(e)}")
        return None

def stopTempDriver(driver = None):
    if driver:
        driver.quit()


def getDefaultProfilePath():
    appdata_path = os.path.expandvars('%AppData%')
    file_path = os.path.join(appdata_path, r'Mozilla\Firefox\Profiles') # \xhvtyp4t.default-release-1583421326042')
    if os.path.exists(file_path):
        logger.info(f'路径 {file_path} 存在')
        subdirectories = [d for d in os.listdir(file_path) if os.path.isdir(os.path.join(file_path, d))]
        if len(subdirectories) == 1:
            profile_dir = os.path.join(appdata_path, r'Mozilla\Firefox\Profiles', subdirectories[0])
            return profile_dir
    return None


def getProfilePath(driver = None):
    if not driver:
        return None

    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        driver.get("about:profiles")
        time.sleep(2)
        
        # 等待配置文件信息加载
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_elements_located((By.CSS_SELECTOR, "th[data-l10n-id='profiles-rootdir']")))
        
        config_elements = driver.find_elements(By.CSS_SELECTOR, "th[data-l10n-id='profiles-is-default'] + td")
        root_dir_elements = driver.find_elements(By.CSS_SELECTOR, "th[data-l10n-id='profiles-rootdir'] + td")

        root_dir_element = None
        # 查找默认配置文件
        for i in range(len(config_elements)):
            if config_elements[i].text == "是":
                root_dir_element = root_dir_elements[i]
                break

        if root_dir_element:
            profile_path = root_dir_element.text.strip()
            logger.info(f"获取到profile路径: {profile_path}")
            return profile_path
        else:
            logger.warning("未找到默认配置文件")
            return None
    except Exception as e:
        logger.error(f"获取profile路径失败: {str(e)}")
        return None


def getUA(driver = None):
    if not driver:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0"
    return driver.execute_script("return navigator.userAgent")


def create_firefox_with_user_profile(webdriver_log_path: str):
    from selenium.webdriver.firefox.options import Options
    from selenium import webdriver
    
    exe_path = checkEnv()
    if not exe_path:
        logger.error("geckodriver not found")
        sys.exit(-1)
    
    ffOptions = Options()
    # 添加稳定运行参数
    ffOptions.add_argument("--no-remote")
    ffOptions.add_argument("--new-instance")
    ffOptions.add_argument("-profile")
    
    # 尝试获取默认profile
    profile_dir = getDefaultProfilePath()
    if not profile_dir:
        # 如果默认profile获取失败，尝试通过临时驱动获取
        logger.info("尝试通过临时驱动获取profile")
        tempDriver = startTempDriver(webdriver_log_path)
        if tempDriver:
            try:
                profile_dir = getProfilePath(tempDriver)
            finally:
                stopTempDriver(tempDriver)
                time.sleep(1)
        
        if not profile_dir:
            logger.error("无法获取profile，使用默认路径")
            profile_dir = os.path.expandvars(r'%AppData%\Mozilla\Firefox\Profiles')
    
    if profile_dir:
        ffOptions.add_argument(profile_dir)
    
    try:
        service = webdriver.firefox.service.Service(executable_path=exe_path, log_path=webdriver_log_path)
        driver = webdriver.Firefox(options=ffOptions, service=service)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        time.sleep(2)
        driver.maximize_window()
        ua = driver.execute_script("return navigator.userAgent")
        logger.info(f"Firefox启动成功，UA: {ua}")
        return driver
    except Exception as e:
        logger.error(f"创建Firefox驱动失败: {str(e)}")
        raise