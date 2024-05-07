import json
import logging
import os
import importlib


logger = logging.getLogger("default")

def setLogger(logger_):
    global logger
    logger = logger_

logger = logging.getLogger('sign')
def load_target_json(dir, json_file):
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


def import_modules(all = True, dir = "", sites = []) -> list:
    sign_list = []
    if all == True:
        # 获取目录下所有.py文件的文件名
        py_files = [f[:-3] for f in os.listdir(dir) if f.endswith('.py')]
        # 动态导入.py文件
        for module_name in py_files:
            if module_name == '_BASE':
                continue
            elif 'Sign' in module_name:
                module = importlib.import_module(f'{dir}.{module_name}')
                sign_list.append(module.signClass())
                logger.info(f'导入{dir}.{module_name}成功')
    else:
        unique_sign_sites = []
        seen_module_names = set()
        if isinstance(sites, str):
            logger.info(f'指定运行{sites}')
            module = importlib.import_module(f'{dir}.{sites}Sign')
            sign_list.append(module.signClass())
            logger.info(f'导入{sites}成功')
        else:
            for site in sites:
                if "module_name" in site:
                    module_name = site["module_name"]
                    if module_name not in seen_module_names:
                        seen_module_names.add(module_name)
                        unique_sign_sites.append(site)
                    else:
                        logger.info(f"重复的module: {module_name}, 忽略")
            for site in unique_sign_sites:
                module = importlib.import_module(f'{dir}.{site["module_name"]}')
                if site["url"]:
                    sign_list.append(module.signClass(site["url"]))
                else:
                    sign_list.append(module.signClass())
                logger.info(f'导入{site["module_name"]}成功')
    return sign_list