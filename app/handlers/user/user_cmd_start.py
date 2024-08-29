from aiogram import Router
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import CommandStart

from app.views import msg_start
from app.data_base.requests import MyRequests
from app.keyboards.inline_markup import MainMenu


router = Router(name=__name__)


@router.message(CommandStart())
async def cmd_start(message: Message, user_id: int = None, full_name: str = None) -> None:
    """
    Асинхронный обработчик команды /start.
    Присылает приветствие и меню для пользователя. Добавляет пользователя в базу данных.

    :param message: Объект класса Message.
    :param user_id: ID пользователя.
    :param full_name: Полное имя пользователя.
    """

    if user_id and full_name:
        user_id = user_id
        full_name = full_name
    else:
        user_id = message.from_user.id
        full_name = message.from_user.full_name

    await message.answer_photo(
        photo=BufferedInputFile(
            file=open('app/media/Base/StartPhoto.png', 'rb').read(),
            filename='StartPhoto.jpg',
        ),
        caption=msg_start(user_id, full_name),
        reply_markup=MainMenu(2),
    )
    user = await MyRequests.get_line(table='Users', column_name='user_id', value=user_id)

    if not user:
        await MyRequests.add_items(table='Users', user_id=user_id, name=full_name)
