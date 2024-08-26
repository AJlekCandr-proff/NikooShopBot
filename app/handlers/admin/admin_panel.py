# Импорт необходимых модулей.
from aiogram import Router
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command

from app.views import msg_admin_panel, msg_error_admin_panel
from app.bot_settings import settings
from app.keyboards.inline_markup import AdminKb


# Инициализация роутера.
router = Router(name=__name__)


# Обработчик команды /admin.
@router.message(Command('admin'))
async def cmd_admin(message: Message, user_id: int = None) -> None:
    """Асинхронный обработчик команды "admin".\n
    Принимает в себя в качестве аргументов объект класса Message и ID пользователя.\n
    Отправляет приветственное сообщение администратору и открывает панель для управления.\n\n """

    user_id = user_id if user_id else message.from_user.id

    if user_id == int(settings.ADMIN_ID.get_secret_value()):
        await message.delete()

        await message.answer_photo(
            photo=BufferedInputFile(
                file=open('app/media/Base/StartPhoto.png', 'rb').read(),
                filename='Admin.jpg',
            ),
            caption=msg_admin_panel(),
            reply_markup=AdminKb(rows=1),
        )
    else:
        await message.answer(text=msg_error_admin_panel())
