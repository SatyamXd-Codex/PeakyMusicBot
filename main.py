"""
Peaky Music Bot – entry point.
"""

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv("config.env")

# ─── Logging setup ─────────────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join("logs", "peaky.log"), encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)

# ─── Validate config ───────────────────────────────────────────────────────────
from config import API_ID, API_HASH, BOT_TOKEN, STRING_SESSION

_missing = []
if not API_ID:
    _missing.append("API_ID")
if not API_HASH:
    _missing.append("API_HASH")
if not BOT_TOKEN:
    _missing.append("BOT_TOKEN")
if not STRING_SESSION:
    _missing.append("STRING_SESSION")

if _missing:
    logger.critical("Missing required environment variables: %s", ", ".join(_missing))
    sys.exit(1)

# Validate STRING_SESSION length for pyrogram 2.x compatibility.
# These are the only valid *encoded* (base64) string lengths pyrogram 2.x accepts:
#   351 → old format  (decodes to 263 bytes)
#   356 → old-64 format (decodes to 267 bytes, 64-bit user_id)
#   362 → new format  (decodes to 271 bytes, pyrogram ≥ 2.0)
_VALID_SESSION_STRING_LENGTHS = (351, 356, 362)
if len(STRING_SESSION) not in _VALID_SESSION_STRING_LENGTHS:
    logger.critical(
        "STRING_SESSION has invalid length %d (expected one of %s). "
        "Please regenerate it using generate_session.py.",
        len(STRING_SESSION),
        _VALID_SESSION_STRING_LENGTHS,
    )
    sys.exit(1)

# ─── Import clients ────────────────────────────────────────────────────────────
from bot import app, assistant
from bot.plugins.play import call_py


async def main():
    logger.info("Starting Peaky Music Bot…")
    try:
        await assistant.start()
    except Exception as exc:
        logger.critical(
            "Failed to start assistant client: %s. "
            "Make sure STRING_SESSION is a valid pyrogram 2.x session string "
            "(generate one with: python3 generate_session.py).",
            exc,
        )
        sys.exit(1)
    logger.info("Assistant client started.")
    await app.start()
    logger.info("Bot client started.")
    await call_py.start()
    logger.info("PyTgCalls started. Bot is live! 🎵")

    # Keep the bot alive
    from pytgcalls import idle as pytgcalls_idle
    await pytgcalls_idle()

    # Graceful shutdown
    await call_py.stop()
    await app.stop()
    await assistant.stop()
    logger.info("Peaky Music Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
