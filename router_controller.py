import time
import os
import sys
from init import config_init
from init import myLogger

import paramiko

def ssh_command(hostname, port, username, password, command, logger):
    try:
        # 创建SSH客户端对象
        client = paramiko.SSHClient()

        # 设置自动添加主机密钥
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 连接到远程主机
        client.connect(hostname, username=username, password=password, port=port)

        # 执行命令
        stdin, stdout, stderr = client.exec_command(command)

        # 读取命令输出
        output = stdout.read().decode()

        # 打印输出
        print(output)

        # 关闭连接
        client.close()

    except paramiko.AuthenticationException:
        logger.error("Authentication failed, please verify your credentials.")
        sys.exit(1)
    except paramiko.SSHException as ssh_ex:
        logger.warning(f"SSH error: {ssh_ex}")
    except Exception as ex:
        logger.warning(f"Error: {ex}")


logPath = 'log/'
if not os.path.exists(logPath):
    # 如果路径不存在，使用os.makedirs()函数创建它
    os.makedirs(logPath)
ddns_log_path = logPath + 'router'
logger = myLogger.myLogger('router', ddns_log_path).getLogger()
config_data = config_init.get_config_for_router()

hostname = config_data['hostname']
ssh_port = config_data['ssh_port']
username = config_data['username']
password = config_data['password']

command = "ls /tmp -l"

# 调用函数执行SSH命令
ssh_command(hostname, ssh_port, username, password, command, logger)