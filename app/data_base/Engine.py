from .Models.base import Base
from app.bot_settings import engine


async def async_engine() -> None:
    """Подключает и обновляет базу данных. """

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
