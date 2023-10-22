import requests

def test_http_connection(url = "https://www.baidu.com/", ua = ""):
    default_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101Firefox/118.0"
    url_set = {
    "https://t.cn/", 
    "https://www.qq.com/", 
    "https://www.bilibili.com/",
    "https://www.baidu.com/",
    "https://www.douyin.com/"}
    url_set.add(url)
    if ua:
        default_ua = ua

    for each_url in url_set:
        try:
            response = requests.get(each_url, headers = {"User-Agent": default_ua})
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
    return False

