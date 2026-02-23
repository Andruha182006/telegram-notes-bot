# handlers/notes.py — додавання (FSM), перегляд, видалення

from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import DATETIME_FORMAT
from database.json_db import add_note, delete_note, get_notes
from keyboards import ask_reminder_keyboard, main_menu, note_actions_keyboard, remove_keyboard
from states import AddNote

router = Router()


# ── ДОДАВАННЯ НОТАТКИ — покроковий FSM-діалог ───────────────────────────────

@router.message(F.text == "📝 Додати нотатку")
@router.message(Command("add"))
async def cmd_add_start(message: Message, state: FSMContext):
    """Крок 1 — просимо ввести текст нотатки."""
    await state.set_state(AddNote.waiting_for_text)
    await message.answer(
        "📝 <b>Введіть текст нотатки:</b>\n\n"
        "<i>Наприклад: Зателефонувати Олегу</i>",
        reply_markup=remove_keyboard(),  # ховаємо меню під час діалогу
    )


@router.message(AddNote.waiting_for_text)
async def fsm_get_text(message: Message, state: FSMContext):
    """Крок 2 — отримали текст, питаємо про нагадування."""
    text = message.text.strip()

    if not text:
        await message.answer("⚠️ Текст не може бути порожнім. Спробуйте ще раз:")
        return

    # Зберігаємо текст у стані FSM (тимчасова пам'ять діалогу)
    await state.update_data(note_text=text)
    await state.set_state(AddNote.waiting_for_reminder)

    await message.answer(
        f"✏️ <b>Нотатка:</b> {text}\n\n"
        "⏰ Додати нагадування?",
        reply_markup=ask_reminder_keyboard(),
    )


@router.message(AddNote.waiting_for_reminder, F.text == "✅ Ні, зберегти без нагадування")
async def fsm_no_reminder(message: Message, state: FSMContext):
    """Користувач відмовився від нагадування — зберігаємо одразу."""
    data = await state.get_data()
    note_id = add_note(
        user_id=message.from_user.id,
        text=data["note_text"],
        remind_at=None,
    )
    await state.clear()  # очищаємо FSM-стан
    await message.answer(
        f"✅ <b>Нотатку #{note_id} збережено!</b>\n"
        f"📝 {data['note_text']}",
        reply_markup=main_menu(),
    )


@router.message(AddNote.waiting_for_reminder, F.text == "⏰ Так, додати нагадування")
async def fsm_want_reminder(message: Message, state: FSMContext):
    """Крок 3 — користувач хоче нагадування, питаємо дату."""
    await state.set_state(AddNote.waiting_for_date)
    await message.answer(
        "📅 <b>Введіть дату та час нагадування:</b>\n\n"
        "Формат: <code>YYYY-MM-DD HH:MM</code>\n"
        "Приклад: <code>2025-12-31 09:00</code>\n\n"
        "<i>Час — UTC (Київ = UTC+2 влітку, UTC+3 взимку)</i>",
        reply_markup=remove_keyboard(),
    )


@router.message(AddNote.waiting_for_date)
async def fsm_get_date(message: Message, state: FSMContext):
    """Отримали дату — валідуємо і зберігаємо нотатку."""
    date_str = message.text.strip()

    # Перевіряємо формат
    try:
        remind_dt = datetime.strptime(date_str, DATETIME_FORMAT)
    except ValueError:
        await message.answer(
            "⚠️ Неправильний формат.\n"
            "Введіть у форматі: <code>YYYY-MM-DD HH:MM</code>\n"
            "Наприклад: <code>2025-06-01 09:00</code>"
        )
        return

    # Перевіряємо що дата у майбутньому
    if remind_dt <= datetime.utcnow():
        await message.answer(
            "⚠️ Дата має бути у майбутньому. Спробуйте ще раз:"
        )
        return

    data = await state.get_data()
    note_id = add_note(
        user_id=message.from_user.id,
        text=data["note_text"],
        remind_at=date_str,
    )
    await state.clear()

    await message.answer(
        f"✅ <b>Нотатку #{note_id} збережено!</b>\n"
        f"📝 {data['note_text']}\n"
        f"⏰ Нагадаю: {date_str} UTC",
        reply_markup=main_menu(),
    )


@router.message(AddNote.waiting_for_reminder, F.text == "❌ Скасувати")
@router.message(AddNote.waiting_for_date, F.text == "❌ Скасувати")
async def fsm_cancel(message: Message, state: FSMContext):
    """Скасування на будь-якому кроці діалогу."""
    await state.clear()
    await message.answer("❌ Додавання скасовано.", reply_markup=main_menu())


# ── ПЕРЕГЛЯД НОТАТОК ─────────────────────────────────────────────────────────

@router.message(F.text == "📋 Мої нотатки")
@router.message(Command("list"))
async def cmd_list(message: Message):
    """
    Виводить кожну нотатку окремим повідомленням
    з інлайн-кнопкою "🗑 Видалити" під кожною.
    """
    notes = get_notes(user_id=message.from_user.id)

    if not notes:
        await message.answer(
            "📋 Нотаток поки немає.\n"
            "Натисніть <b>📝 Додати нотатку</b>",
            reply_markup=main_menu(),
        )
        return

    await message.answer(
        f"📋 <b>Ваші нотатки ({len(notes)}):</b>",
        reply_markup=main_menu(),
    )

    # Кожна нотатка — окреме повідомлення з кнопкою видалення
    for note in notes:
        if note["remind_at"]:
            status = "✅ нагадування надіслано" if note["reminded"] else f"⏰ {note['remind_at']} UTC"
        else:
            status = "без нагадування"

        text = (
            f"<b>#{note['id']}</b> {note['text']}\n"
            f"<i>{status}</i>"
        )
        await message.answer(
            text,
            reply_markup=note_actions_keyboard(note["id"]),  # кнопка "Видалити"
        )


# ── ВИДАЛЕННЯ через інлайн-кнопку ────────────────────────────────────────────

@router.callback_query(F.data.startswith("delete:"))
async def callback_delete(callback: CallbackQuery):
    """
    Спрацьовує коли користувач натискає "🗑 Видалити" під нотаткою.
    callback.data має формат "delete:5" де 5 — ID нотатки.
    """
    note_id = int(callback.data.split(":")[1])
    deleted = delete_note(user_id=callback.from_user.id, note_id=note_id)

    if deleted:
        # Редагуємо повідомлення — прибираємо кнопку і показуємо статус
        await callback.message.edit_text(
            callback.message.text + "\n\n<i>🗑 Видалено</i>"
        )
    else:
        await callback.answer("⚠️ Нотатку не знайдено.", show_alert=True)

    # Прибираємо "годинник" на кнопці після натискання
    await callback.answer()
