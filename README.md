# 🎵 Peaky Music Bot

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Pyrogram-2.0-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/PyTgCalls-Latest-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge" />
</p>

<p align="center">
  <b>A fast, lightweight, and production-ready Telegram Music Bot</b><br/>
  Stream high-quality audio &amp; video from YouTube directly into Telegram Voice Chats.
</p>

<p align="center">
  <a href="https://t.me/eSportLeaker">
    <img src="https://img.shields.io/badge/📢%20Join%20Channel-Telegram-blue?style=for-the-badge&logo=telegram" />
  </a>
</p>

---

## ✨ Features

- 🎵 **Stream Audio** from YouTube into Voice Chat
- 🎬 **Stream Video** from YouTube into Video Chat
- 📋 **Queue System** – per-chat queue with auto-play next
- ⏯ **Full Controls** – pause, resume, skip, stop, end
- 👤 **Role-Based** – user / admin / sudo permissions
- 🤖 **Assistant System** – userbot auto-joins VC, auto-invites itself
- 🖼 **Beautiful UI** – song thumbnail, title, duration, requester shown
- 🔘 **Inline Buttons** – pause, resume, skip from message
- 📝 **Logging** – file + console logging
- ⚡ **No Database** – fully in-memory, zero setup
- 🐍 **Python 3.10+** – modern async, clean code

---

## 📋 Commands

### 👤 User Commands
| Command | Description |
|---------|-------------|
| `/play <song/URL>` | Stream audio in voice chat |
| `/vplay <song/URL>` | Stream video in video chat |

### 🛡 Admin Commands
| Command | Description |
|---------|-------------|
| `/pause` | Pause current playback |
| `/resume` | Resume paused playback |
| `/skip` | Skip to next track |
| `/stop` | Stop playback & clear queue |
| `/end` | Stop playback & leave VC |
| `/queue` | Show current queue |

### 🔑 Sudo Commands
| Command | Description |
|---------|-------------|
| `/restart` | Restart the bot |

---

## ⚙️ Requirements

- Python **3.10** or higher
- **FFmpeg** installed on your system
- A Telegram **Bot Token** (from [@BotFather](https://t.me/BotFather))
- A Telegram **API ID & API Hash** (from [my.telegram.org](https://my.telegram.org))
- A **Pyrogram String Session** for the assistant account
- The bot must be an **admin** in the group
- The group must have **Voice Chat** enabled

---

## 🚀 Deployment Guide

### 📍 Option A – Ubuntu / Debian VPS

```bash
# 1. Update and upgrade system
sudo apt update && sudo apt upgrade -y

# 2. Install required packages
sudo apt install -y python3 python3-pip python3-venv ffmpeg git

# 3. Clone the repository
git clone https://github.com/SatyamXd-Codex/PeakyMusicBot.git
cd PeakyMusicBot

# 4. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# 5. Install Python dependencies
pip install -r requirements.txt

# 6. Set up environment variables
cp config.env.example config.env   # or export variables directly
nano config.env                    # Fill in your credentials

# 7. Run the bot
python3 main.py
```

---

### 📱 Option B – Termux (Android)

```bash
# 1. Update packages
pkg update && pkg upgrade -y

# 2. Install required tools
pkg install -y python ffmpeg git

# 3. Clone the repository
git clone https://github.com/SatyamXd-Codex/PeakyMusicBot.git
cd PeakyMusicBot

# 4. Install dependencies
pip install -r requirements.txt

# 5. Export environment variables
export API_ID=your_api_id
export API_HASH=your_api_hash
export BOT_TOKEN=your_bot_token
export STRING_SESSION=your_string_session
export SUDO_USERS=your_user_id

# 6. Run the bot
python3 main.py
```

---

### 🌐 Option C – General VPS / Cloud

```bash
git clone https://github.com/SatyamXd-Codex/PeakyMusicBot.git
cd PeakyMusicBot
pip3 install -r requirements.txt
# Set environment variables (see below)
python3 main.py
```

---

## 🔑 Environment Variables

Create a `config.env` file or export these variables in your shell:

```env
# Telegram API credentials (from https://my.telegram.org)
API_ID=123456
API_HASH=abcdef1234567890abcdef1234567890

# Bot token (from @BotFather)
BOT_TOKEN=123456:ABC-DEF...

# Pyrogram string session for the assistant account
STRING_SESSION=BQA...

# Comma-separated Telegram user IDs for sudo access
SUDO_USERS=123456789,987654321
```

> 💡 **Tip:** To load from `config.env` automatically, install `python-dotenv`:
> `pip install python-dotenv` and add `from dotenv import load_dotenv; load_dotenv("config.env")` to the top of `main.py`.

---

## 🔐 How to Generate a String Session

The bot needs a **userbot assistant** account to join voice chats. Generate its string session with:

```python
from pyrogram import Client

with Client("assistant", api_id=API_ID, api_hash=API_HASH) as app:
    print(app.export_session_string())
```

**Step-by-step:**

1. Open a Python shell or create a file with the code above.
2. Fill in your `API_ID` and `API_HASH`.
3. Run it – Pyrogram will ask for your **phone number**, then the **OTP**.
4. Copy the printed string and set it as `STRING_SESSION`.

> ⚠️ **Never share your String Session with anyone!**

---

## 📁 Project Structure

```
PeakyMusicBot/
├── bot/
│   ├── __init__.py          # Pyrogram bot + assistant clients
│   ├── helpers/
│   │   ├── __init__.py
│   │   ├── database.py      # In-memory queue & state
│   │   └── utils.py         # yt-dlp, role checks, helpers
│   └── plugins/
│       ├── __init__.py
│       ├── start.py         # /start, /help
│       ├── play.py          # /play, /vplay + stream logic
│       ├── controls.py      # /pause, /resume, /skip, /stop, /end
│       ├── queue.py         # /queue
│       └── sudo.py          # /restart
├── config/
│   └── __init__.py          # Config from environment variables
├── logs/
│   └── peaky.log            # Runtime log file
├── main.py                  # Entry point
├── requirements.txt
├── Procfile
├── .gitignore
└── README.md
```

---

## ⚠️ Important Notes

- The **bot must be an admin** in the group (with at least "Manage Voice Chats" permission).
- The **assistant account** must be able to join the group. The bot will try to auto-invite it.
- **Voice Chat / Video Chat** must be enabled in your Telegram group.
- Keep the assistant account **active** – do not terminate the session.
- FFmpeg must be installed on the server for audio/video processing.

---

## 🛠 Tech Stack

| Tool | Purpose |
|------|---------|
| [Python 3.10+](https://python.org) | Core language |
| [Pyrogram](https://pyrogram.org) | Telegram MTProto client |
| [PyTgCalls](https://pytgcalls.github.io) | Voice/Video chat streaming |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | YouTube audio/video fetching |
| [FFmpeg](https://ffmpeg.org) | Media processing |

---

## 👨‍💻 Developer

**Satyam Xd** – [@eSportLeaker](https://t.me/eSportLeaker)

---

## 📜 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ by <b>Satyam Xd</b> &nbsp;|&nbsp;
  <a href="https://t.me/eSportLeaker">📢 Join Channel</a>
</p>