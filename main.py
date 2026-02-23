# main.py — точка входу

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database.json_db import init_db
from handlers import common, notes
from scheduler import start_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


async def main():
    init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )

    # MemoryStorage зберігає FSM-стани в пам'яті (достатньо для старту)
    dp = Dispatcher(storage=MemoryStorage())

    # Порядок важливий: common останнім, бо там catch-all хендлер
    dp.include_router(notes.router)
    dp.include_router(common.router)

    start_scheduler(bot)

    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
