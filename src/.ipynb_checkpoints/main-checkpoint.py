# src/main.py
import asyncio
import logging

from aiogram import Bot, Dispatcher

# Импорт конфигурации
from .config import TELEGRAM_TOKEN, DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT
# Инициализация пула и БД
from .db.pool import init_pool
from .db.crud import init_db
# Планировщик
from .utils.scheduler import clear_and_reschedule_reminders
# Хендлеры бота
from .bot.handlers import register_handlers
from .bot.middlewares import DbMiddleware

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logging.getLogger("aiogram").setLevel(logging.DEBUG)


async def main():
    # 1) Инициализируем пул соединений
    await init_pool(
        db_name=DB_NAME,
        db_user=DB_USER,
        db_pass=DB_PASS,
        db_host=DB_HOST,
        db_port=DB_PORT,
    )
    # 2) Инициализируем БД (создаем схему и таблицы)
    await init_db()

    # 3) Запускаем бота и диспетчер
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()
    dp.message.middleware(DbMiddleware())

    # 4) Регистрируем все хендлеры
    register_handlers(dp)

    # 5) Настраиваем и запускаем планировщик
    await clear_and_reschedule_reminders()

    # 6) Запускаем поллинг
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
