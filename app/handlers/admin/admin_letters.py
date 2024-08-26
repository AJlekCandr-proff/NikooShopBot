# Импорт необходимых модулей.
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from .admin_panel import cmd_admin
from app.utils.send_messages import send_messages
from app.data_base.requests import MyRequests


# Инициализация роутера.
router = Router(name=__name__)


# Класс FSM.
class States(StatesGroup):
    """Хранит в себе состояния FSM для рассылки. """

    get_message = State()


# Обработчик нажатия кнопки "Рассылка 📣".
@router.callback_query(F.data == 'send_letters')
async def send_massage(callback: CallbackQuery, state: FSMContext) -> None:
    """Асинхронный обработчик нажатия кнопки "Рассылка 📣".\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery и FSMContext.\n
    Присылает вводное сообщение для рассылки: запрашивает сообщение
    и открывает состояние FSM "get_message".\n\n """

    await callback.message.delete()

    await callback.message.answer(
        text=f'🖊 <i><a href="tg:user?id={callback.from_user.id}">{callback.from_user.full_name}</a>,</i> '
             f'напиши сообщение для рассылки ✉️',
    )

    await state.set_state(state=States.get_message)


# Обработчик ввода сообщения администратора для рассылки его пользователям.
@router.message(States.get_message)
async def get_massage(message: Message, state: FSMContext) -> None:
    """Асинхронный обработчик ввода сообщения для дальнейшей рассылки.\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery и FSMContext.\n
    Отправляет сообщение-рассылку и очищает состояние FSM.\n\n """

    if message.text or message.caption:
        users: list[tuple[int]] = await MyRequests.get_columns('Users', *['user_id'])
        users: list[int] = [user[0] for user in users]
        text: str = message.text or message.caption

        if message.photo:
            await send_messages(ids=users, text=text, message=message, type_message='photo')

        elif message.video:
            await send_messages(ids=users, text=text, message=message, type_message='video')

        else:
            await send_messages(ids=users, text=text, message=message, type_message='text')

        await state.clear()

        await cmd_admin(message=message)

    else:
        await message.answer(
            text='❌ Неправильный формат.\n\n'
                 '🖊  Напиши обязательно еще и текст для рассылки ✉️',
        )

        await state.set_state(state=States.get_message)
