@echo off

rem 设置虚拟环境的名称
set venv_name=myenv

rem 创建虚拟环境
python -m venv %venv_name%

rem 激活虚拟环境
call %venv_name%\Scripts\activate

rem 安装依赖项
pip install -r requirements.txt --upgrade

pip freeze
pause

rem 停用虚拟环境
deactivate

