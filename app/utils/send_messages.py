from aiogram.types import Message
from aiogram.exceptions import TelegramForbiddenError

from ..bot_settings import NikooShopBot, logger
from ..data_base.requests import MyRequests


async def send_messages(ids: list[int], text: str, message: Message, type_message: str) -> None:
    """
    Асинхронная функция для отправки рассылки пользователям.
    Определяет тип сообщения для отправки по аргументу "type_message".
    Отправляет рассылку пользователям из списка, указанного в аргументах функции.

    :param ids: Список ID пользователей для рассылки.
    :param text: Текст сообщения-рассылки.
    :param message: Объект класса Message.
    :param type_message: Тип отправляемого сообщения.
    """

    methods = {
        'text': lambda chat_id: NikooShopBot.send_message(chat_id=chat_id, text=text),
        'photo': lambda chat_id: NikooShopBot.send_photo(chat_id=chat_id, photo=message.photo[-1].file_id, caption=text),
        'video': lambda chat_id: NikooShopBot.send_video(chat_id=chat_id, video=message.video.file_id, caption=text),
    }

    for user_id in ids:
        try:
            await methods[type_message](user_id)

        except TelegramForbiddenError:
            logger.info(f'Пользователь {user_id} заблокировал бота и был удален из базы данных.')

            await MyRequests.delete_items(table='Users', column_name='user_id', value=user_id)
