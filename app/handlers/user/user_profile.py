# Импорт необходимых модулей.
from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile

from app.data_base.requests import MyRequests
from app.keyboards.inline_markup import MenuProfileKb


# Инициализация роутера.
router = Router(name=__name__)


# Обработчик кнопки "Профиль 👤".
@router.callback_query(F.data == 'Profile')
async def send_profile(callback: CallbackQuery) -> None:
    """Асинхронный обработчик нажатия кнопки "Профиль 👤".\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery.\n
    Присылает данные профиля пользователя в боте: Telegram ID, полное имя пользователя и баланс.\n\n """

    await callback.message.delete()

    user = await MyRequests.get_line(table='Users', column_name='user_id', value=callback.from_user.id)

    await callback.message.answer_photo(
        photo=BufferedInputFile(
            file=open('app/media/Base/Profile.png', 'rb').read(),
            filename='profile.png',

        ),
        caption=f'📌 <a href="tg: user?id={user.user_id}"><i>{user.name}</i></a>, твой профиль 📊\n\n'
                f'🆔 Telegram: <ins>{user.user_id}</ins>\n'
                f'👤 Имя: {user.name}\n'
                f'💸 Balance: {user.balance} ₽\n\n',
        reply_markup=MenuProfileKb(rows=1),
    )
