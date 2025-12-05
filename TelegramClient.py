from telethon import TelegramClient, functions
import asyncio
import time
import os
import re
import sys
import telethon
import telethon.tl.functions.channels as ch


api_id = 32259686
api_hash = '3e4a946477a7bc62144293d79a99d9f4'
session_name = 'local_uploader'

default_file_path = r'Builds/CoreGame_iOS.zip'
default_link = 'https://t.me/c/3473915677/3/9'
default_message = "New build uploaded from pipeline."


def extract_ids_from_link(link: str):
    """
    Trích xuất internal chat id + topic id từ link Telegram.
    """
    m = re.search(r't\.me/c/(\d+)/(\d+)', link)
    if not m:
        raise ValueError("Link không hợp lệ. Phải là dạng: https://t.me/c/<id>/<topic>")
    internal_id = m.group(1)
    topic_id = int(m.group(2))
    chat_id = int("-100" + internal_id)
    return chat_id, topic_id


# ----------- PROGRESS BAR (BẢN ĐẸP) ----------
_start_time = None
_total_size = None


def progress(current: int, total: int):
    global _start_time, _total_size

    if _start_time is None:
        _start_time = time.time()

    percent = current / total
    bar_len = 28
    filled_len = int(bar_len * percent)

    bar = "█" * filled_len + "-" * (bar_len - filled_len)

    elapsed = time.time() - _start_time
    speed = current / 1024 / 1024 / elapsed if elapsed > 0 else 0
    eta = (total - current) / 1024 / 1024 / speed if speed > 0 else 0

    print(
        f"\r[{bar}] {percent*100:5.1f}% "
        f"{current/1024/1024:6.2f}/{total/1024/1024:6.2f} MB "
        f"{speed:4.2f} MB/s ETA: {eta:5.1f}s",
        end='',
        flush=True
    )


# ----------- LẤY TÊN GROUP & TÊN TOPIC ----------
async def resolve_chat_and_topic(client, chat_id: int, topic_id: int):
    # Lấy entity + tên nhóm/kênh
    chat = await client.get_entity(chat_id)
    chat_name = getattr(chat, "title", getattr(chat, "first_name", "Unknown"))

    # Mặc định nếu không tìm được title
    topic_name = f"Topic {topic_id}"

    try:
        # Lấy danh sách tất cả topic trong forum (tối đa 1000 topic)
        res = await client(functions.channels.GetForumTopicsRequest(
            channel=chat,
            q=None,          # không filter theo text
            offset_date=0,
            offset_id=0,
            offset_topic=0,
            limit=1000,
        ))

        # Map id -> title
        topic_map = {t.id: t.title for t in res.topics}

        # Nếu topic_id tồn tại trong map, lấy title thật
        if topic_id in topic_map:
            topic_name = topic_map[topic_id]

    except Exception as e:
        # debug tạm thời
        print("GetForumTopics error:", e)

    return chat_name, topic_name


# ----------- MAIN UPLOAD LOGIC ----------
async def main(file_path: str, link: str, caption: str):
    chat_id, topic_id = extract_ids_from_link(link)

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    filename = os.path.basename(file_path)
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / 1024 / 1024

    print(f"Start upload: {filename} ({size_mb:.2f} MB)")
    print(f"Caption: {caption}")

    global _start_time, _total_size
    _start_time = time.time()
    _total_size = size_bytes

    async with TelegramClient(session_name, api_id, api_hash) as client:

        # Lấy tên group + topic
        chat_name, topic_name = await resolve_chat_and_topic(client, chat_id, topic_id)
        print(f"\nSend to: {chat_name} -> {topic_name}\n")

        await client.send_file(
            chat_id,
            file_path,
            caption=caption,
            progress_callback=progress,
        )

    elapsed = time.time() - _start_time
    speed_avg = size_mb / elapsed if elapsed > 0 else 0

    print(f"\nUpload xong: {filename}")
    print(f"Thời gian: {elapsed:.1f} s")
    print(f"Tốc độ TB: {speed_avg:.2f} MB/s")


# ----------- ENTRY POINT ----------
if __name__ == "__main__":
    print(telethon.__version__)
    
    print([name for name in dir(ch) if 'Forum' in name])
    
    file_path = sys.argv[1] if len(sys.argv) > 1 else default_file_path
    link = sys.argv[2] if len(sys.argv) > 2 else default_link

    # Caption logic
    if len(sys.argv) > 3:
        caption = " ".join(sys.argv[3:])
    else:
        user_input = input(f"Nhập message (Enter để dùng mặc định):\n[{default_message}]\n> ")
        caption = user_input.strip() or default_message

    asyncio.run(main(file_path, link, caption))
