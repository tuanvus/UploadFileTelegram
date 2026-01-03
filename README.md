# 📤 Telegram Fast Uploader

Fast parallel file uploader for Telegram with Forum Topics support, using FastTelethon to boost upload/download speeds by several times.

## 🚀 Features

- ⚡ **Parallel Upload**: Speed up uploads **2-10x** compared to standard Telethon 
- 🎯 **Forum Topic Support**: Upload directly to specific topics in Telegram Forums 
- 📊 **Real-time Progress Bar**: Display detailed progress, speed, and ETA
- 🔐 **Session Management**: Save session to avoid re-login
- 💾 **Large File Support**: Handle files >2GB with InputFileBig
- 🌐 **Cross-DC Upload**: Automatic authorization export/import for multi-datacenter 

## 📋 Tech Stack

### Core Libraries
- **Telethon 1.x** - Full-featured Telegram MTProto client 
- **Python 3.7+** - Async/await support required 
- **asyncio** - Concurrent connection management

### Custom Implementation
- **FastTelethon (parallel_transfer.py)** - Multi-connection upload/download engine 
  - Dynamic connection scaling (1-25 connections)
  - MTProtoSender pooling
  - Smart buffer management

### APIs Used
- **MTProto API** - Telegram's native protocol 
  - `auth.ExportAuthorization` - Cross-DC authentication 
  - `upload.SaveFilePartRequest` - Small files (<10MB)
  - `upload.SaveBigFilePartRequest` - Large files (>10MB)
  - `channels.GetForumTopicsRequest` - Forum topic information

## ⚡ Speed Benchmarks

### Upload Speed Comparison [web:27][web:30]

| Method | Connections | Speed (20MB file) | Speed (200MB file) | Speed (2GB file) |
|--------|-------------|-------------------|-------------------|------------------|
| Telethon Default | 1 | ~2.1 MiB/s | ~1.5 MiB/s | ~4.6 MiB/s |
| FastTelethon | 2-4 | ~4.0 MiB/s | ~2.8 MiB/s | ~9.1 MiB/s |
| FastTelethon | 10-25 | **~8-15 MiB/s** | **~5-10 MiB/s** | **~20-40 MiB/s** |

**Note**: Actual speeds depend on:
- Your internet bandwidth
- Telegram datacenter location
- File size (larger files = more connections)
- Network latency

### Connection Scaling Logic
```python
# File > 100MB → 25 connections (max)
# File 50-100MB → ~12-13 connections
# File < 10MB → ~2-3 connections
