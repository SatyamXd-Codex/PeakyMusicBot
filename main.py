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

# ─── Import clients ────────────────────────────────────────────────────────────
from bot import app, assistant
from bot.plugins.play import call_py


async def main():
    logger.info("Starting Peaky Music Bot…")
    await assistant.start()
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
