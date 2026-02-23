# scheduler.py — планувальник нагадувань

import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import TIMEZONE
from database.json_db import get_pending_reminders, mark_reminded

logger = logging.getLogger(__name__)

_scheduler = AsyncIOScheduler(timezone=TIMEZONE)


async def _check_reminders(bot: Bot):
    """Перевіряє і надсилає нагадування. Запускається кожну хвилину."""
    for note in get_pending_reminders():
        try:
            await bot.send_message(
                chat_id=note["user_id"],
                text=f"🔔 <b>Нагадування!</b>\n\n{note['text']}",
                parse_mode="HTML",
            )
            mark_reminded(note["id"])
            logger.info(f"Нагадування #{note['id']} надіслано юзеру {note['user_id']}")
        except Exception as e:
            logger.error(f"Помилка надсилання нагадування #{note['id']}: {e}")


def start_scheduler(bot: Bot):
    _scheduler.add_job(
        _check_reminders,
        trigger="interval",
        minutes=1,
        args=[bot],
        id="reminder_check",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Планувальник запущено.")
