# src/db/pool.py
import asyncpg

# объявляем и сразу инициализируем, чтобы имя pool реально существовало
pool: asyncpg.Pool | None = None

async def init_pool(
    db_name: str,
    db_user: str,
    db_pass: str,
    db_host: str,
    db_port: int
) -> None:
    """
    Создаёт пул соединений и сохраняет в атрибуте pool.
    """
    global pool
    pool = await asyncpg.create_pool(
        database=db_name,
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
        min_size=1,
        max_size=10
    )
