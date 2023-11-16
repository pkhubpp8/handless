import requests
import json
import sys
import os
import re

from init import config_init


def login(url, username, password):
    # 登录获取授权令牌
    login_url = url + '/api/v2/auth/login'
    data = {'username': username, 'password': password}
    response = requests.post(login_url, data=data)
    if response.ok == True:
        print("登录成功")
    else:
        print("登录失败，退出")
        sys.exit()

    sid_cookie = response.cookies['SID']
    return sid_cookie

def get_webui_version(url, sid_cookie):
    app_url = url + '/api/v2/app/webapiVersion'
    headers = {'Cookie': f'SID={sid_cookie}'}

    response = requests.get(app_url, headers=headers)
    if response.ok == True:
        print(f'webui version: {response.text}')
    else:
        print("获取版本失败，退出")
        sys.exit()

def get_torrents_info(url, sid_cookie, category = ''):
    # 获取种子信息
    if category:
        opt = f'?category={category}'
        torrent_url = url + '/api/v2/torrents/info' + opt
    else:
        torrent_url = url + '/api/v2/torrents/info'
    headers = {'Cookie': f'SID={sid_cookie}'}
    response = requests.get(torrent_url, headers=headers)
    if response.ok == True:
        torrents_info = response.json()
    else:
        print("获取种子信息失败，退出")
        sys.exit()
    return torrents_info

def check_if_file_is_seeding(file_path, torrents_info, is_sub = False):
    if not os.path.isdir(file_path):
        return
    subfiles = [f for f in os.listdir(file_path)]
    for file in subfiles:
        is_in = False
        for t in torrents_info:
            if t['name'] == file:
                is_in = True
                break
        if not is_in:
            check_if_file_is_seeding(file, True)
            if not is_sub:
                print(f'info: {file} not in')
            else:
                pass
                print(f'dbg: {file} not in')


def get_trackers_info(url, sid_cookie, torrent):
    get_trackers_info_url = url + '/api/v2/torrents/trackers'
    data = {'hash': torrent['hash']}
    headers = {'Cookie': f'SID={sid_cookie}'}
    response = requests.post(get_trackers_info_url, headers=headers, data=data)
    if response.ok == True:
        torrent_trackers_info = response.json()
        return torrent_trackers_info
    else:
        print(f"获取{torrent['hash']}，{torrent['name']}的tracker信息失败")
        return []


def check_tracker_msg(msg):
    if re.search('torrent not registered with this tracker', msg):
        return True
    return False


def delete_torrent_and_files(url, sid_cookie, h):
    get_trackers_info_url = url + '/api/v2/torrents/delete'
    data = {'hashes': h, 'deleteFiles': 'true'}
    headers = {'Cookie': f'SID={sid_cookie}'}
    response = requests.post(get_trackers_info_url, headers=headers, data=data)
    return response



directory_path = './'
result = config_init.get_config_for_qbwebui()
url = 'http://' + result['webui_ip'] + ':' + result['webui_port']
sid_cookie = login(url, result['username'], result['password'])
get_webui_version(url, sid_cookie)
all_torrents_info = get_torrents_info(url, sid_cookie)

# check_if_file_is_seeding(directory_path, all_torrents_info)

need_remove = []
for torrent in all_torrents_info:
    trackers_info = get_trackers_info(url, sid_cookie, torrent)
    for t in trackers_info:
        if re.search("^http.*", t['url']) and t['msg']:
            if check_tracker_msg(t['msg']):
                print(f"{torrent['hash']}, {torrent['name']}: {t}\n")
                need_remove.append(torrent)
                continue


if not need_remove:
    print("already clear!")
    sys.exit()

for h in need_remove:
    r = delete_torrent_and_files(url, sid_cookie, h['hash'])
    if r.ok == True:
        print(f"deleted {h['name']}")
    else:
        print(f"delete {h['name']} error")
        print(r)


need_remove = []
all_torrents_info = get_torrents_info(url, sid_cookie)

for torrent in all_torrents_info:
    trackers_info = get_trackers_info(url, sid_cookie, torrent)
    for t in trackers_info:
        if re.search("^http.*", t['url']) and t['msg']:
            if check_tracker_msg(t['msg']):
                print(f"{torrent['hash']}, {torrent['name']}: {t}\n")
                need_remove.append(torrent)
                continue

if not need_remove:
    print("clear!")
else:
    print("something wrong")
    for i in need_remove:
        print(i['name'])


'''
print(torrent_info[0]['name'])
sys.exit()
# 获取种子文件
contents_url = url + '/api/v2/torrents/files'

result = ""
for torrent in torrent_info:
    data = {'hash': torrent['hash']}
    response = requests.post(contents_url, headers=headers, data=data)
    torrentContents = response.json()
    for i in torrentContents:
        result = result + i['name'] + "\n"
    break

print(result)
'''