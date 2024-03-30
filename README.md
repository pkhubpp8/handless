# 如何使用

## 通用
1. 安装python 3
2. 运行`install_venv.bat`安装依赖库

## DNSPod
+ 原理：使用requests库发送http请求
1. 直接运行`activate_virtualenv_and_ddns.bat`

## 签到、保活
+ 原理：使用selenium操作浏览器进行模拟点击
1. 下载匹配浏览器的geckodriver.exe：<https://github.com/mozilla/geckodriver/releases>
2. 将geckodriver.exe路径存入环境变量或项目目录
3. （可选）修改target/sign_site.json。默认all
4. 因为firefox不允许使用相同配置打开不同浏览器进程，因此需要关闭已经打开的firefox
5. 执行`activate_virtualenv_and_sign.bat`

## 朱雀抽卡时间
+ 原理：使用requests库发送http请求，与签到的原理不同
1. 浏览器登录朱雀（依赖浏览器的cookie数据库），无需关闭浏览器
2. 直接运行`activate_virtualenv_and_game.bat`


## WIP
+ 签到的同时获取一些数据信息
+ 完善`qb_check_unseeding_files.py`和`router_controller.py`

## TODO
+ 实现chromedriver. 都无法过cf验证，暂时不搞
+ 整合seleniumSign和zhuque_game
+ ~~通过本地记录防止seleniumSign重复签到~~
+ ~~增加requirements.txt~~
+ 签到结果推送
+ ~~增加配置文件，yaml或ini~~