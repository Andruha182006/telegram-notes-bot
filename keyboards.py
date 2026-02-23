# keyboards.py — всі клавіатури в одному місці

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

# ── Головне меню (завжди видно внизу екрану) ────────────────────────────────

def main_menu() -> ReplyKeyboardMarkup:
    """
    Постійна клавіатура внизу екрану.
    Користувач бачить її завжди і просто тапає кнопку.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📝 Додати нотатку"),
                KeyboardButton(text="📋 Мої нотатки"),
            ],
            [
                KeyboardButton(text="❓ Допомога"),
            ],
        ],
        resize_keyboard=True,       # менший розмір кнопок
        input_field_placeholder="Оберіть дію або введіть команду...",
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    """Прибирає клавіатуру (використовується під час FSM-діалогу)."""
    return ReplyKeyboardRemove()


# ── Клавіатура вибору — додавати нагадування чи ні ─────────────────────────

def ask_reminder_keyboard() -> ReplyKeyboardMarkup:
    """Питаємо користувача чи потрібне нагадування."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="⏰ Так, додати нагадування"),
                KeyboardButton(text="✅ Ні, зберегти без нагадування"),
            ],
            [
                KeyboardButton(text="❌ Скасувати"),
            ],
        ],
        resize_keyboard=True,
    )


# ── Інлайн-кнопка "Видалити" під кожною нотаткою ───────────────────────────

def note_actions_keyboard(note_id: int) -> InlineKeyboardMarkup:
    """
    Інлайн-кнопки прямо під повідомленням з нотаткою.
    callback_data містить ID нотатки щоб знати яку видаляти.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗑 Видалити",
                    callback_data=f"delete:{note_id}",
                )
            ]
        ]
    )
