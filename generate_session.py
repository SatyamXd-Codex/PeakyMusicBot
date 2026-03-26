"""
Generate a valid Pyrogram StringSession for Peaky Music Bot.

Run this script once locally (NOT in CI) to obtain a STRING_SESSION value
that you can store as a GitHub secret or in config.env.

Usage:
    python3 generate_session.py
"""

import asyncio
import os

from dotenv import load_dotenv

load_dotenv("config.env")

try:
    API_ID = int(os.environ.get("API_ID", 0))
except ValueError:
    raise SystemExit(
        "API_ID must be a number. Check your config.env or environment variables."
    )
API_HASH = os.environ.get("API_HASH", "")

if not API_ID or not API_HASH:
    raise SystemExit("Set API_ID and API_HASH in config.env before running this script.")


async def generate():
    from pyrogram import Client

    async with Client(
        name="generate_session",
        api_id=API_ID,
        api_hash=API_HASH,
        in_memory=True,
    ) as app:
        session_string = await app.export_session_string()
        print("\n✅ Your STRING_SESSION:\n")
        print(session_string)
        print(
            "\nCopy the value above into your config.env file as STRING_SESSION=<value>"
            "\nor set it as a GitHub secret named STRING_SESSION."
        )


if __name__ == "__main__":
    asyncio.run(generate())
