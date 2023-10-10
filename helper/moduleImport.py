import json
import logging
import os
import importlib


logger = logging.getLogger('sign')
def load_target_json(dir, json_file):
    all = 1
    sites = None
    try:
        with open(dir + '/' + json_file, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        logger.info(f"{dir + '/' + json_file} 不存在。")
    except json.JSONDecodeError:
        logger.warning(f"{dir + '/' + json_file} 文件解析错误。请检查格式")
    else:
        logger.info("JSON数据加载成功。")
        return data


def import_modules(all = True, dir = "", sites = [], driver = None):
    signList = []

    if all == True:
        # 获取目录下所有.py文件的文件名
        py_files = [f[:-3] for f in os.listdir(dir) if f.endswith('.py')]
        # 动态导入.py文件
        for module_name in py_files:
            module = importlib.import_module(f'{dir}.{module_name}')
            signList.append(module.signClass(driver))
            logger.info(f'导入{dir}.{module_name}成功')
    else:
        unique_sign_sites = []
        seen_filenames = set()
        for site in sites:
            if "fileName" in site:
                filename = site["fileName"]
                if filename not in seen_filenames:
                    seen_filenames.add(filename)
                    unique_sign_sites.append(site)
                else:
                    logger.info(f"重复的fileName: {filename}, 忽略")
        for site in unique_sign_sites:
            module = importlib.import_module(f'{dir}.{site["fileName"][:-3]}')
            if site["url"]:
                signList.append(module.signClass(driver, site["url"]))
            else:
                signList.append(module.signClass(driver))
            logger.info(f'导入{site["fileName"][:-3]}成功')
    return signList