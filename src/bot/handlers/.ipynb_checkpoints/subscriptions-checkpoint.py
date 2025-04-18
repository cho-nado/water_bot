from aiogram import Router, types

from ..keyboards import subscription_menu, main_menu

import logging
logger = logging.getLogger(__name__)


router = Router()

@router.message(lambda message: message.text == "💵 Subscription")
async def subscription_handler(message: types.Message):
    logger.debug(f"[subscription_handler] text={message.text!r}")
    text = (
        "<b>🌟 Support the Project</b>\n\n"
        "This bot is currently <i>100% free</i> and always will be.\n"
        "If you'd like to support its development and get new features faster — you can make a small donation 🙌\n\n"
        "<b>💸 Donate here:</b>\n"
        "<a href='https://www.donationalerts.com/r/ilartstu_bots'>https://www.donationalerts.com/r/ilartstu_bots</a>\n\n"
        "Every drop counts 💧 Thank you for your support and for staying hydrated with us! 💙"
    )
    await message.answer(
        text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=subscription_menu()
    )

@router.message(lambda message: message.text == "⬅️ Back")
async def back_from_subscription(message: types.Message):
    logger.debug(f"[back_from_subscription] text={message.text!r}")
    # Возврат в главное меню
    await message.answer("Returning to main menu.", reply_markup=main_menu())
