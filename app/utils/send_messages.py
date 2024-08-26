# Импорт необходимых модулей.
from aiogram.types import Message
from aiogram.exceptions import TelegramForbiddenError

from ..bot_settings import bot, logger
from ..data_base.requests import MyRequests


# Асинхронная функция отправки рассылки.
async def send_messages(ids: list[int], text: str, message: Message, type_message: str) -> None:
    """Асинхронная функция для отправки рассылки пользователям.\n
    В качестве аргументов принимает в себя список ID пользователей для рассылки,
    текст, объект класса Message и тип сообщения.\n
    Определяет тип сообщения для отправки по аргументу "type_message".
    Отправляет рассылку пользователям из списка, указанного в аргументах функции.\n\n """

    methods = {
        'text': lambda chat_id: bot.send_message(chat_id=chat_id, text=text),
        'photo': lambda chat_id: bot.send_photo(chat_id=chat_id, photo=message.photo[-1].file_id, caption=text),
        'video': lambda chat_id: bot.send_video(chat_id=chat_id, video=message.video.file_id, caption=text),
    }

    for user_id in ids:
        try:
            await methods[type_message](user_id)

        except TelegramForbiddenError:
            logger.info(f'Пользователь {user_id} заблокировал бота и был удален из базы данных.')

            await MyRequests.delete_items(table='Users', column_name='user_id', value=user_id)
