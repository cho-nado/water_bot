from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    timezone = State()
    reminders = State()
    delete_reminder = State()
