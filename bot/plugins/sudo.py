"""
Sudo-only commands: /restart
"""

import asyncio
import os
import sys

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.helpers.utils import is_sudo


@Client.on_message(filters.command("restart"))
async def restart_cmd(client: Client, message: Message):
    if not is_sudo(message.from_user.id):
        await message.reply_text("🚫 This command is only for sudo users.")
        return

    await message.reply_text("🔄 **Restarting…**")
    os.execv(sys.executable, [sys.executable] + sys.argv)
