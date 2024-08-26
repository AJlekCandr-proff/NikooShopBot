import re

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.views import msg_format_promo, msg_error_format_promo
from app.data_base.requests import MyRequests
from app.handlers.admin.admin_panel import cmd_admin
from app.keyboards.inline_markup import EditPromoKb, InlineKeyBoard


# Инициализация роутера.
router = Router(name=__name__)


# Состояния FSM.
class States(StatesGroup):
    get_promo = State()
    choice_promo = State()


# Обработчик нажатия кнопки "Промокоды 🎁".
@router.callback_query(F.data == 'get_promo_codes')
async def send_promo_codes(callback: CallbackQuery) -> None:
    """Асинхронный обработчик нажатия кнопки "Промокоды 🎁".\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery.\n
    Отправляет список промо-кодов и действий с ним.\n\n """

    await callback.message.delete()

    promo_codes = await MyRequests.get_columns(table='PromoCode', *['code', 'gift_sum', 'limit'])
    text = '\n'.join([f' 🎁 <code>{promo_codes[0]}</code> - <b>{promo_codes[1]} ₽</b> | Осталось штук: <b>{promo_codes[2]}</b> 🔑' for promo_codes in promo_codes])

    await callback.message.answer(
        text='🔑 Все действующие промо-коды 🎁 \n\n'
             f'{text}',
        reply_markup=EditPromoKb(rows=1),
    )


# Обработчик кнопки "Добавить промокод 🎁".
@router.callback_query(F.data == 'add_promo')
async def add_promo_code(callback: CallbackQuery, state: FSMContext) -> None:
    """Асинхронный обработчик нажатия кнопки "Добавить промокод 🎁".\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery и FSMContext.\n
    Запрашивает новый промокод в определенном формате.\n\n """

    await callback.message.delete()

    await callback.message.answer(text=msg_format_promo())

    await state.set_state(state=States.get_promo)


# Обработчик ввода нового промо-кода.
@router.message(States.get_promo, F.text)
async def add_promo_code_into_db(message: Message, state: FSMContext) -> None:
    """Асинхронный обработчик ввода нового промо-кода.\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery и FSMContext.\n
    Проверяет формат введенного промокода и при корректности его - добавляет в базу данных и
    переносит в панель администратора, иначе
    при неверном формате - запрашивает снова.\n\n """

    if re.fullmatch(r'^[\w+]+\s-+\s+\d+\s-+\s+\d+$', message.text):
        code = message.text.split()[0]
        gift_sum = float(message.text.split()[2])
        limit = int(message.text.split()[4])

        await MyRequests.add_items(table='PromoCode', code=code, gift_sum=gift_sum, limit=limit)

        await message.answer(text='✅ Промо-код успешно добавлен 🎁')

        await cmd_admin(message=message)

        await state.clear()

    else:
        await message.answer(text=msg_error_format_promo())

        await state.set_state(state=States.get_promo)


# Обработчик кнопки "Удалить промокод 🗑️".
@router.callback_query(F.data == 'delete_promo')
async def delete_promo_code(callback: CallbackQuery, state: FSMContext) -> None:
    """Асинхронный обработчик нажатия кнопки "Удалить промокод 🗑️".\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery и FSMContext.\n
    Присылает список всех промокодов и отрывает состояние FSM для выбора промокода "choice_promo".\n\n """

    promo_codes = await MyRequests.get_columns(table='PromoCode', *['code', 'id'])

    promo_code_kb = InlineKeyBoard(
        *[
            (f'{promo_code[0]}', f'promo_{promo_code[1]}') for promo_code in promo_codes
        ],
    )

    await callback.message.edit_text(
        text='🔑 Выбери промокод, который Ты хочешь удалить 👇🏻',
        reply_markup=promo_code_kb(rows=1),
    )

    await state.set_state(state=States.choice_promo)


# Обработчик выбора промокода для удаления.
@router.callback_query(F.data.startswith('promo_'), States.choice_promo)
async def delete_promo_code(callback: CallbackQuery, state: FSMContext) -> None:
    """Асинхронный обработчик выбора промокода для удаления.\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery и FSMContext.\n
    Удаляет промокод из базы данных и переносит в панель администратора.\n\n """

    await MyRequests.delete_items(table='PromoCode', column_name='id', value=callback.data.split('_')[1])

    await callback.message.answer(text='✅ Промо-код успешно удален 🎁')

    await state.clear()

    await cmd_admin(message=callback.message, user_id=callback.from_user.id)
