# Импорт необходимых модулей.
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from .user.user_cmd_start import cmd_start
from .admin.admin_panel import cmd_admin


# Инициализация роутера.
router = Router(name=__name__)


# Обработчик нажатия кнопки "Главное меню 🏠".
@router.callback_query(F.data == 'main_menu')
async def send_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """Асинхронный обработчик нажатия кнопки "Главное меню 🏠".\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery и FSMContext.\n
    Направляет пользователя в главное меню и очищает состояние FSM.\n\n """

    await state.clear()

    await cmd_start(message=callback.message, *[callback.from_user.id, callback.from_user.full_name])


# Обработчик кнопки "В панель 🏠".
@router.callback_query(F.data == 'panel')
async def send_panel(callback: CallbackQuery, state: FSMContext) -> None:
    """Асинхронный обработчик нажатия кнопки "В панель 🏠".\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery и FSMContext.\n
    Возвращает администратора в панель управления и очищает состояние FSM.\n\n """

    await state.clear()

    await cmd_admin(message=callback.message, user_id=callback.from_user.id)
