# src/bot/handlers/__init__.py
"""
Регистрация всех роутеров (хендлеров) бота.
"""
from aiogram import Dispatcher

from .start import router as start_router
from .subscriptions import router as subscriptions_router
from .progress import router as progress_router
from .reminders import router as reminders_router
from .settings import router as settings_router


def register_handlers(dp: Dispatcher) -> None:
    # Основной хендлер старта
    dp.include_router(start_router)
    # Подписка/донаты
    dp.include_router(subscriptions_router)
    # Логирование прогресса
    dp.include_router(progress_router)
    # Напоминания
    dp.include_router(reminders_router)
    # Настройки (таймзона)
    dp.include_router(settings_router)
