# states.py — стани для покрокового діалогу (FSM)
#
# FSM (Finite State Machine) дозволяє боту вести діалог:
# крок 1 → бот питає текст нотатки
# крок 2 → бот питає чи потрібне нагадування
# крок 3 → якщо так, бот питає дату

from aiogram.fsm.state import State, StatesGroup


class AddNote(StatesGroup):
    waiting_for_text     = State()  # чекаємо текст нотатки
    waiting_for_reminder = State()  # чекаємо відповідь: так/ні нагадування
    waiting_for_date     = State()  # чекаємо дату нагадування
