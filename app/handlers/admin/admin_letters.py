from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from .admin_panel import cmd_admin
from app.utils.states_form import StatesAdmin
from app.utils.send_messages import send_messages
from app.data_base.requests import MyRequests


router = Router(name=__name__)


@router.callback_query(F.data == 'send_letters')
async def send_massage(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Асинхронный обработчик нажатия кнопки "Рассылка 📣".
    Присылает вводное сообщение для рассылки: запрашивает сообщение
    и открывает состояние FSM "get_message".

    :param callback: Объект класса CallbackQuery.
    :param state: Объект класса FSMContext.
    """

    await callback.message.delete()

    await callback.message.answer(
        text=f'🖊 <i><a href="tg:user?id={callback.from_user.id}">{callback.from_user.full_name}</a>,</i> '
             f'напиши сообщение для рассылки ✉️',
    )

    await state.set_state(state=StatesAdmin.get_message)


@router.message(StatesAdmin.get_message)
async def get_massage(message: Message, state: FSMContext) -> None:
    """
    Асинхронный обработчик ввода сообщения для дальнейшей рассылки.
    Отправляет сообщение-рассылку и очищает состояние FSM.

    :param message: Объект класса Message.
    :param state: Объект класса FSMContext.
    """

    if message.text or message.caption:
        users: list[tuple[int]] = await MyRequests.get_columns(table='Users', columns_name=['user_id'])
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

        await state.set_state(state=StatesAdmin.get_message)
