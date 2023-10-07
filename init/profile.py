import logging
import re
import os

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


def getProfilePath(log_path=""):
    if not checkEnv():
        return None
        
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    if log_path:
        service = webdriver.firefox.service.Service(log_path=log_path)
        driver = webdriver.Firefox(service=service)
    else:
        driver = webdriver.Firefox()
    driver.get("about:profiles")
    # 使用CSS选择器定位所有 "默认配置文件" 为 "是" 的元素以及对应的根目录元素
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


    profile_path = re.sub(re.escape(open_folder_button.text), '', root_dir_element.text)

    driver.quit()
    return profile_path