@echo off
title RPSC RAS & UPSC AI Dashboard
cd /d "%~dp0"
if exist "C:\Users\jiten\AppData\Local\Programs\Python\Python314\pythonw.exe" (
    start "" "C:\Users\jiten\AppData\Local\Programs\Python\Python314\pythonw.exe" "app_gui.py"
) else (
    start "" pythonw "app_gui.py"
)
exit
