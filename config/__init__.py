import os

# ─── Bot Credentials ───────────────────────────────────────────────────────────
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "")

# ─── Sudo Users ────────────────────────────────────────────────────────────────
_sudo_raw = os.environ.get("SUDO_USERS", "")
SUDO_USERS = list(
    map(int, [u.strip() for u in _sudo_raw.split(",") if u.strip()])
)

# ─── Bot Info ──────────────────────────────────────────────────────────────────
BOT_NAME = "Peaky Music Bot"
SUPPORT_CHANNEL = "https://t.me/eSportLeaker"

# ─── Streaming ─────────────────────────────────────────────────────────────────
STREAM_TYPE_AUDIO = "audio"
STREAM_TYPE_VIDEO = "video"
