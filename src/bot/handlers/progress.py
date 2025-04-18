import re
from aiogram import Router, types

from ...db.crud import record_progress, get_daily_progress
from ..keyboards import main_menu

import logging
logger = logging.getLogger(__name__)


router = Router()

@router.message(lambda message: bool(re.search(r"(\d+)\s*ml", message.text)))
async def log_water(message: types.Message):
    logger.debug(f"[log_water] text={message.text!r}")
    """
    Логирует выпитый объём воды.
    Срабатывает на любое сообщение, где есть число+ml.
    """
    match = re.search(r"(\d+)\s*ml", message.text)
    amount = int(match.group(1))
    await record_progress(message.chat.id, amount)
    await message.answer(
        f"Nice! You logged {amount} ml 💧\nKeep it up to stay hydrated 💪",
        reply_markup=main_menu()
    )

@router.message(lambda message: message.text == "📊 Check Progress")
async def show_progress(message: types.Message):
    logger.debug(f"[show_progress] text={message.text!r}")
    """
    Показывает прогресс за сегодня.
    """
    details, total = await get_daily_progress(message.chat.id)
    if details:
        await message.answer(
            f"📊 Today's progress:\n{details}\n\nTotal: {total} ml",
            reply_markup=main_menu()
        )
    else:
        await message.answer(
            "❌ No entries yet today. Start drinking!",
            reply_markup=main_menu()
        )
