import time
import os
import sys
from init import config_init
from init import myLogger
import paramiko

_logger = None
_client = None

def get_ssh_client(hostname, port, username, password):
    try:
        # 创建SSH客户端对象
        client = paramiko.SSHClient()

        # 设置自动添加主机密钥
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 连接到远程主机
        client.connect(hostname, username=username, password=password, port=port)

        return client

    except paramiko.AuthenticationException:
        _logger.error("Authentication failed, please verify your credentials.")
        sys.exit(1)
    except paramiko.SSHException as ssh_ex:
        _logger.warning(f"SSH error: {ssh_ex}")
    except Exception as ex:
        _logger.warning(f"Error: {ex}")
    
    return None

def close_connection():
    if _client:
        # 关闭连接
        _client.close()
        _client = None


def init():
    if not _logger:
        logPath = 'log/'
        if not os.path.exists(logPath):
            # 如果路径不存在，使用os.makedirs()函数创建它
            os.makedirs(logPath)
        router_ctrl_log_path = logPath + 'router'
        _logger = myLogger.myLogger('router', router_ctrl_log_path).getLogger()
    
    if not _client:
        config_data = config_init.get_config_for_router()

        hostname = config_data['hostname']
        ssh_port = config_data['ssh_port']
        username = config_data['username']
        password = config_data['password']
        _client = get_ssh_client(hostname, ssh_port, username, password)

def destroy():
    close_connection()
    _logger = None

def ssh_command(command):
    if _client:
        # 执行命令
        stdin, stdout, stderr = _client.exec_command(command)

        # 读取命令输出
        output = stdout.read().decode()

        # 打印输出
        return output
    else:
        _logger.info("client not exist. Do nothing")
        return None

def execute_reset():
    # command = "ls /tmp -l"
    command = "reset"

    # 调用函数执行SSH命令
    _logger.info(ssh_command(command))