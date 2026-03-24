"""
In-memory queue and active-call state management.
No external database required.
"""

from typing import Dict, List, Optional

# queue_data: { chat_id: [ { title, duration, thumb, file_path, stream_type, requested_by }, ... ] }
queue_data: Dict[int, List[dict]] = {}

# active_chats: { chat_id: { "status": "playing"|"paused", "current": {...} } }
active_chats: Dict[int, dict] = {}


# ─── Queue helpers ─────────────────────────────────────────────────────────────

def get_queue(chat_id: int) -> List[dict]:
    return queue_data.get(chat_id, [])


def add_to_queue(chat_id: int, track: dict) -> None:
    queue_data.setdefault(chat_id, []).append(track)


def remove_from_queue(chat_id: int) -> Optional[dict]:
    """Pop and return the next track from the queue."""
    q = queue_data.get(chat_id, [])
    if q:
        return q.pop(0)
    return None


def clear_queue(chat_id: int) -> None:
    queue_data.pop(chat_id, None)


def queue_length(chat_id: int) -> int:
    return len(queue_data.get(chat_id, []))


# ─── Active chat helpers ───────────────────────────────────────────────────────

def get_active(chat_id: int) -> Optional[dict]:
    return active_chats.get(chat_id)


def set_active(chat_id: int, data: dict) -> None:
    active_chats[chat_id] = data


def remove_active(chat_id: int) -> None:
    active_chats.pop(chat_id, None)


def is_active(chat_id: int) -> bool:
    return chat_id in active_chats
