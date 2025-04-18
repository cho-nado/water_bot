from aiogram import Router, types
from aiogram import F

from ...db.crud import fetch_user_timezone, update_user_timezone
from ..keyboards import settings_menu, timezone_menu, main_menu

import logging
logger = logging.getLogger(__name__)


router = Router()

@router.message(lambda message: message.text == "⚙ Settings")
async def settings_entry(message: types.Message):
    logger.debug(f"[settings_entry] text={message.text!r}")
    await message.answer(
        "Customize your experience here – change your timezone, language or preferences 🛠️\n\n"
        "⚙ Settings:",
        reply_markup=settings_menu()
    )

@router.message(lambda message: message.text == "🌍 Time zone")
async def timezone_entry(message: types.Message):
    logger.debug(f"[timezone_entry] text={message.text!r}")
    current = await fetch_user_timezone(message.chat.id)
    await message.answer(
        "🌎 Choose your timezone so your reminders match your local time:",
        reply_markup=timezone_menu(current)
    )

@router.callback_query(lambda c: c.data.startswith("tz_"))
async def set_timezone(callback: types.CallbackQuery):
    logger.debug(f"[set_timezone] data={callback.data!r}")
    tz = callback.data[3:]
    await update_user_timezone(callback.message.chat.id, tz)
    # удаляем inline-клавиатуру
    await callback.message.delete()
    # подтверждаем и возвращаемся в Settings
    await callback.message.answer(
        f"✅ Timezone set to `{tz}`.",
        parse_mode="Markdown",
        reply_markup=settings_menu()
    )

@router.message(lambda message: message.text == "⬅️ Back")
async def back_from_settings(message: types.Message):
    logger.debug(f"[back_from_settings] text={message.text!r}")
    await message.answer("Back to main menu:", reply_markup=main_menu())
