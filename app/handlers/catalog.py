from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile, Message
from aiogram.fsm.context import FSMContext

from app.utils.states_form import StatesUser
from .user.user_cmd_start import cmd_start
from ..bot_settings import NikooShopBot, settings
from ..data_base.requests import MyRequests
from ..keyboards.inline_markup import InlineKeyBoard, MenuKb, MenuProfileKb


router = Router(name=__name__)


@router.callback_query(F.data == 'My_shop')
async def category(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Асинхронный обработчик нажатия кнопки "Каталог 🛍️".
    Присылает каталог игр и открывает состояние FSM 'choice_product' для выбора товара.

    :param callback: Объект класса CallbackQuery.
    :param state: Объект класса FSMContext.
    """

    await callback.message.delete()

    categories = await MyRequests.get_columns(table='Category', columns_name=['id', 'title_game'])

    category_kb = InlineKeyBoard(
        *[
            (game[1], f'game_{game[0]}') for game in categories

        ] + [
            ('Главное меню 🏠', 'main_menu'),
        ],
    )

    await callback.message.answer_photo(
        photo=BufferedInputFile(
            file=open('app/media/Base/catalog.png', 'rb').read(),
            filename='catalog.png',
        ),
        caption='🎮 Выберите категорию 👇🏻',
        reply_markup=category_kb(rows=1),
    )

    await state.set_state(state=StatesUser.choice_game)


@router.callback_query(F.data.startswith('game_'), StatesUser.choice_game)
async def send_catalog_game(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Асинхронный обработчик нажатия кнопки "Профиль 👤".
    Отправляет каталог выбранной игры и открывает состояние FSM 'choice_product' для выбора товара.

    :param callback: Объект класса CallbackQuery.
    :param state: Объект класса FSMContext.
    """

    await callback.message.delete()

    game = await MyRequests.get_line(table='Category', column_name='id', value=callback.data.split('_')[1])

    products = await MyRequests.get_columns(table=f'{game.title_game}', columns_name=['id', 'Count', 'Product', 'Price'])

    product_kb = InlineKeyBoard(
        *[
            (
                f'{product[1] if int(product[1]) > 1 else " "} {product[2].replace("Гемы", "Гемов") if "Гемы" in product[2] else product[2]} | {product[3]} ₽',
                f'product_{product[0]}'
            )
            for product in products
        ] +
        [
            ('Главное меню 🏠', 'main_menu'),
        ]
    )

    await callback.message.answer_photo(
        photo=BufferedInputFile(
            file=open('app/media/Base/catalog.png', 'rb').read(),
            filename='catalog.png',
        ),
        reply_markup=product_kb(rows=1),
    )
    await state.update_data(game=game.title_game)

    await state.set_state(state=StatesUser.choice_product)


@router.callback_query(F.data.startswith('product_'), StatesUser.choice_product)
async def send_product(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Асинхронный обработчик выбора товара в выбранной игре.
    Присылает информацию о выбранном товаре и присылает меню для выбора действия с товаром,
    открывает состояние FSM "buy_product".

    :param callback: Объект класса CallbackQuery.
    :param state: Объект класса FSMContext.
    """

    data = await state.get_data()
    game = data['game']
    product_id = int(callback.data.split('_')[1])

    await callback.message.delete()

    product = await MyRequests.get_line(table=game, column_name='id', value=product_id)

    await callback.message.answer_photo(
        photo=BufferedInputFile(
            file=open(f'app/media/{game}/Product_{product_id}.png', 'rb').read(),
            filename='product.png',
            ),
        caption=f'✅ Покупка для вашего аккаунта в {game} 🎮\n\n'
                f'📦 Товар: {product.Product}\n'
                f'💰 Цена: {product.Price} ₽\n\n',
        reply_markup=MenuKb(rows=1),
    )

    await state.update_data(price=product.Price, product=product.Product, count=product.Count)
    await state.set_state(state=StatesUser.buy_product)


@router.callback_query(F.data == 'Buy', StatesUser.buy_product)
async def buy_product_game(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Асинхронный обработчик нажатия кнопки "Купить 💳".
    Списывает деньги с баланса и запрашивает адрес электронной почты.
    В противном случае, при недостаточном балансе,
    выводит сообщение об ошибке и предложение пополнить баланс.

    :param callback: Объект класса CallbackQuery.
    :param state: Объект класса FSMContext.
    """

    await callback.message.delete()

    data = await state.get_data()
    game = data['game']
    price = data['price']
    user = await MyRequests.get_line(table='Users', column_name='user_id', value=callback.from_user.id)

    if user.balance >= price:
        await MyRequests.update_items(
            table='Users',
            column_name='user_id',
            value=callback.from_user.id,
            balance=user.balance - price)

        await callback.message.answer(
            text='Спасибо за покупку!)\n\n' 
                 f'Ниже обязательно укажите адрес Е-mail ✉️ от вашего аккаунта(учетной записи) в {game} 👇🏻',
        )

        await state.set_state(state=StatesUser.get_email)

    else:
        await callback.message.answer_photo(
            photo=BufferedInputFile(
                file=open('app/media/Base/balance.png', 'rb').read(),
                filename='balance.png',
            ),
            caption=f'❌ Недостаточно средств на балансе!\n\n'
                    f'💰 Баланс: {user.balance} ₽\n\n',

            reply_markup=MenuProfileKb(rows=1),
        )


@router.message(StatesUser.get_email, F.text)
async def send_purchase(message: Message, state: FSMContext) -> None:
    """
    Асинхронный обработчик ввода электронной почты.
    Отправляет благодарное сообщение пользователю и переносит его в главное меню.
    Отправляет сообщение об успешной покупке товара администратору бота.
    Очищается состояние FSM.

    :param message: Объект класса Message.
    :param state: Объект класса FSMContext.
    """

    data: dict = await state.get_data()

    game = data['game']
    price = data['price']
    count = data['count']
    product = data['product']
    email = message.text
    user_id = message.from_user.id

    await message.answer(
        text='ОК. Еще раз спасибо за покупку ❤️\n'
             f'📦 Ресурсы обрабатываются и в течение суток будут отправлены вам на аккаунт в {game}... 🕓\n\n'
             f'В случае ошибки/проблем и прочих вопросов обращаться в поддержку - 👉🏻 @NikoooShopSupport 👈🏻\n\n'
             f'C уважением, администрация проекта @NikoooShop 🤝🏻\n\n',
    )

    await NikooShopBot.send_message(
        chat_id=settings.ADMIN_ID,
        text=f'🔔 <i>Новая покупка 🛍</i>\n\n'
             f'<b>👤 Пользователь:</b> <a href="tg:user?id={user_id}">{message.from_user.full_name}</a>\n'
             f'<b>🆔 Telegram:</b> <ins>{user_id}</ins>\n\n'
             f'<b>🎮 Игра:</b> {game}\n'
             f'<b>✉️ E-mail адрес:</b> <code>{email}</code>\n\n'
             f'<b>📦 Товар:</b> {product}\n'
             f'<b>📌 Кол-во:</b> {count}\n'
             f'<b>💰 Сумма:</b> {price} ₽\n\n'
             f'@NikoooShopBot\n\n',
    )

    await cmd_start(message=message)

    await state.clear()


@router.callback_query(F.data == 'Back', StatesUser.buy_product)
async def back_to_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Асинхронный обработчик нажатия кнопки "Назад 🏠".
    Возвращает в меню с товарами выбранной игры.

    :param callback: Объект класса CallbackQuery.
    :param state: Объект класса FSMContext.
    """

    await send_catalog_game(callback=callback, state=state)
