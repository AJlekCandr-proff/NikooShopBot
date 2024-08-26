# Импорт необходимых модулей.
from aiogram import Router
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import CommandStart

from app.views import msg_start
from app.data_base.requests import MyRequests
from app.keyboards.inline_markup import MainMenu


# Инициализация роутера.
router = Router(name=__name__)


# Обработчик команды /start.
@router.message(CommandStart())
async def cmd_start(message: Message, *args) -> None:
    """Присылает приветствие и меню для пользователя.
    Добавляет пользователя в базу данных. """

    if args:
        user_id = args[0]
        full_name = args[1]
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
    user = await MyRequests.get_line('Users', 'user_id', user_id)

    if not user:
        await MyRequests.add_items(
            'Users',
            user_id=user_id,
            name=full_name,
        )
