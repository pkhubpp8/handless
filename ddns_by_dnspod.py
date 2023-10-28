import sys
import requests
import json
import time
import traceback
import os
from helper import getipv4
from helper import test_connection
from init import config_init
from init import myLogger

logPath = 'log/'
if not os.path.exists(logPath):
    # 如果路径不存在，使用os.makedirs()函数创建它
    os.makedirs(logPath)
ddns_log_path = logPath + 'ddns'
logger = myLogger.myLogger('ddns', ddns_log_path).getLogger()


def get_record_list(config_data: dict):
    url = 'https://dnsapi.cn/Record.List'
    # 填写登录信息和域名信息
    params = {
        'login_token': config_data['login_token'],
        'format': 'json',
        'domain': config_data['domain'],
        'sub_domain': config_data['sub_domain'],
        'record_type': config_data['record_type'],
    }

    # 获取 record_id、value 和 ip 地址
    response = requests.post(url, data=params).text
    result = json.loads(response)
    return result

def modify_record(config_data: dict, record_id, ip, record_line_id):
    # 调用 Dnspod API 修改记录值
    url = 'https://dnsapi.cn/Record.Modify'
    data = {
        'login_token': config_data['login_token'],
        'domain': config_data['domain'],
        'record_id': record_id,
        'sub_domain': config_data['sub_domain'],
        'value': ip,
        'record_type': config_data['record_type'],
        'record_line_id': record_line_id,
    }
    response = requests.post(url, data=data).text
    result = json.loads(response)
    return result

def config_data_check(config_data: dict):
    keys_to_check = ["login_token", "domain", "sub_domain", "record_type"]
    for key in keys_to_check:
        if (key not in config_data) or (not config_data[key]):
            logger.error(f"缺少{key}，程序退出")
            sys.exit(1)

def test_http_until_connection_ok():
    while True:
        if test_connection.test_http_connection():
            break
        else:
            logger.info("网络连接异常，20s后重试")
            time.sleep(20)

if __name__ == "__main__":
    config_data = config_init.get_config_for_ddns()
    config_data_check(config_data)
    test_http_until_connection_ok()

    logger.info("start DDNS by DNSPod")
    while True:
        try:
            result = get_record_list(config_data)
            record_id = result['records'][0]['id']
            last_ip = result['records'][0]['value']
            record_line_id = result['records'][0]['line_id']

            current_ip = (
                getipv4.get_ipv4_icanhazip() or
                getipv4.get_ipv4_ipify() or
                getipv4.get_ipv4_wtfismyip() or
                getipv4.get_ipv4_ipv4icanhazip() or
                getipv4.get_ipv4_ip4onlyme()
            )
            if not current_ip:
                logger.warning("can't get ip by getipv4 module, sleep 1 min")
                time.sleep(60)
                continue

            if current_ip == last_ip:
                time.sleep(600)
                continue

            logger.info(f'My new IP: {current_ip}, last ip {last_ip}, start modify')

            result = modify_record(config_data, record_id, current_ip, record_line_id)
            # 输出修改结果
            if result['status']['code'] == '1':
                logger.info(f"{config_data['sub_domain']}.{config_data['domain']} 已更新为 {current_ip}。")
                time.sleep(600)
                continue
            else:
                logger.warning(f"modify error: {result}")
                time.sleep(60)
                continue
        except Exception as e:
            logger.warning(f"unknown error: {e}")
            logger.warning(traceback.format_exc())
            time.sleep(60)