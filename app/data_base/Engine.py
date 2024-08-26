# -*- coding: utf-8 -*-


# Импорт необходимых модулей.
from .Models.base import Base
from app.bot_settings import engine


# Функция подключения к базе данных.
async def async_engine():
    """Подключает и обновляет базу данных"""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
