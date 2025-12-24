import os
import sys
import traceback
import time
import json
import datetime
import argparse
import atexit
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from init import firefox_profile
from init import myLogger
from init import config_init
from helper import module_importer

RESULT_VERSION = 1.0

@dataclass
class SignResult:
    module_name: str
    site_name: str
    timestamp: int
    timestring: str
    access_result_info: Optional[str] = None
    sign_result_info: Optional[str] = None
    extra_info: Optional[str] = None
    new_message: Optional[str] = None
    sign_result: bool = False

class SignLogger:
    def __init__(self, logger):
        self.logger = logger

    def print_list(self, sign_list: List[Any], is_detail: bool) -> None:
        """打印签到列表信息

        Args:
            sign_list: 签到站点列表
            is_detail: 是否显示详细信息
        """
        if not sign_list:
            self.logger.info("空")
            return
            
        for sign in sign_list:
            if is_detail and hasattr(sign, 'result'):
                result = getattr(sign, 'result')
                if result:
                    info = result.get('access_result_info') or result.get('sign_result_info') or 'no result'
                    self.logger.info(f"{sign.indexUrl}: {info}")
                else:
                    self.logger.info(f"{sign.indexUrl}: no result")
            else:
                self.logger.info(f"{sign.indexUrl}")

    def show_extra_info(self, sign_list: List[Any]) -> None:
        """显示额外信息

        Args:
            sign_list: 签到站点列表
        """
        self.logger.info("start print extra info")
        if not sign_list:
            self.logger.info("空")
            return
            
        for sign in sign_list:
            if hasattr(sign, 'result') and sign.result:
                extra = sign.result.get('extra_info')
                msg = sign.result.get('new_message')
                if extra or msg:
                    self.logger.info(f"{sign.indexUrl}; extra info: {extra}; new message: {msg}")

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

    data = []
    if not force:
        try:
            with open("log/result_data.json", "r", encoding='utf-8') as f:
                result_data = json.load(f)
                if isinstance(result_data, dict) and result_data.get('version') == RESULT_VERSION:
                    data = result_data['result']
                else:
                    logger.info(f"reult版本已过时，丢弃")
        except:
            data = []
    for sign in sign_list[:]:
        logger.info(f"检查{sign.module_name}")
        need_sign = True
        for last in data:
            if last == None or sign.module_name != last['module_name']:
                continue
            last_timestamp = last['timestamp']
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

class SignResultManager:
    def __init__(self, logger):
        self.logger = logger
        self.result_file = "log/result_data.json"

    def load_previous_results(self) -> Dict:
        """加载之前的签到结果"""
        try:
            with open(self.result_file, "r", encoding='utf-8') as f:
                result_data = json.load(f)
                if isinstance(result_data, dict) and result_data.get('version') == RESULT_VERSION:
                    return result_data
                self.logger.info("result版本已过时，丢弃")
        except Exception as e:
            self.logger.warning(f"打开结果记录异常：{e}")
            self.logger.warning(traceback.format_exc())
        return {'version': RESULT_VERSION, 'result': []}

    def is_result_valid(self, result: Dict) -> bool:
        """检查结果是否有效"""
        if not result:
            return False
        last_time = datetime.datetime.fromtimestamp(result['timestamp'])
        current_time = datetime.datetime.now()
        return (last_time.day == current_time.day and 
                result.get('sign_result', False))

    def update_result(self, sign_list: List[Any]) -> None:
        """更新签到结果

        Args:
            sign_list: 签到站点列表
        """
        new_data = self.load_previous_results()
        valid_results = [r for r in new_data['result'] if self.is_result_valid(r)]
        new_data['result'] = valid_results

        self.logger.info(f"尝试写入{len(sign_list)}个打卡数据")
        
        for sign in sign_list:
            result = None
            if hasattr(sign, 'result'):
                result = sign.result
            else:
                t = time.time()
                result = SignResult(
                    module_name=sign.module_name,
                    site_name=sign.site_name,
                    timestamp=int(t),
                    timestring=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
                ).__dict__

            # Update existing or append new
            for item in new_data['result']:
                if item.get("module_name") == sign.module_name:
                    if result:
                        item.update(result)
                    break
            else:
                if result:
                    self.logger.info(f"追加{sign.site_name}新数据")
                    new_data['result'].append(result)

        self.logger.info(f"写入{len(new_data['result'])}个打卡数据")
        with open(self.result_file, "w", encoding='utf-8') as f:
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
            elif "未签到。需要使用webbrowser签到" in sign.result.get('sign_result_info'):
                logger.info(f"{sign.module_name} 需要使用webbrowser签到, not retry")
                return True
    return False

class SignManager:
    def __init__(self, logger):
        self.logger = logger
        self.sign_logger = SignLogger(logger)
        self.result_manager = SignResultManager(logger)
        self.driver = None
        
    def initialize_driver(self):
        """初始化WebDriver"""
        if not self.driver or (self.driver.service.process.poll() == 1):
            self.driver = get_web_driver()
        return bool(self.driver)

    def shutdown(self) -> None:
        """安全关闭 WebDriver（如果存在）。

        这个方法在程序退出或接收到中断时应被调用，确保浏览器和 geckodriver 进程被正确终止。
        """
        try:
            if self.driver:
                try:
                    self.logger.info("Shutting down webdriver...")
                    self.driver.quit()
                except Exception:
                    # 不要抛出异常，记录即可
                    self.logger.warning("Exception while quitting webdriver", exc_info=True)
                finally:
                    self.driver = None
        except Exception:
            self.logger.warning("Unexpected exception during SignManager.shutdown", exc_info=True)
        
    def handle_webbrowser_signs(self, temp_pass: List[Any]):
        """处理需要使用webbrowser的签到"""
        for sign in temp_pass:
            if not (sign.result and "需要使用webbrowser签到" in sign.result.get('sign_result_info', '')):
                continue
                
            import re
            match = re.search(r'需要使用webbrowser签到(http.*)', sign.result.get('sign_result_info'))
            if match:
                if self.driver:
                    self.driver.quit()
                    self.driver = None
                    
                webbrowser.open(match.group(1))
                time.sleep(15)
                os.system("taskkill /im firefox.exe /f")
                
    def main(self, force: bool, site_name: str):
        """主要签到流程
        
        Args:
            force: 是否强制签到
            site_name: 站点名称
        """
        if not self.logger:
            self.logger.error("初始化失败")
            sys.exit(-1)
            
        sign_list = get_sign_list(site_name)
        target_size = len(sign_list)
        self.logger.info(f"有{target_size}个站需要签到")
        
        ignore_list = get_and_remove_ignore_list(sign_list, force)
        self.logger.info(f"有{len(ignore_list)}个站忽略签到")
        
        if len(ignore_list) == target_size:
            self.logger.info("没有站需要签到，等待30秒结束")
            time.sleep(30)
            return
            
        if not self.initialize_driver():
            self.logger.error("driver未创建")
            return
            
        # 首次签到
        success_signs, failed_signs = do_sign(sign_list, self.driver)
        self.logger.info(f"签到成功{len(success_signs)}个站，失败{len(failed_signs)}个站")

        # 分类失败原因
        retry_failed_signs = []  # 需要重试的失败项
        skipped_signs = []       # 不重试的失败项（如未登录、活跃度不够等）
        for sign in failed_signs:
            if not_retry(sign):
                skipped_signs.append(sign)
            else:
                retry_failed_signs.append(sign)

        # 第一次重试
        retry1_success_signs, retry1_failed_signs = [], []
        if retry_failed_signs:
            time.sleep(5)
            retry1_success_signs, retry1_failed_signs = resign(retry_failed_signs, self.driver)
            self.logger.info(f"重试1: 成功{len(retry1_success_signs)}/失败{len(retry1_failed_signs)}")

        # 第二次重试
        retry2_success_signs, retry2_failed_signs = [], []
        if retry1_failed_signs:
            time.sleep(5)
            retry2_success_signs, retry2_failed_signs = resign(retry1_failed_signs, self.driver)
            self.logger.info(f"重试2: 成功{len(retry2_success_signs)}/失败{len(retry2_failed_signs)}")

        self.logger.info("不重试签到 列表：")
        self.sign_logger.print_list(skipped_signs, True)

        self.logger.info("重试依然签到失败 列表：")
        self.sign_logger.print_list(retry2_failed_signs, True)

        self.handle_webbrowser_signs(skipped_signs)

        if not self.driver:
            self.initialize_driver()

        # 汇总所有结果
        all_results = success_signs + retry1_success_signs + retry2_success_signs + retry2_failed_signs
        self.sign_logger.show_extra_info(all_results)
        self.result_manager.update_result(all_results)


def run_scheduler(sign_manager: SignManager, args: argparse.Namespace) -> None:
    """运行签到调度器
    
    Args:
        sign_manager: 签到管理器实例
        args: 命令行参数
    """
    if args.once:
        sign_manager.main(args.force, args.site_name)
        return

    logger.info('开始等待')
    while True:
        now = datetime.datetime.now()
        if now.hour == 4 and now.minute == 0:
            logger.info(f'现在是{now.day}日{now.hour}时{now.minute}分')
            sign_manager.main(args.force, args.site_name)
            logger.info('开始等待')
        else:
            time.sleep(50)

if __name__ == "__main__":
    import webbrowser
    
    logger = get_logger()
    parser = argparse.ArgumentParser(description='自动化签到工具')

    parser.add_argument('-f', '--force', action='store_true', help='强制重新运行，忽略已运行记录')
    parser.add_argument('-o', '--once', action='store_true', help='立即运行一次')
    parser.add_argument('site_name', nargs='?', default='all', help='指定站点名，默认all')

    args = parser.parse_args()

    logger.info(f'参数 force: {args.force}')
    logger.info(f'参数 once: {args.once}')
    logger.info(f'参数 site_name: {args.site_name}')
    logger.info('开始执行签到任务')

    sign_manager = SignManager(logger)

    # Ensure webdriver is closed on normal exit
    atexit.register(sign_manager.shutdown)

    try:
        run_scheduler(sign_manager, args)
    except KeyboardInterrupt:
        logger.info('收到键盘中断，准备退出')
    except Exception as e:
        logger.error(f'运行时发生未捕获异常: {e}')
        logger.warning(traceback.format_exc())
    finally:
        # 确保在任意退出路径都调用 shutdown
        try:
            sign_manager.shutdown()
        except Exception:
            logger.warning('shutdown 时发生异常', exc_info=True)