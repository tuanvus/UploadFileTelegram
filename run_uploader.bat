@echo off
setlocal

if not exist ".venv" (
    echo Virtualenv chua co. Run setup_telegram_uploader.bat truoc.
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"

REM Truyen path file + link neu muon, neu khong se dung default trong script
REM vi du:
REM .venv\Scripts\python TelegramClient.py "Builds\CoreGame_iOS.zip" "https://t.me/c/3473915677/3/9"

.venv\Scripts\python TelegramClient.py

pause
endlocal
