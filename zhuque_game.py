import requests
import brotli
import json
import time
import sys
import os
import zlib
import datetime
from bs4 import BeautifulSoup
from init import profile
from init import sql
from init import myLogger

class GAME():
    def __init__(self):
        self.ua = None
        self.csrf = None
        self.cookie = None
    def setUA(self, ua):
        self.ua = ua
    def getUA(self):
        return self.ua
    def setCSRF(self, csrf):
        self.csrf = csrf
    def getCSRF(self):
        return self.csrf
    def setCookie(self, cookie):
        self.cookie = cookie
    def getCookie(self):
        return self.cookie
    def setInfo(self, day, costOfDay, salaryOfDay):
        self.day = day
        self.costOfDay = costOfDay
        self.salaryOfDay = salaryOfDay
    def getSalary(self):
        return self.salaryOfDay
    def getCost(self):
        return self.costOfDay
    def getDay(self):
        return self.day

logPath = 'log/'
if not os.path.exists(logPath):
    # 如果路径不存在，使用os.makedirs()函数创建它
    os.makedirs(logPath)
game_log_path = logPath + 'game.log'
geckodriver_log_path = logPath + 'geckodriver.log'
logger = myLogger.myLogger('game', game_log_path).getLogger()

def initGame(game: GAME):
    if not game:
        logger.error("game初始化异常")
        return
    currentUA = None
    tempDriver = None
    profile_dir = profile.getDefaultProfilePath()
    if profile_dir:
        localSql = sql.Sql(profile_dir)
    else:
        tempDriver = profile.startTempDriver(geckodriver_log_path)
        profile_dir = profile.getProfilePath(tempDriver)
        currentUA = profile.getUA(tempDriver)
        profile.stopTempDriver(tempDriver)
        localSql = sql.Sql(profile_dir)

    if not currentUA:
        currentUA = profile.getUA(tempDriver)
    sid = localSql.getCookieByUrlAndName('zhuque.in', 'connect.sid')

    game.setCookie(f"connect.sid={sid}")
    game.setUA(currentUA)

    csrf = getCsrfToken(ua = game.getUA(), cookie = game.getCookie())
    game.setCSRF(csrf = csrf)

    game.setInfo(datetime.date.today().day, 0, 0)


def sleep_to_target_with_logging(game: GAME, target_time_stamp, interval=5*60, log_interval=30*60):
    first_log = True
    last_log_time = time.time()  # 记录上次记录日志的时间
    while True:
        updateCostAndSalaryPerDay(0, 0, game)
        current_time = int(time.time())
        if current_time >= target_time_stamp:
            logger.info("sleep 到期，退出等待")
            break
        else:
            remainHours = (target_time_stamp - current_time) // 3600
            remainMinutes = ((target_time_stamp - current_time) % 3600) // 60   # 60秒为1分钟
            remainSeconds = (target_time_stamp - current_time) % 60
            sleep_duration = min(interval, target_time_stamp - current_time)
            if first_log or (current_time - last_log_time >= log_interval):
                logger.info(f"等待{sleep_duration // 60:02}分{sleep_duration % 60:02}秒，还剩{remainHours:02}:{remainMinutes:02}:{remainSeconds:02}...")
                if first_log:
                    first_log = False
                last_log_time = current_time
            time.sleep(sleep_duration)


def sleep_with_logging(total_sleep_time, interval=30*60):
    remaining_sleep_time = total_sleep_time
    while remaining_sleep_time > 0:
        remainHours = remaining_sleep_time // 3600            # 3600秒为1小时
        remainMinutes = (remaining_sleep_time % 3600) // 60   # 60秒为1分钟
        remainSeconds = remaining_sleep_time % 60
        sleep_duration = min(interval, remaining_sleep_time)
        logger.info(f"等待{sleep_duration // 60:02}分{sleep_duration % 60:02}秒，还剩{remainHours:02}:{remainMinutes:02}:{remainSeconds:02}...")
        time.sleep(sleep_duration)
        remaining_sleep_time -= sleep_duration



def getData(funcName, response):
    if response.status_code == 200:
        try:
            content = response.content
            encoding = response.headers.get("content-encoding", "")
            if "br" in encoding:
                try:
                    content = brotli.decompress(content)
                except Exception as e:
                    logger.debug("%s br 解压缩失败: %s", funcName, e)
            elif "gzip" in encoding:
                try:
                    content = zlib.decompress(content, zlib.MAX_WBITS | 16)
                except Exception as e:
                    logger.debug("%s gzip 解压缩失败: %s", funcName, e)
            elif "deflate" in encoding:
                try:
                    content = zlib.decompress(content, -zlib.MAX_WBITS)
                except Exception as e:
                    logger.debug("%s deflate 解压缩失败: %s", funcName, e)
            logger.info(f"{funcName} 请求成功")
            data = json.loads(content.decode("utf-8"))
            return data
        except json.JSONDecodeError as e:
            logger.error("%s 无法解析JSON: %s", funcName, e)
    elif response.status_code == 401:
        logger.error(f"{funcName} 鉴权无效 {response.status_code}。进程退出。请重新登录并更新cookie")
        sys.exit(-1)
    else:
        logger.error(f"{funcName} 请求失败，状态码: {response.status_code}")


def getCsrfToken(ua: str, cookie: str):
    url = "https://zhuque.in/index"
    headers = {
        "Host": "zhuque.in",
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.7,en;q=0.5,zh-TW;q=0.3,zh-HK;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "TE": "trailers",
    }
    response = requests.get(url, headers=headers)
    content = getData(getCsrfToken.__name__, response)
    indexSoup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')
    csrfToken = indexSoup.find('meta', {'name':'x-csrf-token'})
    return csrfToken.attrs['content']


def getAllCharacters(ua: str, cookie: str, csrf: str):
    url = "https://zhuque.in/api/gaming/listGenshinCharacter"
    headers = {
        "Host": "zhuque.in",
        "User-Agent": ua,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.7,en;q=0.5,zh-TW;q=0.3,zh-HK;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "x-csrf-token": csrf,
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "https://zhuque.in/gaming/genshin/character/list",
        "Cookie": cookie,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }
    response = requests.get(url, headers=headers)

    return getData(getAllCharacters.__name__, response)


def doLvlUp(character: dict, ua: str, cookie: str, csrf: str):
    commonHeaders = {
        "Host": "zhuque.in",
        "User-Agent": ua,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.7,en;q=0.5,zh-TW;q=0.3,zh-HK;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "x-csrf-token": csrf,
        "Content-Length": "27",
        "Origin": "https://zhuque.in",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "https://zhuque.in/gaming/genshin/character/list",
        "Cookie": cookie,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    logger.info(f"尝试升级id: {character['id']}, key name: {character['key']}")
    data = {
        "id": character['id'],
        "resetModal": False
    }

    # 发送POST请求
    url = "https://zhuque.in/api/gaming/trainGenshinCharacter"
    response = requests.post(url, json=data, headers=commonHeaders)
    return getData(doLvlUp.__name__, response)


def releaseAll(ua: str, cookie: str, csrf: str):
    data = {
        "all": 1,
        "resetModal": True
    }
    commonHeaders = {
        "Host": "zhuque.in",
        "User-Agent": ua,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.7,en;q=0.5,zh-TW;q=0.3,zh-HK;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "x-csrf-token": csrf,
        "Content-Length": "27",
        "Origin": "https://zhuque.in",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "https://zhuque.in/gaming/genshin/character/list",
        "Cookie": cookie,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    url = "https://zhuque.in/api/gaming/fireGenshinCharacterMagic"
    response = requests.post(url, json=data, headers=commonHeaders)

    return getData(releaseAll.__name__, response)


def getNextTimeStamp(characterList):
    if len(characterList) > 0:
        timeStamp = characterList[0]['info']['next_time']
        id = characterList[0]['id']
        for i in characterList:
            if (i['magic'] == 1 or i['magic'] == 2) and i['info']['next_time'] < timeStamp:
                timeStamp = i['info']['next_time']
                id = i['id']
        return id
    else:
        return 0


def checkIfAllCharactersNeedLvlUpAndDoLvlUp(characterList, game: GAME):
    isLvlUp = False
    for i in characterList:
        if checkIfCharacterNeedLvlUp(i):
            isLvlUp = True
            doLvlUp(i, game.getUA(), game.getCookie(), game.getCSRF())
            time.sleep(5)  # 等待5秒钟
    if isLvlUp == False:
        logger.info("无需升级")
    return isLvlUp


def checkIfCharacterNeedLvlUp(character):
    '''
        magic == 1, 获得灵石
        magic == 2, 获得持续时间为 1 天的灵石加成
        magic == 3, 绑定的角色在释放技能时有几率免除冷却时间
        magic == 4, 绑定的角色在释放技能时有几率获得双倍灵石
    '''
    if character['magic'] == 1 and character['info']['ratio'] == 0.5 and character['info']['level'] < 70:
        return True
    return False


def updateCostAndSalaryPerDay(cost, salary, game: GAME):
    if game.getDay() == datetime.date.today().day:
        game.setInfo(game.getDay(), game.getCost() + int(cost), game.getSalary() + int(salary))
    else:
        logger.info(f"日期变更。现在是{game.getDay()}日，昨天共消费{game.getCost()}灵石，获取{game.getSalary()}灵石")
        game.setInfo(datetime.date.today().day, cost, salary)

if __name__ == "__main__":
    try:
        logger.info("===========程序启动，尝试初始化会话")
        logger.info("===========程序启动，尝试初始化会话")
        logger.info("===========程序启动，尝试初始化会话")
        logger.info("===========程序启动，尝试初始化会话")
        logger.info("===========程序启动，尝试初始化会话")
        game = GAME()
        initGame(game)
        logger.info("===========会话初始化成功")
        logger.info(f"===========COOKIE: {game.getCookie()}")
        logger.info(f"===========UA: {game.getUA()}")
        logger.info(f"===========CSRF: {game.getCSRF()}")
        logger.info("===========初始化角色信息")
        logger.info("===========初始化角色信息")
        logger.info("===========初始化角色信息")

        data = getAllCharacters(game.getUA(), game.getCookie(), game.getCSRF())
        if data['status'] != 200:
            logger.error("getAll 1 状态码异常，退出")
            raise ValueError("getAll 1 状态码异常")

        myRemainBonus = data['data']['bonus']
        myCharacterList = data['data']['characters']
        while checkIfAllCharactersNeedLvlUpAndDoLvlUp(myCharacterList, game):
            logger.info("升级判断完成，重新更新信息")
            data = getAllCharacters(game.getUA(), game.getCookie(), game.getCSRF())
            if data['status'] != 200:
                logger.error("getAll 2 状态码异常，退出")
                raise ValueError("getAll 2 状态码异常")
            logger.info(f"此次升级消费{myRemainBonus - data['data']['bonus']}灵石")
            myRemainBonus = data['data']['bonus']
            myCharacterList = data['data']['characters']
    except Exception as e:
        logger.error("%s 初始化失败: %s", e)
        sys.exit(-1)

    logger.info("初始化结束，开始循环")
    max_wait_time = 3600   # 最大错误等待时间
    current_wait_time = 5  # 最短错误等待时间。每次发生错误都会翻倍

    while True:
        try:
            data = getAllCharacters(game.getUA(), game.getCookie(), game.getCSRF())
            if data['status'] != 200:
                logger.warning("getAll 3 状态码异常")
                current_wait_time = min(current_wait_time * 2, max_wait_time)  # 加倍等待时间，但不超过最大等待时间
                sleep_with_logging(current_wait_time)
                continue
            myRemainBonus = data['data']['bonus']
            myCharacterList = data['data']['characters']
            id = getNextTimeStamp(myCharacterList)
            if id < 1:
                logger.warning("getNextTimeStamp 异常")
                current_wait_time = min(current_wait_time * 2, max_wait_time)  # 加倍等待时间，但不超过最大等待时间
                sleep_with_logging(current_wait_time)
                continue

            c = myCharacterList[id - 1]
            nextTime = c['info']['next_time']
            dt_object = datetime.datetime.fromtimestamp(nextTime)
            logger.info(f"最近可以释放的角色是{c['id']}, {c['key']}, 在{dt_object}")

            remainTime = nextTime - int(time.time())
            if remainTime > 0:
                remainHours = remainTime // 3600  # 3600秒为1小时
                remainMinutes = (remainTime % 3600) // 60  # 60秒为1分钟
                remainSeconds = remainTime % 60
                logger.info(f"还需要{remainHours:02}:{remainMinutes:02}:{remainSeconds:02}进行释放，开始等待")
                # sleep_with_logging(remainTime)
                sleep_to_target_with_logging(game, nextTime + 1) # 多等待1秒，确保释放
            if c['magic'] == 2:
                # todo 有优化空间
                x = releaseAll(game.getUA(), game.getCookie(), game.getCSRF())
                if x['status'] != 200:
                    logger.warning("releaseAll for magic == 2，但是状态码异常")
                    current_wait_time = min(current_wait_time * 2, max_wait_time)  # 加倍等待时间，但不超过最大等待时间
                    sleep_with_logging(current_wait_time)
                    continue
                logger.info("释放技能：灵石加成。等待20秒")
                time.sleep(20)  # 等待20秒
            else:
                for i in range(4):
                    x = releaseAll(game.getUA(), game.getCookie(), game.getCSRF())
                    if x['status'] != 200:
                        logger.warning("releaseAll for magic == 1，但是状态码异常")
                        current_wait_time = min(current_wait_time * 2, max_wait_time)  # 加倍等待时间，但不超过最大等待时间
                        sleep_with_logging(current_wait_time)
                        continue

                    if x['data']['bonus'] == 0:
                        logger.info(f"释放成功，第{i+1}次没有获取到灵石")
                        if (i + 1) == 4:
                            break # 最后一次无需sleep
                    else:
                        logger.info(f"释放成功，第{i+1}次获取{x['data']['bonus']}灵石")
                        updateCostAndSalaryPerDay(0, x['data']['bonus'], game)
                        break
                    time.sleep(5*(i+1))  # 5,10,15,20
                logger.info("释放结束，等待10秒")
                time.sleep(10)  # 等待10秒

            # 释放后判断是否需要升级
            data = getAllCharacters(game.getUA(), game.getCookie(), game.getCSRF())
            if data['status'] != 200:
                logger.warning("getAll 4 状态码异常")
                current_wait_time = min(current_wait_time * 2, max_wait_time)  # 加倍等待时间，但不超过最大等待时间
                sleep_with_logging(current_wait_time)
                continue
            myRemainBonus = data['data']['bonus']
            myCharacterList = data['data']['characters']
            isUp = False
            isUp = checkIfAllCharactersNeedLvlUpAndDoLvlUp(myCharacterList, game)
            logger.info("升级判断完成")
            if isUp == True:
                data = getAllCharacters(game.getUA(), game.getCookie(), game.getCSRF())
                if data['status'] != 200:
                    logger.warning("getAll 5 状态码异常")
                    current_wait_time = min(current_wait_time * 2, max_wait_time)  # 加倍等待时间，但不超过最大等待时间
                    sleep_with_logging(current_wait_time)
                    continue
                logger.info(f"更新信息。此次升级消费{myRemainBonus - data['data']['bonus']}灵石")
                updateCostAndSalaryPerDay(myRemainBonus - data['data']['bonus'], 0, game)
            logger.info("一切正常，重置错误等待时间为5秒。等待20秒进入下一轮循环")
            current_wait_time = 5
            time.sleep(20)  # 等待20秒钟
            # 结束此次循环，重置等待时间为5秒
        except Exception as e:
            current_wait_time = min(current_wait_time * 2, max_wait_time)  # 加倍等待时间，但不超过最大等待时间
            logger.warning(f"未知错误{e}，等待: {current_wait_time}")
            sleep_with_logging(current_wait_time)

    logger.info("程序结束")