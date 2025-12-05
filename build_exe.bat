@echo off
setlocal

if not exist ".venv" (
    echo Chua co venv. đã khởi tạo.
	py -m venv .venv
)

call ".venv\Scripts\activate.bat"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

pyinstaller --onefile --name TelegramUploader TelegramClient.py

echo.
echo EXE build xong: dist\TelegramUploader.exe
pause
endlocal
