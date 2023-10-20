# 如何使用

## 通用
1. 安装python 3
2. 运行`install_venv.bat`安装依赖库
3. 当前只支持firefox浏览器
4. 暂时无法过cf真人验证

## 签到、保活
+ 原理：使用selenium操作浏览器进行模拟点击
1. 下载geckodriver.exe：<https://github.com/mozilla/geckodriver/releases>
2. 将geckodriver.exe路径存入环境变量或项目目录
3. （可选）修改target/sign_site.json。默认all
4. firefox不允许使用相同配置打开不同浏览器进程，因此需要关闭当前浏览器
5. 每天执行一次`activate_virtualenv_and_sign.bat`

## 朱雀抽卡时间
+ 原理：使用requests库发送http请求，与签到的原理不同
1. 浏览器登录朱雀（依赖浏览器的cookie数据库），无需关闭浏览器
2. 直接运行`activate_virtualenv_and_game.bat`
3. 可以一直运行在后台

## WIP
+ 签到的同时获取一些数据信息


## TODO
+ 实现undetected_chromedriver. 但是由于cf升级，uc + chrome v117也无法过cf验证，暂停
+ 整合seleniumSign和zhuque_game
+ 日志整改
+ 通过本地记录防止seleniumSign重复签到
+ ~~增加requirements.txt~~
+ 结果推送，考虑使用IYUUU或html页面展示
+ ~~增加配置文件，yaml或ini~~
+ 增加test代码
+ 增加页面访问超时时间