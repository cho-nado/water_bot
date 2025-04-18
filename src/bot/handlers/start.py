# src/bot/handlers/start.py
import logging
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext

from ...db.crud import add_user, fetch_user_timezone, update_user_timezone
from ..keyboards import main_menu, timezone_menu
from ..states import Form

logger = logging.getLogger(__name__)
router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    logger.debug(f"[cmd_start] text={message.text!r} state={await state.get_state()!r}")
    # Добавляем или обновляем пользователя
    await add_user(message.chat.id, message.from_user.username or '')
    # Проверяем, установлен ли таймзона
    tz = await fetch_user_timezone(message.chat.id)
    if not tz:
        # Если нет — просим выбрать и переводим в состояние выбора
        await state.set_state(Form.timezone)
        await message.answer(
            "Please select your timezone:",
            reply_markup=timezone_menu()
        )
        return
    # Приветствие для пользователей с уже установленным таймзоном
    welcome_text = (
        "<b>👋 Welcome to Water Tracker Bot!</b>\n\n"
        "This bot helps you stay healthy and hydrated by:\n"
        "💧 Logging your water intake\n"
        "⏰ Setting up daily reminders\n"
        "📊 Checking your daily progress\n\n"
        "Stay consistent and drink enough water every day!\n\n"
        "Tap any button below to begin. Let's get hydrated together! 💙"
    )
    await message.answer(welcome_text, parse_mode="HTML", reply_markup=main_menu())

# Первичный выбор часового пояса после /start
@router.callback_query(F.data.startswith("tz_"), StateFilter(Form.timezone))
async def first_set_timezone(callback: types.CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    tz = callback.data[3:]
    # Сохраняем выбранный часовой пояс
    await update_user_timezone(chat_id, tz)
    await callback.message.delete()
    # Маленькое уведомление пользователю
    await callback.answer(f"✅ Timezone set to {tz}")
    # Приветственное сообщение после первоначальной установки
    welcome_text = (
        f"<b>✅ Your timezone has been set to {tz}</b>\n\n"
        "<b>👋 Welcome to Water Tracker Bot!</b>\n\n"
        "This bot helps you stay healthy and hydrated by:\n"
        "💧 Logging your water intake\n"
        "⏰ Setting up daily reminders\n"
        "📊 Checking your daily progress\n\n"
        "Stay consistent and drink enough water every day!\n\n"
        "Tap any button below to begin. Let's get hydrated together! 💙"
    )
    await callback.message.answer(welcome_text, parse_mode="HTML", reply_markup=main_menu())
    # Сбрасываем состояние
    await state.clear()

# Повторная смена часового пояса из настроек
@router.callback_query(F.data.startswith("tz_"))
async def change_timezone(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    tz = callback.data[3:]
    # Сохраняем новый часовой пояс
    await update_user_timezone(chat_id, tz)
    # Удаляем меню выбора часового пояса (inline)
    await callback.message.delete()
    # Отправляем обычное сообщение в чат с подтверждением и основным меню
    await callback.message.answer(
        f"✅ Timezone changed to {tz}",
        reply_markup=main_menu()
    )
