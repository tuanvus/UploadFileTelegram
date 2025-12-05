@echo off
setlocal

REM ==== 1. Tạo venv nếu chưa có ====
if not exist ".venv" (
    echo Creating virtual environment...
    py -m venv .venv
)

REM ==== 2. Active venv ====
call ".venv\Scripts\activate.bat"

REM ==== 3. Upgrade pip + cài packages ====
echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing requirements...
python -m pip install -r requirements.txt

echo.
echo Environment is ready. Run uploader with:
echo   .venv\Scripts\python TelegramClient.py
echo or double-click run_uploader.bat if you create it.
echo.

pause
endlocal
