@echo off
call myenv\Scripts\activate.bat
python seleniumSign.py
call myenv\Scripts\deactivate.bat