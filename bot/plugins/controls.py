"""
Playback control commands: /pause, /resume, /skip, /stop, /end
Only admins and sudo users can use these.
"""

import logging

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.helpers import database as db
from bot.helpers.utils import is_admin

logger = logging.getLogger(__name__)


def _get_call_py():
    """Lazy import to avoid circular dependency."""
    from bot.plugins.play import call_py
    return call_py


# ─── Internal helpers (also called from callbacks in play.py) ─────────────────

async def _do_pause(client: Client, message: Message) -> None:
    chat_id = message.chat.id
    if not db.is_active(chat_id):
        await message.reply_text("❌ Nothing is playing right now.")
        return
    try:
        await _get_call_py().pause(chat_id)
        state = db.get_active(chat_id)
        if state:
            state["status"] = "paused"
        await message.reply_text("⏸ **Playback paused.**")
    except Exception as exc:
        logger.error("pause error: %s", exc)
        await message.reply_text(f"❌ Error: `{exc}`")


async def _do_resume(client: Client, message: Message) -> None:
    chat_id = message.chat.id
    if not db.is_active(chat_id):
        await message.reply_text("❌ Nothing is playing right now.")
        return
    try:
        await _get_call_py().resume(chat_id)
        state = db.get_active(chat_id)
        if state:
            state["status"] = "playing"
        await message.reply_text("▶️ **Playback resumed.**")
    except Exception as exc:
        logger.error("resume error: %s", exc)
        await message.reply_text(f"❌ Error: `{exc}`")


async def _do_skip(client: Client, message: Message) -> None:
    chat_id = message.chat.id
    if not db.is_active(chat_id):
        await message.reply_text("❌ Nothing is playing right now.")
        return
    next_track = db.remove_from_queue(chat_id)
    if next_track:
        from bot.plugins.play import _start_stream
        await _start_stream(chat_id, next_track)
        await message.reply_text(
            f"⏭ **Skipped!**\n\n▶️ Now playing: **{next_track['title']}**"
        )
    else:
        db.remove_active(chat_id)
        try:
            await _get_call_py().leave_call(chat_id)
        except Exception:
            pass
        await message.reply_text("⏹ **Queue is empty. Stopped playback.**")


async def _do_stop(client: Client, message: Message) -> None:
    chat_id = message.chat.id
    if not db.is_active(chat_id):
        await message.reply_text("❌ Nothing is playing right now.")
        return
    db.clear_queue(chat_id)
    db.remove_active(chat_id)
    try:
        await _get_call_py().leave_call(chat_id)
    except Exception:
        pass
    await message.reply_text("⏹ **Stopped and queue cleared.**")


# ─── Command handlers ─────────────────────────────────────────────────────────

@Client.on_message(filters.command("pause") & filters.group)
async def pause_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        await message.reply_text("🚫 Only admins can use this command.")
        return
    await _do_pause(client, message)


@Client.on_message(filters.command("resume") & filters.group)
async def resume_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        await message.reply_text("🚫 Only admins can use this command.")
        return
    await _do_resume(client, message)


@Client.on_message(filters.command("skip") & filters.group)
async def skip_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        await message.reply_text("🚫 Only admins can use this command.")
        return
    await _do_skip(client, message)


@Client.on_message(filters.command("stop") & filters.group)
async def stop_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        await message.reply_text("🚫 Only admins can use this command.")
        return
    await _do_stop(client, message)


@Client.on_message(filters.command("end") & filters.group)
async def end_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        await message.reply_text("🚫 Only admins can use this command.")
        return
    await _do_stop(client, message)
