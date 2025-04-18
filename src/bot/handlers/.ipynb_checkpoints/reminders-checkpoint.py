# src/bot/handlers/reminders.py
import re
import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from aiogram.types import ReplyKeyboardRemove

from ...db.crud import (
    fetch_user_reminders,
    update_user_reminders,
    clear_user_reminders,
    delete_specific_reminder,
)
from ..keyboards import reminder_menu, main_menu
from ..states import Form
from ...utils.scheduler import reschedule_user_reminders

logger = logging.getLogger(__name__)
router = Router()

@router.message(lambda message: message.text == "⏰ Reminders")
async def reminders_entry(message: types.Message):
    logger.debug(f"[reminders_entry] text={message.text!r}")
    await message.answer(
        "Set up hydration reminders so you never forget to drink water 🧠💧\n\n"
        "Reminder settings:",
        reply_markup=reminder_menu()
    )

@router.message(lambda message: message.text == "🕐 Add Reminders")
async def add_reminders_start(message: types.Message, state: FSMContext):
    logger.debug(f"[add_reminders_start] text={message.text!r} state before={await state.get_state()!r}")
    await state.set_state(Form.reminders)
    await message.answer(
        "Please send the times you want to be reminded like:\n\n"
        "08:00 14:00 20:00\n\n"
        "⏰ Use 24h format. Separate times with spaces.",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(StateFilter(Form.reminders))
async def process_reminders(message: types.Message, state: FSMContext):
    logger.debug(f"[process_reminders] state={await state.get_state()!r} text={message.text!r}")
    # Новые введённые времена
    new_times = message.text.strip().split()
    # Проверка формата
    if not all(len(t) == 5 and t[2] == ':' and t.replace(':', '').isdigit() for t in new_times):
        await message.reply(
            "Invalid format. Use hh:mm like 08:00 14:00 (leading zero is required)",
            reply_markup=reminder_menu()
        )
        await state.clear()
        return
    # Получаем существующие напоминания из БД
    rows = await fetch_user_reminders()
    current = next((r for r in rows if r[0] == message.chat.id), None)
    existing = current[1].split(',') if current and current[1] else []
    # Объединяем списки, убираем дубликаты и сортируем
    combined = sorted(set(existing + new_times))
    # Обновляем в БД
    await update_user_reminders(message.chat.id, ",".join(combined))
    # Перенастройка планировщика
    await reschedule_user_reminders(message.chat.id)

    await message.reply("Reminders updated!", reply_markup=reminder_menu())
    await state.clear()

@router.message(lambda message: message.text == "📋 Show Reminders")
async def show_reminders(message: types.Message):
    logger.debug(f"[show_reminders] text={message.text!r}")
    rows = await fetch_user_reminders()
    row = next((r for r in rows if r[0] == message.chat.id), None)
    if row and row[1]:
        formatted = "\n".join(f"- {t}" for t in row[1].split(","))
        await message.answer(f"✅ Your reminders:\n{formatted}", reply_markup=reminder_menu())
    else:
        await message.answer("❌ You have no reminders set.", reply_markup=reminder_menu())

@router.message(lambda message: message.text == "🗑️ Delete All")
async def delete_all(message: types.Message):
    logger.debug(f"[delete_all] text={message.text!r}")
    await clear_user_reminders(message.chat.id)
    await reschedule_user_reminders(message.chat.id)
    await message.answer("🗑️ All reminders deleted.", reply_markup=reminder_menu())

@router.message(lambda message: message.text == "✂️ Delete Specific")
async def delete_specific_start(message: types.Message, state: FSMContext):
    logger.debug(f"[delete_specific_start] text={message.text!r} state before={await state.get_state()!r}")
    await state.set_state(Form.delete_reminder)
    await message.answer(
        "⌛ Enter the time hh:mm (like 13:00) of the reminder you want to delete:",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(StateFilter(Form.delete_reminder))
async def process_delete_specific(message: types.Message, state: FSMContext):
    logger.debug(f"[process_delete_specific] state={await state.get_state()!r} text={message.text!r}")
    t = message.text.strip()
    if not (len(t) == 5 and t[2] == ':' and t.replace(':', '').isdigit()):
        await message.reply("Invalid format. Use hh:mm like 08:00. Try again:", reply_markup=reminder_menu())
        await state.clear()
        return
    ok = await delete_specific_reminder(message.chat.id, t)
    if ok:
        await reschedule_user_reminders(message.chat.id)
        await message.reply("Reminder deleted.", reply_markup=reminder_menu())
    else:
        await message.reply("This reminder does not exist. Try again:", reply_markup=reminder_menu())
    await state.clear()

@router.message(lambda message: message.text == "⬅️ Back")
async def back_from_reminders(message: types.Message, state: FSMContext):
    logger.debug(f"[back_from_reminders] text={message.text!r} state before={await state.get_state()!r}")
    await state.clear()
    await message.answer("Back to main menu:", reply_markup=main_menu())
