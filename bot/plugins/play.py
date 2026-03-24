"""
/play and /vplay handlers – the core streaming logic.
"""

import asyncio
import logging
import os

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from pytgcalls import PyTgCalls, filters as tgfilters, idle
from pytgcalls.types import MediaStream, StreamEnded

from bot.helpers import database as db
from bot.helpers.utils import (
    download_audio,
    download_video,
    get_track_info,
    seconds_to_min,
    search_yt,
)
from config import STREAM_TYPE_AUDIO, STREAM_TYPE_VIDEO, SUPPORT_CHANNEL

logger = logging.getLogger(__name__)

# pytgcalls instance lives here so all plugins share one instance
from bot import assistant

# `app` is imported here so Pyrogram's plugin system picks up the decorators
# defined in this module when it scans the plugins package.
from bot import app as _app  # noqa: F401

call_py = PyTgCalls(assistant)


# ─── Inline buttons ────────────────────────────────────────────────────────────

def _player_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⏸ Pause", callback_data="pause"),
                InlineKeyboardButton("▶️ Resume", callback_data="resume"),
                InlineKeyboardButton("⏭ Skip", callback_data="skip"),
            ],
            [
                InlineKeyboardButton("📢 Join Channel", url=SUPPORT_CHANNEL),
            ],
        ]
    )


# ─── Stream ended callback ────────────────────────────────────────────────────

@call_py.on_update(tgfilters.stream_end)
async def _on_stream_end(client: PyTgCalls, update: StreamEnded):
    chat_id = update.chat_id
    next_track = db.remove_from_queue(chat_id)
    if next_track:
        await _start_stream(chat_id, next_track)
    else:
        db.remove_active(chat_id)
        try:
            await call_py.leave_call(chat_id)
        except Exception:
            pass


# ─── Internal helpers ─────────────────────────────────────────────────────────

async def _ensure_assistant_in_chat(client: Client, chat_id: int) -> None:
    """Make sure the assistant is a member of the voice chat's group."""
    try:
        assistant_me = await assistant.get_me()
        await assistant.get_chat_member(chat_id, assistant_me.id)
    except Exception:
        try:
            chat = await client.get_chat(chat_id)
            invite = await client.export_chat_invite_link(chat_id)
            await assistant.join_chat(invite)
        except Exception as exc:
            logger.warning("Could not invite assistant to %s: %s", chat_id, exc)


async def _start_stream(chat_id: int, track: dict) -> None:
    """Begin streaming a track in the given chat."""
    db.set_active(chat_id, {"status": "playing", "current": track})
    stream_type = track.get("stream_type", STREAM_TYPE_AUDIO)
    file_path = track["file_path"]

    try:
        if stream_type == STREAM_TYPE_VIDEO:
            await call_py.play(
                chat_id,
                MediaStream(file_path),
            )
        else:
            await call_py.play(
                chat_id,
                MediaStream(file_path, video_flags=MediaStream.Flags.IGNORE),
            )
    except Exception as exc:
        logger.error("_start_stream error in %s: %s", chat_id, exc)
        db.remove_active(chat_id)


async def _play_track(
    client: Client,
    message: Message,
    query: str,
    stream_type: str,
) -> None:
    chat_id = message.chat.id
    status_msg = await message.reply_text("🔍 **Searching…**")

    url = await search_yt(query)
    if not url:
        await status_msg.edit_text("❌ No results found. Try a different search.")
        return

    await status_msg.edit_text("⬇️ **Downloading…**")
    if stream_type == STREAM_TYPE_VIDEO:
        file_path, info = await download_video(url, chat_id)
    else:
        file_path, info = await download_audio(url, chat_id)

    if not file_path or not info:
        await status_msg.edit_text("❌ Failed to download the track. Please try again.")
        return

    title = info.get("title", "Unknown")
    duration = seconds_to_min(info.get("duration", 0))
    thumb = info.get("thumbnail", None)
    requester = message.from_user.mention if message.from_user else "Unknown"

    track = {
        "title": title,
        "duration": duration,
        "thumb": thumb,
        "file_path": file_path,
        "stream_type": stream_type,
        "requested_by": requester,
        "url": url,
    }

    caption = (
        f"🎵 **Now Playing**\n\n"
        f"**Title:** {title}\n"
        f"**Duration:** {duration}\n"
        f"**Requested by:** {requester}\n"
    )

    if db.is_active(chat_id):
        # Already streaming – add to queue
        db.add_to_queue(chat_id, track)
        pos = db.queue_length(chat_id)
        await status_msg.edit_text(
            f"✅ **Added to Queue** (Position #{pos})\n\n"
            f"**Title:** {title}\n"
            f"**Duration:** {duration}\n"
            f"**Requested by:** {requester}"
        )
        return

    # Ensure assistant is in the chat
    await _ensure_assistant_in_chat(client, chat_id)
    await _start_stream(chat_id, track)

    try:
        await status_msg.delete()
    except Exception:
        pass

    try:
        if thumb:
            await message.reply_photo(
                thumb,
                caption=caption,
                reply_markup=_player_buttons(),
            )
        else:
            await message.reply_text(
                caption,
                reply_markup=_player_buttons(),
            )
    except Exception as exc:
        logger.warning("Could not send now-playing message: %s", exc)


# ─── Command handlers ─────────────────────────────────────────────────────────

@Client.on_message(filters.command("play") & filters.group)
async def play_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❗ Usage: `/play <song name or YouTube URL>`")
        return
    query = " ".join(message.command[1:])
    await _play_track(client, message, query, STREAM_TYPE_AUDIO)


@Client.on_message(filters.command("vplay") & filters.group)
async def vplay_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❗ Usage: `/vplay <song name or YouTube URL>`")
        return
    query = " ".join(message.command[1:])
    await _play_track(client, message, query, STREAM_TYPE_VIDEO)


# ─── Callback handlers for inline buttons ─────────────────────────────────────

@Client.on_callback_query(filters.regex("^pause$"))
async def cb_pause(client: Client, callback_query):
    from bot.plugins.controls import _do_pause
    await _do_pause(client, callback_query.message)
    await callback_query.answer("⏸ Paused")


@Client.on_callback_query(filters.regex("^resume$"))
async def cb_resume(client: Client, callback_query):
    from bot.plugins.controls import _do_resume
    await _do_resume(client, callback_query.message)
    await callback_query.answer("▶️ Resumed")


@Client.on_callback_query(filters.regex("^skip$"))
async def cb_skip(client: Client, callback_query):
    from bot.plugins.controls import _do_skip
    await _do_skip(client, callback_query.message)
    await callback_query.answer("⏭ Skipped")
