from telethon import TelegramClient
import asyncio
import time
import os
import re
import sys

api_id = 32259686
api_hash = '3e4a946477a7bc62144293d79a99d9f4'
session_name = 'local_uploader'

default_file_path = r'Builds/CoreGame_iOS.zip'
default_link = 'https://t.me/c/3473915677/3/9'
default_message = "New build uploaded from pipeline."   # <-- message mặc định

def extract_chat_id_from_link(link: str) -> int:
    m = re.search(r't\.me/c/(\d+)', link)
    if not m:
        raise ValueError('Link không đúng dạng t.me/c/<id>/...')
    digits = m.group(1)
    return int('-100' + digits)

_start_time = None
_total_size = None

def progress(current: int, total: int):
    global _start_time, _total_size
    if _start_time is None:
        _start_time = time.time()
    if _total_size is None:
        _total_size = total

    percent = current * 100 / total if total else 0
    elapsed = max(time.time() - _start_time, 0.001)
    speed = current / 1024 / 1024 / elapsed

    msg = (
        f"\rUploaded {percent:5.1f}%  "
        f"({current/1024/1024:6.2f}/{total/1024/1024:6.2f} MB)  "
        f"{speed:4.2f} MB/s"
    )
    print(msg, end='', flush=True)

async def main(file_path: str, link: str, caption: str):
    chat_id = extract_chat_id_from_link(link)

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f'Không tìm thấy file: {file_path}')

    filename = os.path.basename(file_path)
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / 1024 / 1024

    print(f"Start upload: {filename} ({size_mb:.2f} MB)")
    print(f"Caption: {caption}")

    global _start_time, _total_size
    _start_time = time.time()
    _total_size = size_bytes

    async with TelegramClient(session_name, api_id, api_hash) as client:
        await client.send_file(
            chat_id,
            file_path,
            caption=caption,
            progress_callback=progress,
        )

    elapsed = time.time() - _start_time
    speed = size_mb / elapsed if elapsed > 0 else 0
    print(f"\nUpload xong: {filename}")
    print(f"Thời gian: {elapsed:.1f} s")
    print(f"Tốc độ TB: {speed:.2f} MB/s")

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else default_file_path
    link = sys.argv[2] if len(sys.argv) > 2 else default_link

    # Ưu tiên theo thứ tự:
    # 1) Arg từ command line (sys.argv[3:])
    # 2) Nếu không có arg, hỏi input()
    # 3) Nếu chỉ Enter trống, dùng default_message
    if len(sys.argv) > 3:
        caption = " ".join(sys.argv[3:])
    else:
        user_input = input(f"Nhập message (Enter để dùng mặc định):\n[{default_message}]\n> ")
        caption = user_input.strip() or default_message

    asyncio.run(main(file_path, link, caption))
