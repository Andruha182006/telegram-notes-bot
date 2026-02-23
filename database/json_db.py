# database/json_db.py — вся робота з JSON-файлом

import json
from datetime import datetime
from pathlib import Path

from config import DATETIME_FORMAT, DB_PATH

_path = Path(DB_PATH)


def init_db():
    """Створює JSON-файл якщо він ще не існує."""
    if not _path.exists():
        _save({"next_id": 1, "notes": []})


def _load() -> dict:
    with open(_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict):
    with open(_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_note(user_id: int, text: str, remind_at: str | None) -> int:
    """Додає нотатку, повертає її ID."""
    data = _load()
    note_id = data["next_id"]
    data["notes"].append({
        "id": note_id,
        "user_id": user_id,
        "text": text,
        "remind_at": remind_at,
        "reminded": False,
    })
    data["next_id"] += 1
    _save(data)
    return note_id


def get_notes(user_id: int) -> list[dict]:
    """Повертає всі нотатки користувача."""
    return [n for n in _load()["notes"] if n["user_id"] == user_id]


def delete_note(user_id: int, note_id: int) -> bool:
    """Видаляє нотатку. Повертає True якщо знайдено і видалено."""
    data = _load()
    before = len(data["notes"])
    data["notes"] = [
        n for n in data["notes"]
        if not (n["id"] == note_id and n["user_id"] == user_id)
    ]
    if len(data["notes"]) == before:
        return False
    _save(data)
    return True


def get_pending_reminders() -> list[dict]:
    """Повертає нотатки, час яких настав і нагадування ще не відправлено."""
    now = datetime.utcnow()
    result = []
    for note in _load()["notes"]:
        if note["remind_at"] and not note["reminded"]:
            if datetime.strptime(note["remind_at"], DATETIME_FORMAT) <= now:
                result.append(note)
    return result


def mark_reminded(note_id: int):
    """Позначає нотатку як відправлену."""
    data = _load()
    for note in data["notes"]:
        if note["id"] == note_id:
            note["reminded"] = True
            break
    _save(data)
