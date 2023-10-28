import configparser

def get_config_for_sign() -> dict:
    config = configparser.ConfigParser()
    config.read('config.ini')
    browser = config.get('common', 'browser')
    log_path = config.get('common', 'log_path')
    result = {
        "browser": browser,
        "log_path": log_path
    }
    return result

def get_config_for_ddns() -> dict:
    config = configparser.ConfigParser()
    config.read('config.ini')
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