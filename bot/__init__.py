"""
Peaky Music Bot – initialisation module.
Creates the Bot client and the Assistant (userbot) client.
"""

import logging
import os

from pyrogram import Client

from config import API_ID, API_HASH, BOT_TOKEN, STRING_SESSION

logger = logging.getLogger(__name__)

# ─── Session directory ─────────────────────────────────────────────────────────
os.makedirs("sessions", exist_ok=True)

# ─── Bot client ───────────────────────────────────────────────────────────────
app = Client(
    name="PeakyMusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="bot/plugins"),
    workdir="sessions",
)

# ─── Assistant (userbot) client ───────────────────────────────────────────────
assistant = Client(
    name="PeakyAssistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION,
    workdir="sessions",
)
