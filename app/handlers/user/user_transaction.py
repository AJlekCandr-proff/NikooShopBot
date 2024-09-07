import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.utils.states_form import StatesUser
from app.bot_settings import NikooShopBot
from app.data_base.requests import MyRequests
from app.handlers.user.user_cmd_start import cmd_start
from app.handlers.user.user_profile import send_profile
from app.keyboards.inline_markup import InlineKeyBoard
from app.services.payment_lava import API_Lava


router = Router(name=__name__)


@router.callback_query(F.data == 'set_promocode')
async def get_promocode(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Асинхронный обработчик нажатия кнопки "Ввести промокод 🎁".
    Открывает состояние FSM "get_promocode" и
    отправляет ответ с запросом на введение промокода.

    :param callback: Объект класса CallbackQuery.
    :param state: Объект класса FSMContext.
    """

    await callback.message.edit_caption(
        caption=f'📌 <a href="tg: user?id={callback.from_user.id}"><i>{callback.from_user.full_name}</i></a>, '
                f'введи промокод и получи свой бонус на баланс! 🎁\n\n',
    )

    await state.set_state(state=StatesUser.get_promocode)


@router.message(StatesUser.get_promocode, F.text)
async def check_promocode(message: Message, state: FSMContext) -> None:
    """
    Асинхронный обработчик ввода промокода.
    Проверяет промокод на валидность. Если промокод существует и он верный, то бонус зачисляется на баланс.
    В противном случае высвечивается соответствующее сообщение.

    :param message: Объект класса Message.
    :param state: Объект класса FSMContext.
    """

    promo_code: str = message.text
    promo_codes = await MyRequests.get_columns(table='PromoCode', columns_name=['code', 'gift_sum', 'limit'])
    user = await MyRequests.get_line(table='Users', column_name='user_id', value=message.from_user.id)
    promo = next((promo for promo in promo_codes if promo_code == promo[0]), None)

    if promo and promo[2] > 0:
        await MyRequests.update_items(table='PromoCode', column_name='code', value=promo[0],  limit=promo[2] - 1)

        await MyRequests.update_items(
            table='Users',
            column_name='user_id',
            value=message.from_user.id,
            balance=user.balance + promo[1]
        )

        await message.answer(text=f'🎁 Вам начислено {promo[1]} ₽!\n\n')

    else:
        await message.answer(text=f'❌ Такого промокода не существует!\n\n')

    await cmd_start(message=message)

    await state.clear()


@router.callback_query(F.data == 'set_balance')
async def get_sum_balance(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Асинхронный обработчик нажатия кнопки "Пополнить баланс 💳".
    Открывает состояние FSM "get_sum" и
    отправляет ответ с запросом на введение желаемой суммы для пополнения баланса.

    :param callback: Объект класса CallbackQuery.
    :param state: Объект класса FSMContext.
    """

    await callback.message.answer(text='💳 Напиши сумму, на которую хочешь пополнить свой баланс:')

    await state.set_state(state=StatesUser.get_sum)


# Обработчик введения суммы для пополнения баланса.
@router.message(StatesUser.get_sum, F.text)
async def send_link(message: Message, state: FSMContext) -> None:
    """
    Асинхронный обработчик введения суммы для пополнения баланса.
    Удаляет 2 предыдущих сообщения и проверяет введенное сумму на корректность (Число или нет?).
    При прохождении проверки создается платежная ссылка и отправляется соответсвующее сообщение,
    открывается состояние FSM "check_pay".
    В противном случае, сумма запрашивается еще раз.

    :param message: Объект класса Message.
    :param state: Объект класса FSMContext.
    """

    payment_sum: str = message.text

    await NikooShopBot.delete_messages(chat_id=message.chat.id, message_ids=[message.message_id, message.message_id - 1])

    if re.fullmatch(r'\d+', payment_sum):
        response = await API_Lava.create_invoice(amount=payment_sum)

        payment_link = response[0]
        payment_id = response[1]

        payment_kb = InlineKeyBoard(
            *[
                ('Перейти к оплате 💳', payment_link),
                ('Проверить оплату ✅', 'check_payment'),
                ('Главное меню 🏠', 'main_menu'),
            ],
        )

        await message.answer(
            text='💳 Для пополнения баланса перейди по ссылке: 👇🏻\n\n' + payment_link,
            reply_markup=payment_kb(rows=1),
        )

        await state.update_data(id=payment_id, sum=payment_sum)
        await state.set_state(state=StatesUser.check_pay)

    else:
        await message.answer(
            text="<b>❌ Данные были введены неверно.</b>\n"
            "💰 Введите сумму для пополнения средств <b>еще раз:</b>",
        )

        await state.set_state(state=StatesUser.get_sum)


@router.callback_query(StatesUser.check_pay, F.data == 'check_payment')
async def check_pay(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Асинхронный обработчик кнопки "Проверить оплату ✅".
    Удаляет предыдущее сообщение и проверяет статус оплаты.
    При совершенно оплате, деньги зачисляются на баланс в профиле игрового магазина и очищается состояние FSM.
    Иначе, присылается предупредительное сообщение и снова открывается состояние FSM.

    :param callback: Объект класса CallbackQuery.
    :param state: Объект класса FSMContext.
    """

    data = await state.get_data()

    payment_status = await API_Lava.status_invoice(data['id'])

    if payment_status:
        await callback.message.delete()

        await callback.message.answer(
            text='✅ Отлично! Оплата прошла успешно!\n\n'
                 '💰 Деньги зачислены на баланс. \n\n'
        )

        user = await MyRequests.get_line(table='Users', column_name='user_id', value=callback.from_user.id)
        await MyRequests.update_items(
            table='Users',
            column_name='user_id',
            value=callback.from_user.id,
            balance=float(user.balance) + float(data.get('sum'))
        )

        await send_profile(callback=callback)

    else:
        await callback.message.answer(text='❌ <b>Оплата не была произведена, скорее пополни баланс!</b>')

        await state.set_state(state=StatesUser.check_pay)
