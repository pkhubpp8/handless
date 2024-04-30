import os
import sys
import queue
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

def record_extra_info(sign_list: list):
    logger.info("start print extra info")
    if not sign_list:
        logger.info("空")
        return
    result_data = []
    for sign in sign_list:
        if sign.result:
            if sign.result.get('extra_info') or sign.result.get('new_message'):
                logger.info(f"{sign.indexUrl}; extra info: {sign.result.get('extra_info')}; new message: {sign.result.get('new_message')}")
            result_data.append(sign.result)

def get_sign_queue(driver, module_name):
    # 获取目录下.py文件的文件名
    target_directory = 'target'
    data = module_importer.load_target_json(target_directory, 'sign_site.json')
    if module_name != 'all':
        sign_queue = module_importer.import_modules(all = False, dir = target_directory, sites = module_name, driver = driver)
        return sign_queue
    else:
        if 'all' in data and data['all'] != True and "module_list" in data:
            sign_queue = module_importer.import_modules(all = False, dir = target_directory, sites = data['module_list'], driver = driver)
        else:
            logger.info("import所有模块")
            sign_queue = module_importer.import_modules(all = True, dir = target_directory, sites = [], driver = driver)
        return sign_queue

def do_sign(sign_queue: queue.Queue, force) -> list:
    succeedList = []
    failedList = []
    passList = []
    if force:
        data = []
    else:
        try:
            with open("log/result_data.json", "r", encoding='utf-8') as f:
            # 将文件内容转换为 JSON 对象列表
                data = json.load(f)
        except:
            data = []
    while not sign_queue.empty():
        sign = sign_queue.get()
        logger.info(f"开始{sign.indexUrl}")
        try:
            need_go_ahead = True
            for last in data:
                if last == None or sign.module_name != last['module_name']:
                    continue
                last_timestamp = last['date_and_time']
                last_sign_time = datetime.datetime.fromtimestamp(last_timestamp)
                current_datetime = datetime.datetime.now()
                if last_sign_time.day == current_datetime.day:
                    if last['sign_result'] == True:
                        need_go_ahead = False
                break
            if need_go_ahead == False:
                logger.info(f"{sign.module_name}今天已经签到成功了，无需再次签到")
                passList.append(sign)
                continue

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
                    # driver.save_screenshot('log/' + sign.module_name + '_snapshot.png')
                    # with open('log/' + sign.module_name + '_page.html', 'w', encoding='utf-8') as file:
                    #     file.write(driver.page_source)
            else:
                failedList.append(sign)
            if hasattr(sign, 'collect_info') and callable(getattr(sign, 'collect_info')):
                logger.info(sign.collect_info())
        except Exception as e:
            logger.error(f"something error: {e}")
            logger.warning(traceback.format_exc())
            failedList.append(sign)
        sign.exit()

    return [succeedList, failedList, passList]

def get_web_driver_and_logger() -> list:
    config_data = config_init.get_config_for_sign()
    log_path = config_data['log_path']
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    sign_log_path = os.path.join(log_path, 'sign')
    logger = myLogger.myLogger('sign', sign_log_path, False).getLogger()
    firefox_profile.setLogger(logger)
    module_importer.setLogger(logger)

    browser = config_data['browser']
    if browser == 'firefox':
        geckodriver_log_path = os.path.join(log_path, 'geckodriver.log')
        driver = firefox_profile.create_firefox_with_user_profile(geckodriver_log_path)
    elif browser == 'chrome':
        logger.error(f"当前不支持")
        sys.exit(-1)

    return [driver, logger]

def resign(fs) -> list:
    logger.info(f"失败{len(fs)}。尝试再次签到失败网站")
    sign_queue = queue.Queue()
    for f in fs:
        sign_queue.put(f)
    ss, fs, ps = do_sign(sign_queue)
    if len(ps) != 0:
        logger.warning(f"异常len of pass site: {len(ps)}")
    return [ss, fs]

def rewrite_result(sign_list: list):
    new_data = []
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

    logger.info(f"尝试写入打卡数据")
    for sign in sign_list:
        new_data.append(sign.result)

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

def main(force: bool, module_name: str):
    global logger
    driver, logger = get_web_driver_and_logger()
    '''
    WebDriverWait(driver, 10).until(
            lambda wd: driver.execute_script("return document.readyState") == 'complete',
            "Page taking too long to load"
        )
    '''
    if driver and logger:
        sign_queue = get_sign_queue(driver, module_name)

        logger.info(f"有{sign_queue.qsize()}个站需要签到")
        ss, fs, ps = do_sign(sign_queue, force)
        logger.info(f"忽略签到{len(ps)}个站")

        real_failed_list = []
        temp_pass = []
        for item in fs:
            if not_retry(item) == True:
                temp_pass.append(item)
            else:
                real_failed_list.append(item)
        fs = real_failed_list
        ps = ps + temp_pass

        ss2 = []
        fs2 = []
        if fs:
            time.sleep(5)
            ss2, fs2 = resign(fs)
            logger.info(f"重新签到, 成功{len(fs) - len(fs2)}/{len(fs)}")

        ss3 = []
        fs3 = []
        if fs2:
            time.sleep(5)
            ss3, fs3 = resign(fs2)
            logger.info(f"重新签到, 成功{len(fs2) - len(fs3)}/{len(fs2)}")

        logger.info("不重试签到 列表：")
        printList(temp_pass, True)

        logger.info("重试依然签到失败 列表：")
        printList(fs3, True)

        record_extra_info(ss + ss2 + ss3 + fs3)

        rewrite_result(ss + ss2 + ss3 + fs3)
        driver.quit()
    else:
        logger.error(f"webdriver 初始化失败")
        sys.exit(-1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='哈哈哈哈')

    # 添加命令行参数
    parser.add_argument('-f', '--force', action='store_true', help='强制重新运行，忽略已运行记录')
    parser.add_argument('module_name', nargs='?', default='all', help='指定模块名，默认all')

    # 解析命令行参数
    args = parser.parse_args()

    # 输出解析结果
    print('参数1:', args.force)
    print('参数2:', args.module_name)

    main(args.force, args.module_name)