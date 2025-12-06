from telethon import TelegramClient, functions, utils
from telethon.tl import types
import asyncio
import time
import os
import re
import sys
import telethon
import telethon.tl.functions.channels as ch

# Import FastTelethon
try:
    from FastTelethon import upload_file
    FAST_UPLOAD = True
    print("✓ FastTelethon loaded - Upload song song (NHANH)\n")
except ImportError:
    FAST_UPLOAD = False
    print("✗ FastTelethon not found - Upload thường (CHẬM)\n")

# ========== CẤU HÌNH SESSION PATH ==========
USER_HOME = os.path.expanduser("~")
SESSION_DIR = os.path.join(USER_HOME, ".telegram_sessions")
os.makedirs(SESSION_DIR, exist_ok=True)
session_path = os.path.join(SESSION_DIR, "local_uploader")

print(f"Session: {session_path}.session\n")

# ========== CẤU HÌNH API ==========
api_id = 32259686
api_hash = "3e4a946477a7bc62144293d79a99d9f4"

default_file_path = r"Builds/CoreGame_iOS.zip"
default_link = "https://t.me/c/2046770732/2725"
default_message = "New build uploaded from pipeline."


def extract_ids_from_link(link: str):
    """Trích xuất internal chat id + topic id từ link Telegram."""
    m = re.search(r"t\.me/c/(\d+)/(\d+)", link)
    if not m:
        raise ValueError("Link không hợp lệ. Phải là dạng: https://t.me/c/<id>/<topic>")
    internal_id = m.group(1)
    topic_id = int(m.group(2))
    chat_id = int("-100" + internal_id)
    return chat_id, topic_id


# ----------- PROGRESS BAR ----------
_start_time = None


def progress(current: int, total: int):
    global _start_time

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
        end="",
        flush=True,
    )


# ----------- LẤY TÊN GROUP & TOPIC ----------
async def resolve_chat_and_topic(client, chat_id: int, topic_id: int):
    chat = await client.get_entity(chat_id)
    chat_name = getattr(chat, "title", getattr(chat, "first_name", "Unknown"))
    topic_name = f"Topic {topic_id}"

    try:
        res = await client(
            functions.channels.GetForumTopicsRequest(
                channel=chat,
                q=None,
                offset_date=0,
                offset_id=0,
                offset_topic=0,
                limit=1000,
            )
        )
        topic_map = {t.id: t.title for t in res.topics}
        if topic_id in topic_map:
            topic_name = topic_map[topic_id]
    except Exception as e:
        print(f"GetForumTopics error: {e}")

    return chat_name, topic_name


# ----------- MAIN UPLOAD LOGIC ----------
async def main(file_path: str, link: str, caption: str):
    chat_id, topic_id = extract_ids_from_link(link)

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    filename = os.path.basename(file_path)
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / 1024 / 1024

    print(f"File: {filename} ({size_mb:.2f} MB)")
    print(f"Mode: {'⚡ FAST (parallel)' if FAST_UPLOAD else '🐢 NORMAL (slow)'}")
    print(f"Caption: {caption}\n")

    global _start_time
    _start_time = time.time()

    async with TelegramClient(session_path, api_id, api_hash) as client:
        chat_name, topic_name = await resolve_chat_and_topic(client, chat_id, topic_id)
        print(f"Send to: {chat_name} -> {topic_name}\n")

        if FAST_UPLOAD:
            # ===== FAST UPLOAD (SONG SONG) =====
            with open(file_path, "rb") as f:
                uploaded_file = await upload_file(
                    client=client,
                    file=f,
                    progress_callback=progress
                )

            # Get file attributes
            attributes, mime_type = utils.get_attributes(file_path)
            
            # Send file với attributes
            await client.send_file(
                chat_id,
                file=uploaded_file,
                caption=caption,
                reply_to=topic_id,
                attributes=attributes,
                mime_type=mime_type,
                force_document=True
            )
        else:
            # ===== NORMAL UPLOAD (TỐI ƯU PART SIZE) =====
            await client.send_file(
                chat_id,
                file_path,
                caption=caption,
                progress_callback=progress,
                reply_to=topic_id,
                part_size_kb=1024  # Tăng từ 512KB lên 1024KB
            )

    elapsed = time.time() - _start_time
    speed_avg = size_mb / elapsed if elapsed > 0 else 0

    print(f"\n\n✅ Upload xong: {filename}")
    print(f"⏱  Thời gian: {elapsed:.1f}s")
    print(f"🚀 Tốc độ TB: {speed_avg:.2f} MB/s")


# ----------- ENTRY POINT ----------
if __name__ == "__main__":
    print(f"Telethon v{telethon.__version__}")
    
    # Check cryptg
    try:
        import cryptg
        print("✓ cryptg installed (AES tối ưu)")
    except ImportError:
        print("✗ cryptg NOT installed - Chạy: pip install cryptg")
    
    print()

    file_path = sys.argv[1] if len(sys.argv) > 1 else default_file_path
    link = sys.argv[2] if len(sys.argv) > 2 else default_link

    if len(sys.argv) > 3:
        caption = " ".join(sys.argv[3:])
    else:
        user_input = input(
            f"Nhập message (Enter = mặc định):\n[{default_message}]\n> "
        )
        caption = user_input.strip() or default_message

    asyncio.run(main(file_path, link, caption))
