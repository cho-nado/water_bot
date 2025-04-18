# src/db/crud.py
"""
CRUD-операции для работы с базой через пул соединений.
"""
import pytz
from datetime import datetime
from . import pool as pool_module
from typing import Optional, List, Tuple

async def init_db() -> None:
    """
    Инициализирует схему и таблицы в базе данных.
    Обязательно вызвать после init_pool().
    """
    if pool_module.pool is None:
        raise RuntimeError("Database pool is not initialized")
    async with pool_module.pool.acquire() as conn:
        await conn.execute('CREATE SCHEMA IF NOT EXISTS water_schema')
        await conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS water_schema.users (
                id SERIAL PRIMARY KEY,
                chat_id BIGINT UNIQUE,
                username TEXT,
                reminders TEXT DEFAULT '08:00,12:00,18:00',
                timezone TEXT
            )
            '''
        )
        await conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS water_schema.progress (
                user_id INTEGER REFERENCES water_schema.users(id),
                date DATE,
                time TIME,
                amount INTEGER,
                PRIMARY KEY (user_id, date, time)
            )
            '''
        )

async def add_user(chat_id: int, username: str) -> None:
    """Добавляет или обновляет пользователя в базе."""
    if pool_module.pool is None:
        raise RuntimeError("Database pool is not initialized")
    async with pool_module.pool.acquire() as conn:
        await conn.execute(
            '''
            INSERT INTO water_schema.users (chat_id, username)
            VALUES ($1, $2)
            ON CONFLICT (chat_id) DO UPDATE SET username = EXCLUDED.username
            ''', chat_id, username
        )

async def fetch_user_timezone(chat_id: int) -> Optional[str]:
    """Возвращает сохранённый часовой пояс пользователя."""
    if pool_module.pool is None:
        raise RuntimeError("Database pool is not initialized")
    async with pool_module.pool.acquire() as conn:
        row = await conn.fetchrow(
            'SELECT timezone FROM water_schema.users WHERE chat_id = $1', chat_id
        )
    return row['timezone'] if row else None

async def update_user_timezone(chat_id: int, timezone: str) -> None:
    """Обновляет часовой пояс пользователя."""
    if pool_module.pool is None:
        raise RuntimeError("Database pool is not initialized")
    async with pool_module.pool.acquire() as conn:
        await conn.execute(
            'UPDATE water_schema.users SET timezone = $1 WHERE chat_id = $2', timezone, chat_id
        )

async def fetch_user_reminders() -> List[Tuple[int, str]]:
    """Возвращает список (chat_id, reminders)."""
    if pool_module.pool is None:
        raise RuntimeError("Database pool is not initialized")
    async with pool_module.pool.acquire() as conn:
        rows = await conn.fetch('SELECT chat_id, reminders FROM water_schema.users')
    return [(r['chat_id'], r['reminders']) for r in rows]

async def update_user_reminders(chat_id: int, reminders: str) -> None:
    """Сохраняет список напоминаний пользователя."""
    if pool_module.pool is None:
        raise RuntimeError("Database pool is not initialized")
    async with pool_module.pool.acquire() as conn:
        await conn.execute(
            'UPDATE water_schema.users SET reminders = $1 WHERE chat_id = $2', reminders, chat_id
        )

async def clear_user_reminders(chat_id: int) -> None:
    """Очищает все напоминания пользователя."""
    if pool_module.pool is None:
        raise RuntimeError("Database pool is not initialized")
    async with pool_module.pool.acquire() as conn:
        await conn.execute(
            'UPDATE water_schema.users SET reminders = $1 WHERE chat_id = $2', '', chat_id
        )

async def delete_specific_reminder(chat_id: int, time_str: str) -> bool:
    """Удаляет одно напоминание. Возвращает True, если удалено."""
    if pool_module.pool is None:
        raise RuntimeError("Database pool is not initialized")
    async with pool_module.pool.acquire() as conn:
        row = await conn.fetchrow(
            'SELECT reminders FROM water_schema.users WHERE chat_id = $1', chat_id
        )
        if not row or not row['reminders']:
            return False
        parts = row['reminders'].split(',')
        if time_str not in parts:
            return False
        parts.remove(time_str)
        new_val = ','.join(parts)
        await conn.execute(
            'UPDATE water_schema.users SET reminders = $1 WHERE chat_id = $2', new_val, chat_id
        )
    return True

async def record_progress(chat_id: int, amount: int) -> None:
    """
    Записывает прогресс пользователя с точным временем HH:MM:SS по его часовому поясу.
    """
    if pool_module.pool is None:
        raise RuntimeError("Database pool is not initialized")
    tz_name = await fetch_user_timezone(chat_id)
    try:
        user_tz = pytz.timezone(tz_name) if tz_name else pytz.timezone('Europe/Moscow')
    except pytz.UnknownTimeZoneError:
        user_tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(user_tz)
    date_val = now.date()
    time_val = now.time()
    async with pool_module.pool.acquire() as conn:
        user = await conn.fetchrow(
            'SELECT id FROM water_schema.users WHERE chat_id = $1', chat_id
        )
        if user:
            await conn.execute(
                'INSERT INTO water_schema.progress (user_id, date, time, amount) VALUES ($1, $2, $3, $4)',
                user['id'], date_val, time_val, amount
            )

async def get_daily_progress(chat_id: int) -> Tuple[Optional[str], int]:
    """
    Возвращает подробности и общий объём для текущего дня с учётом часового пояса.
    """
    if pool_module.pool is None:
        raise RuntimeError("Database pool is not initialized")
    tz_name = await fetch_user_timezone(chat_id)
    try:
        user_tz = pytz.timezone(tz_name) if tz_name else pytz.timezone('Europe/Moscow')
    except pytz.UnknownTimeZoneError:
        user_tz = pytz.timezone('Europe/Moscow')
    today = datetime.now(user_tz).date()
    async with pool_module.pool.acquire() as conn:
        user = await conn.fetchrow(
            'SELECT id FROM water_schema.users WHERE chat_id = $1', chat_id
        )
        if not user:
            return None, 0
        entries = await conn.fetch(
            'SELECT time, amount FROM water_schema.progress WHERE user_id = $1 AND date = $2 ORDER BY time',
            user['id'], today
        )
    total = sum(e['amount'] for e in entries)
    details = '\n'.join(f"{e['amount']} ml at {e['time'].strftime('%H:%M:%S')}" for e in entries)
    return details, total
