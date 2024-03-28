import logging
import re
import os

logger = logging.getLogger("default")

def setLogger(logger_):
    global logger
    logger = logger_

def checkEnv():
    exe = "chromedriver.exe"
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


def startTempDriver():
    if not checkEnv():
        return None
    import undetected_chromedriver as uc
    opts = uc.ChromeOptions()
    opts.headless = False
    opts.add_argument("user-data-dir=C:\\Path")
    driver = uc.Chrome(options=opts)

    driver.get("https://nowsecure.nl/")
    return driver

def stopTempDriver(driver = None):
    if driver:
        driver.quit()


def getDefaultProfilePath():
    return None


def getProfilePath(driver = None):
    if not driver:
        return None


def getUA(driver = None):
    if not driver:
        return ""
