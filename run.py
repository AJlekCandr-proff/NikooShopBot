# Импорт необходимых модулей.
import asyncio

from aiogram import Dispatcher, Bot

from app.bot_settings import bot, logger
from app import router as root_router
from app.data_base.Engine import async_engine


# Асинхронная функция запуска бота.
async def main_func(main_bot: Bot) -> None:
    """Главная асинхронная функция.\n
    Запускает бота и обновляет базу данных.\n\n """

    dp = Dispatcher()

    dp.include_routers(root_router)

    logger.info('Bot successfully started!')

    try:
        await async_engine()
        await dp.start_polling(main_bot)

    finally:
        await main_bot.session.close()


# Конструкция "if __name__ == '__main__'".
if __name__ == '__main__':
    try:
        asyncio.run(main_func(bot))

    except KeyboardInterrupt:
        logger.info('Bot successfully finished!')
