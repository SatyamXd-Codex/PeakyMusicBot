"""
/start and /help command handlers.
"""

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import BOT_NAME, SUPPORT_CHANNEL

HELP_TEXT = f"""
**🎵 {BOT_NAME} – Commands**

**User Commands:**
• `/play <song/URL>` – Stream audio in voice chat
• `/vplay <song/URL>` – Stream video in voice chat

**Admin Commands:**
• `/pause` – Pause playback
• `/resume` – Resume playback
• `/skip` – Skip to next track
• `/stop` – Stop and clear queue
• `/end` – Stop playback and leave VC
• `/queue` – Show current queue

**Sudo Commands:**
• `/restart` – Restart the bot

━━━━━━━━━━━━━━━━━━━━
Add me to your group, make me admin, and start playing music! 🎶
"""


@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📢 Join Channel", url=SUPPORT_CHANNEL),
                InlineKeyboardButton("❓ Help", callback_data="help"),
            ]
        ]
    )
    await message.reply_text(
        f"**🎵 Welcome to {BOT_NAME}!**\n\n"
        "A fast & lightweight Telegram Music Bot.\n"
        "Add me to your group and use `/play` to start streaming!\n\n"
        f"[Join our channel]({SUPPORT_CHANNEL}) for updates.",
        reply_markup=buttons,
        disable_web_page_preview=True,
    )


@Client.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    await message.reply_text(HELP_TEXT)


@Client.on_callback_query(filters.regex("^help$"))
async def help_callback(client: Client, callback_query):
    await callback_query.message.edit_text(HELP_TEXT)
    await callback_query.answer()
