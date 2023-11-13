import configparser
import os

# committed
default_config = 'config.ini'
# not committed due to sensitive data
local_config = 'local_config.ini'

def get_config_for_sign() -> dict:
    config = configparser.ConfigParser()
    if os.path.exists(local_config):
        config.read(local_config)
    else:
        config.read(default_config)

    browser = config.get('common', 'browser')
    log_path = config.get('common', 'log_path')
    result = {
        "browser": browser,
        "log_path": log_path
    }
    return result

def get_config_for_ddns() -> dict:
    config = configparser.ConfigParser()
    if os.path.exists(local_config):
        config.read(local_config)
    else:
        config.read(default_config)

    login_token = config.get('DNSPod', 'login_token')
    domain = config.get('DNSPod', 'domain')
    sub_domain = config.get('DNSPod', 'sub_domain')
    record_type = config.get('DNSPod', 'record_type')
    result = {
        "login_token": login_token,
        "domain": domain,
        "sub_domain": sub_domain,
        "record_type": record_type
    }
    return result

def get_config_for_qbwebui() -> dict:
    config = configparser.ConfigParser()
    if os.path.exists(local_config):
        config.read(local_config)
    else:
        config.read(default_config)

    webui_ip = config.get('QB', 'webui_ip')
    webui_port = config.get('QB', 'webui_port')
    username = config.get('QB', 'username')
    password = config.get('QB', 'password')
    result = {
        "webui_ip": webui_ip,
        "webui_port": webui_port,
        "username": username,
        "password": password
    }
    return result