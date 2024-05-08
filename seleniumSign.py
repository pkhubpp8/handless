import os
import sys
import traceback
import time
import json
import datetime
import argparse
from selenium.webdriver.common.by import By
# from selenium.webdriver.support.wait import WebDriverWait

from init import firefox_profile
from init import myLogger
from init import config_init
from helper import module_importer

def printList(sign_list: list, is_detail: bool):
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

def show_extra_info(sign_list: list):
    logger.info("start print extra info")
    if not sign_list:
        logger.info("空")
        return
    for sign in sign_list:
        if sign.result:
            if sign.result.get('extra_info') or sign.result.get('new_message'):
                logger.info(f"{sign.indexUrl}; extra info: {sign.result.get('extra_info')}; new message: {sign.result.get('new_message')}")

def get_sign_list(site_name: str):
    # 获取目录下.py文件的文件名
    target_directory = 'target'
    data = module_importer.load_target_json(target_directory, 'sign_site.json')
    if site_name != 'all':
        sign_list = module_importer.import_modules(all = False, dir = target_directory, sites = site_name)
        return sign_list
    else:
        if 'all' in data and data['all'] != True and "module_list" in data:
            sign_list = module_importer.import_modules(all = False, dir = target_directory, sites = data['module_list'])
        else:
            logger.info("import所有模块")
            sign_list = module_importer.import_modules(all = True, dir = target_directory, sites = [])
        return sign_list


def get_and_remove_ignore_list(sign_list: list, force) -> list:
    ignore_list = []

    if force:
        data = []
    else:
        try:
            with open("log/result_data.json", "r", encoding='utf-8') as f:
            # 将文件内容转换为 JSON 对象列表
                data = json.load(f)
        except:
            data = []
    for sign in sign_list[:]:
        logger.info(f"检查{sign.module_name}")
        need_sign = True
        for last in data:
            if last == None or sign.module_name != last['module_name']:
                continue
            last_timestamp = last['date_and_time']
            last_sign_time = datetime.datetime.fromtimestamp(last_timestamp)
            current_datetime = datetime.datetime.now()
            if last_sign_time.day == current_datetime.day:
                if last['sign_result'] == True:
                    need_sign = False
            break
        if need_sign == False:
            logger.info(f"{sign.module_name}今天已经签到成功了，无需再次签到")
            ignore_list.append(sign)
            sign_list.remove(sign)
    return ignore_list

def do_sign(sign_list: list, driver) -> list:
    succeed_list = []
    fail_list = []
    for sign in sign_list[:]:
        logger.info(f"开始{sign.indexUrl}, module name = {sign.module_name}")
        try:
            if not sign.get_driver():
                sign.set_driver(driver)
            if hasattr(sign, 'accessIndex') and callable(getattr(sign, 'accessIndex')):
                sign.accessIndex()
            if hasattr(sign, 'valid_access') and callable(getattr(sign, 'valid_access')):
                if not sign.valid_access():
                    if hasattr(sign, 'collect_info') and callable(getattr(sign, 'collect_info')):
                        logger.info(sign.collect_info())
                    fail_list.append(sign)
                    sign.exit()
                    sign_list.remove(sign)
                    continue
            if hasattr(sign, 'sign') and callable(getattr(sign, 'sign')):
                sign.sign()
            if hasattr(sign, 'msgCheck') and callable(getattr(sign, 'msgCheck')):
                sign.msgCheck()
            if hasattr(sign, 'validSign') and callable(getattr(sign, 'validSign')):
                if sign.validSign():
                    succeed_list.append(sign)
                else:
                    fail_list.append(sign)
                    # driver.save_screenshot('log/' + sign.module_name + '_snapshot.png')
                    # with open('log/' + sign.module_name + '_page.html', 'w', encoding='utf-8') as file:
                    #     file.write(driver.page_source)
            else:
                fail_list.append(sign)
            if hasattr(sign, 'collect_info') and callable(getattr(sign, 'collect_info')):
                logger.info(sign.collect_info())
        except Exception as e:
            logger.error(f"something error: {e}")
            logger.warning(traceback.format_exc())
            fail_list.append(sign)
        sign.exit()
        sign_list.remove(sign)

    return [succeed_list, fail_list]

def get_logger() -> list:
    config_data = config_init.get_config_for_sign()
    log_path = config_data['log_path']
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    sign_log_path = os.path.join(log_path, 'sign')
    logger = myLogger.myLogger('sign', sign_log_path, False).getLogger()
    firefox_profile.setLogger(logger)
    module_importer.setLogger(logger)

    return logger

def get_web_driver() -> list:
    config_data = config_init.get_config_for_sign()
    log_path = config_data['log_path']
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    browser = config_data['browser']
    if browser == 'firefox':
        geckodriver_log_path = os.path.join(log_path, 'geckodriver.log')
        driver = firefox_profile.create_firefox_with_user_profile(geckodriver_log_path)
    elif browser == 'chrome':
        logger.error(f"当前不支持")
        sys.exit(-1)

    return driver

def resign(fail_list, driver) -> list:
    logger.info(f"失败{len(fail_list)}。尝试再次签到失败网站")
    ss, fail_list = do_sign(fail_list, driver)
    return [ss, fail_list]

def rewrite_result(sign_list: list):
    new_data = []
    # load旧数据
    try:
        with open("log/result_data.json", "r", encoding='utf-8') as f:
        # 将文件内容转换为 JSON 对象列表
            data = json.load(f)
            for i in range(len(data)):
                if data[i] == None:
                    continue
                last_timestamp = data[i]['date_and_time']
                last_sign_time = datetime.datetime.fromtimestamp(last_timestamp)
                current_datetime = datetime.datetime.now()
                if last_sign_time.day != current_datetime.day:
                    continue
                if data[i]['sign_result'] == False:
                    continue
                new_data.append(data[i])
    except Exception as e:
        logger.warning(f"打开结果记录异常：{e}")
        logger.warning(f"错误堆栈信息：")
        logger.warning(traceback.format_exc())

    # 追加新数据
    logger.info(f"尝试写入{len(sign_list)}个打卡数据 ")
    for sign in sign_list:
        # 判断sign.result是否在new_data中已存在，已存在则修改
        for item in new_data:
            if "module_name" in item and "module_name" in sign.result and item["module_name"] == sign.result["module_name"]:
                # 如果找到匹配项，则修改数据
                item.update(sign.result)
                break
        else:
            # 如果没找到匹配项，则追加数据
            new_data.append(sign.result)

    logger.info(f"决定写入{len(new_data)}个打卡数据 ")
    # logger.info(new_data)
    with open("log/result_data.json", "w", encoding='utf-8') as f:
        # 将 JSON 对象列表写入文件
        json.dump(new_data, f, ensure_ascii=False, indent=4)

def not_retry(sign):
    if sign.result:
        if sign.result.get('access_result_info'):
            if "未登录" in sign.result.get('access_result_info'):
                logger.info(f"{sign.module_name} access 未登录, not retry")
                return True
            if "标题异常" in sign.result.get('access_result_info'):
                if "502" in sign.result.get('access_result_info') or "504" in sign.result.get('access_result_info'):
                    return False
                # 之后改成"502: Bad gateway", "504: Gateway time-out" 可以 retry
                logger.info(f"{sign.module_name} access 标题异常, not retry")
                return True
        if sign.result.get('sign_result_info'):
            if "标题异常" in sign.result.get('sign_result_info'):
                if "502" in sign.result.get('sign_result_info') or "504" in sign.result.get('sign_result_info'):
                    return False
                logger.info(f"{sign.module_name} sign 标题异常, not retry")
                return True
            elif "8点不到，无法签到" in sign.result.get('sign_result_info'):
                logger.info(f"{sign.module_name} 8点不到, not retry")
                return True
            elif "未签到。活跃度不够" in sign.result.get('sign_result_info'):
                logger.info(f"{sign.module_name} 活跃度不够, not retry")
                return True
    return False

def main(force: bool, site_name: str):
    '''
    WebDriverWait(driver, 10).until(
            lambda wd: driver.execute_script("return document.readyState") == 'complete',
            "Page taking too long to load"
        )
    '''
    if logger:
        sign_list = get_sign_list(site_name)
        target_size = len(sign_list);
        logger.info(f"有{target_size}个站需要签到")
        ignore_list = get_and_remove_ignore_list(sign_list, force)
        logger.info(f"有{len(ignore_list)}个站忽略签到")
        if len(ignore_list) == target_size:
            logger.info(f"没有站需要签到，等待30秒结束") # 防止运行过快
            time.sleep(30)
            return

        driver = get_web_driver()
        if driver:
            succeed_list, fail_list = do_sign(sign_list, driver)
            logger.info(f"签到成功{len(succeed_list)}个站，失败{len(fail_list)}个站")

            real_failed_list = []
            temp_pass = []
            for item in fail_list:
                if not_retry(item) == True:
                    temp_pass.append(item)
                else:
                    real_failed_list.append(item)
            fail_list = real_failed_list

            succeed_list2 = []
            fail_list2 = []
            if fail_list:
                time.sleep(5)
                succeed_list2, fail_list2 = resign(fail_list, driver)
                logger.info(f"重新签到, 成功{len(succeed_list2)}/失败{len(fail_list2)}")

            succeed_list3 = []
            fail_list3 = []
            if fail_list2:
                time.sleep(5)
                succeed_list3, fail_list3 = resign(fail_list2, driver)
                logger.info(f"重新签到, 成功{len(succeed_list3)}/失败{len(fail_list3)}")

            logger.info("不重试签到 列表：")
            printList(temp_pass, True)

            logger.info("重试依然签到失败 列表：")
            printList(fail_list3, True)

            show_extra_info(succeed_list + succeed_list2 + succeed_list3 + fail_list3)

            rewrite_result(succeed_list + succeed_list2 + succeed_list3 + fail_list3)
            driver.quit()
            driver = None
    else:
        logger.error(f"初始化失败")
        sys.exit(-1)


if __name__ == "__main__":
    global logger
    logger = get_logger()
    parser = argparse.ArgumentParser(description='哈哈哈哈')

    # 添加命令行参数
    parser.add_argument('-f', '--force', action='store_true', help='强制重新运行，忽略已运行记录')
    parser.add_argument('-o', '--once', action='store_true', help='运行一次')
    parser.add_argument('site_name', nargs='?', default='all', help='指定站点名，默认all')

    # 解析命令行参数
    args = parser.parse_args()

    # 输出解析结果
    logger.info(f'参数 force: {args.force}')
    logger.info(f'参数 once: {args.once}')
    logger.info(f'参数 site_name: {args.site_name}')
    if args.once == True:
        main(args.force, args.site_name)
    else:
        logger.info(f'开始等待')
        while True:
            now = datetime.datetime.now()
            today = datetime.date.today()
            current_hour = now.hour
            current_minute = now.minute
            if current_hour == 1 and current_minute == 0:
                logger.info(f'现在是{today.day}日{current_hour}时{current_minute}分')
                main(args.force, args.site_name)
            else:
                time.sleep(50)