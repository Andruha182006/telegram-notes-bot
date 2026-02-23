# handlers/common.py — /start, /help та кнопка "Допомога"

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from keyboards import main_menu

router = Router()

HELP_TEXT = (
    "👋 <b>Привіт! Я бот для нотаток та нагадувань.</b>\n\n"
    "Просто натискай кнопки внизу екрану 👇\n\n"
    "<b>📝 Додати нотатку</b> — бот запитає текст і час\n"
    "<b>📋 Мої нотатки</b> — список усіх нотаток з кнопкою видалення\n\n"
    "<i>Також працюють команди: /add, /list</i>"
)


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(HELP_TEXT, reply_markup=main_menu())


@router.message(F.text == "❓ Допомога")
@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT, reply_markup=main_menu())
