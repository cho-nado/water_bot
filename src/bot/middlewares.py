# src/bot/middlewares.py
import logging
from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware

from ..db.crud import add_user    # <- здесь две точки, не три

logger = logging.getLogger(__name__)

class DbMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, types.Message):
            chat_id   = event.chat.id
            username  = event.from_user.username or ""
            try:
                await add_user(chat_id, username)
                logger.debug(f"[DbMiddleware] ensured user {chat_id} in DB")
            except Exception as e:
                logger.error(f"[DbMiddleware] failed to add_user: {e}")
        return await handler(event, data)
