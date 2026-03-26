"""
Utility helpers: yt-dlp downloading, thumbnail fetching, duration formatting,
admin/sudo role checks.
"""

import asyncio
import logging
import os
import re
from typing import Optional, Tuple

import yt_dlp

from config import SUDO_USERS

logger = logging.getLogger(__name__)

YT_COOKIES = os.environ.get("YT_COOKIES_FILE", None)  # optional cookies.txt path


# ─── Duration ──────────────────────────────────────────────────────────────────

def seconds_to_min(seconds: int) -> str:
    """Convert seconds → mm:ss string."""
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


# ─── yt-dlp helpers ────────────────────────────────────────────────────────────

def _build_ydl_opts(audio: bool, output_template: str) -> dict:
    opts = {
        "quiet": True,
        "no_warnings": True,
        "outtmpl": output_template,
        "retries": 3,
    }
    if YT_COOKIES:
        opts["cookiefile"] = YT_COOKIES

    if audio:
        opts.update(
            {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
        )
    else:
        opts.update(
            {
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            }
        )
    return opts


async def search_yt(query: str) -> Optional[str]:
    """Return the YouTube URL for a search query (or pass through if already URL)."""
    if re.match(r"https?://", query):
        return query

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch1",
        "skip_download": True,
    }
    if YT_COOKIES:
        ydl_opts["cookiefile"] = YT_COOKIES

    loop = asyncio.get_running_loop()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(
                None, lambda: ydl.extract_info(f"ytsearch1:{query}", download=False)
            )
        if info and "entries" in info and info["entries"]:
            return info["entries"][0].get("webpage_url")
    except Exception as exc:
        logger.error("search_yt error: %s", exc)
    return None


async def get_track_info(url: str) -> Optional[dict]:
    """Fetch metadata for a YouTube URL without downloading."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    if YT_COOKIES:
        ydl_opts["cookiefile"] = YT_COOKIES

    loop = asyncio.get_running_loop()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(
                None, lambda: ydl.extract_info(url, download=False)
            )
        return info
    except Exception as exc:
        logger.error("get_track_info error: %s", exc)
    return None


async def download_audio(url: str, chat_id: int) -> Tuple[Optional[str], Optional[dict]]:
    """Download best audio. Returns (file_path, info_dict)."""
    out_dir = os.path.join("downloads", str(chat_id))
    os.makedirs(out_dir, exist_ok=True)
    template = os.path.join(out_dir, "%(id)s.%(ext)s")
    opts = _build_ydl_opts(audio=True, output_template=template)
    loop = asyncio.get_running_loop()
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await loop.run_in_executor(
                None, lambda: ydl.extract_info(url, download=True)
            )
        # After FFmpeg post-processing the extension becomes mp3
        video_id = info.get("id") if info else None
        if not video_id:
            logger.error("download_audio: could not determine video id from info")
            return None, None
        path = os.path.join(out_dir, f"{video_id}.mp3")
        if not os.path.exists(path):
            # fallback: find any file in dir with the video id
            for f in os.listdir(out_dir):
                if video_id in f:
                    path = os.path.join(out_dir, f)
                    break
        return path, info
    except Exception as exc:
        logger.error("download_audio error: %s", exc)
    return None, None


async def download_video(url: str, chat_id: int) -> Tuple[Optional[str], Optional[dict]]:
    """Download best video. Returns (file_path, info_dict)."""
    out_dir = os.path.join("downloads", str(chat_id))
    os.makedirs(out_dir, exist_ok=True)
    template = os.path.join(out_dir, "%(id)s.%(ext)s")
    opts = _build_ydl_opts(audio=False, output_template=template)
    loop = asyncio.get_running_loop()
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await loop.run_in_executor(
                None, lambda: ydl.extract_info(url, download=True)
            )
            if not info:
                logger.error("download_video: yt-dlp returned no info for %s", url)
                return None, None
            path = ydl.prepare_filename(info)
        # yt-dlp may merge into mkv; find the actual file by trying known extensions
        base, _ = os.path.splitext(path)
        for ext in ("mp4", "mkv", "webm"):
            candidate = f"{base}.{ext}"
            if os.path.exists(candidate):
                return candidate, info
        # Last resort: use the prepare_filename path if it exists
        if os.path.exists(path):
            return path, info
        logger.error("download_video: could not locate downloaded file for %s", url)
    except Exception as exc:
        logger.error("download_video error: %s", exc)
    return None, None


# ─── Role checks ───────────────────────────────────────────────────────────────

async def is_admin(client, chat_id: int, user_id: int) -> bool:
    """Return True if user_id is a chat admin or a sudo user."""
    if user_id in SUDO_USERS:
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status.value in ("administrator", "creator")
    except Exception:
        return False


def is_sudo(user_id: int) -> bool:
    return user_id in SUDO_USERS
