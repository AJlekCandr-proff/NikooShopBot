from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.data_base.requests import MyRequests
from app.keyboards.inline_markup import StatisticKb


router = Router(name=__name__)


@router.callback_query(F.data == 'statistic')
async def statistic(callback: CallbackQuery) -> None:
    """
    Асинхронный обработчик нажатия кнопки "Статистика 📊".
    Присылает данные профиля пользователей в боте (Telegram ID, полное имя пользователя и баланс)
    для администратора списком.

    :param callback: Объект класса CallbackQuery.
    """

    users: list[tuple[int, str, float]] = await MyRequests.get_columns(
        table='Users',
        columns_name=['user_id', 'name', 'balance']
    )
    count_users = len(users)
    text: str = '\n'.join(f'🆔 <code>{users[0]}</code> | 👤 <a href="user?id={users[0]}">{users[1]}</a> | 💰 {users[2]}' for users in users)

    await callback.message.edit_caption(
        caption='📊 Статистика бота: Пользователи 👤\n\n'
                f'{text}\n\n'
                f'<b>Всего пользователей:</b> {count_users}',
        reply_markup=StatisticKb(rows=1),
    )
