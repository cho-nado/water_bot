# src/utils/scheduler.py
import logging
from datetime import datetime

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

from ..config import TELEGRAM_TOKEN
from ..db.crud import fetch_user_reminders, fetch_user_timezone

logger = logging.getLogger(__name__)

# Создаём планировщик и бот для отправки сообщений
scheduler = AsyncIOScheduler()
bot = Bot(token=TELEGRAM_TOKEN)

async def send_reminder(chat_id: int):
    """
    Отправляет напоминание о питье воды пользователю.
    """
    tz_value = await fetch_user_timezone(chat_id)
    try:
        user_tz = pytz.timezone(tz_value) if tz_value else pytz.timezone("Europe/Moscow")
    except Exception:
        user_tz = pytz.timezone("Europe/Moscow")

    now_str = datetime.now(user_tz).strftime("%H:%M")
    try:
        await bot.send_message(chat_id, f"Reminder: Drink water! 💧 ({now_str})")
        logger.info(f"✅ Sent reminder to {chat_id} at {now_str}")
    except Exception as e:
        logger.error(f"❌ Failed to send to {chat_id}: {e}")

async def reschedule_user_reminders(chat_id: int):
    """
    Пересоздаёт cron-задачи для заданного пользователя.
    """
    # Удаляем старые
    for job in scheduler.get_jobs():
        if job.id.startswith(f"reminder_{chat_id}_"):
            scheduler.remove_job(job.id)

    rows = await fetch_user_reminders()
    user_row = next((r for r in rows if r[0] == chat_id), None)
    if not user_row or not user_row[1]:
        return
    times = user_row[1].split(",")

    tz_value = await fetch_user_timezone(chat_id)
    try:
        user_tz = pytz.timezone(tz_value) if tz_value else pytz.timezone("Europe/Moscow")
    except Exception:
        user_tz = pytz.timezone("Europe/Moscow")

    for t in times:
        hour, minute = map(int, t.split(':'))
        job_id = f"reminder_{chat_id}_{t.replace(':','')}"
        scheduler.add_job(
            send_reminder,
            trigger="cron",
            hour=hour,
            minute=minute,
            timezone=user_tz,
            args=[chat_id],
            id=job_id,
            replace_existing=True
        )
        logger.info(f"📅 Scheduled reminder for {chat_id} at {t} ({user_tz})")

async def clear_and_reschedule_reminders():
    """
    Очищает все задачи и пересоздаёт для всех пользователей при старте.
    """
    scheduler.remove_all_jobs()
    rows = await fetch_user_reminders()
    for chat_id, _ in rows:
        await reschedule_user_reminders(chat_id)
    scheduler.start()
    logger.info("🚀 Scheduler started and all reminders scheduled")
