"""
/queue command – shows the current playback queue.
"""

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.helpers import database as db
from bot.helpers.utils import is_admin


@Client.on_message(filters.command("queue") & filters.group)
async def queue_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        await message.reply_text("🚫 Only admins can use this command.")
        return

    chat_id = message.chat.id
    active = db.get_active(chat_id)

    if not active and not db.queue_length(chat_id):
        await message.reply_text("📭 The queue is empty.")
        return

    lines = ["🎶 **Current Queue**\n"]

    if active:
        current = active.get("current", {})
        status_icon = "▶️" if active.get("status") == "playing" else "⏸"
        lines.append(
            f"{status_icon} **Now Playing:**\n"
            f"   `{current.get('title', 'Unknown')}` "
            f"[{current.get('duration', '??:??')}] "
            f"– {current.get('requested_by', 'Unknown')}\n"
        )

    queue = db.get_queue(chat_id)
    if queue:
        lines.append("**Up Next:**")
        for i, track in enumerate(queue, start=1):
            lines.append(
                f"  {i}. `{track.get('title', 'Unknown')}` "
                f"[{track.get('duration', '??:??')}] "
                f"– {track.get('requested_by', 'Unknown')}"
            )

    await message.reply_text("\n".join(lines))
