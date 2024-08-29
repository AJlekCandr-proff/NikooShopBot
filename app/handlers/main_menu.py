from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from .user.user_cmd_start import cmd_start
from .admin.admin_panel import cmd_admin


router = Router(name=__name__)


@router.callback_query(F.data == 'main_menu')
async def send_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Асинхронный обработчик нажатия кнопки "Главное меню 🏠".
    Направляет пользователя в главное меню и очищает состояние FSM.

    :param callback: Объект класса CallbackQuery.
    :param state: Объект класса FSMContext.
    """

    await state.clear()

    await cmd_start(message=callback.message, user_id=callback.from_user.id, full_name=callback.from_user.full_name)


@router.callback_query(F.data == 'panel')
async def send_panel(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Асинхронный обработчик нажатия кнопки "В панель 🏠".
    Возвращает администратора в панель управления и очищает состояние FSM.

    :param callback: Объект класса CallbackQuery.
    :param state: Объект класса FSMContext.
    """

    await state.clear()

    await cmd_admin(message=callback.message, user_id=callback.from_user.id)
