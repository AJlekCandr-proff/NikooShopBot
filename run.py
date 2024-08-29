import asyncio

from aiogram import Dispatcher, Bot

from app.bot_settings import NikooShopBot, Logger
from app import router as root_router
from app.data_base.Engine import async_engine


async def main_func(bot: Bot) -> None:
    """Главная асинхронная функция.
    Запускает бота и обновляет базу данных.

    :param bot: Объект класса Bot.
    """

    dp = Dispatcher()

    dp.include_routers(root_router)

    Logger.info('Bot successfully started!')

    try:
        await async_engine()
        await dp.start_polling(bot)

    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main_func(NikooShopBot))

    except KeyboardInterrupt:
        Logger.info('Bot successfully finished!')
