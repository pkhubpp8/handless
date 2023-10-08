# 使用原因
1. 网站签到，比如pt站
2. 网站保活，比如长期不登陆就删封号的
3. 朱雀抽卡时间
4. 解放双手


# 如何使用

## 通用
1. 安装python 3
2. 安装必须的依赖库

## 签到、保活
1. 下载geckodriver.exe：<https://github.com/mozilla/geckodriver/releases>
2. 将geckodriver.exe路径存入环境变量或项目目录
3. （可选）修改target/sign_site.json
4. 关闭浏览器
5. `python seleniumSign.py`




## 朱雀抽卡时间
+ 浏览器登录朱雀，无需关闭浏览器
+ 直接运行`zhuque_game.py`或`python zhuque_game.py`。
+ 如果http报400错误，重新抓包，修改getAllCharacters的headers。大概率是"If-None-Match"引起的。
+ 可以一直运行在后台，例如NAS上
+ 如果浏览器有多份配置文件，cookie仅会从第一份配置文件中获取。如果加载cookie失败。可以用以下方法
### 方法1
1. 直接修改`zhuque_game.py`中的`profile.getProfilePath()`，替换为默认配置路径，注意转义符
2. 配置文件获取方式：打开火狐浏览器，地址栏输入`about:profiles`。取"根目录"地址

### 方法2
+ 安装geckodriver.exe，`profile.py`会自动检测firefox的默认配置路径，过程相对较慢

