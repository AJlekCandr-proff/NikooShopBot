# Импорт необходимых модулей.
from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from .user.user_cmd_start import cmd_start
from ..bot_settings import bot, settings
from ..data_base.requests import MyRequests
from ..keyboards.inline_markup import InlineKeyBoard, MenuKb, MenuProfileKb


# Инициализация роутера.
router = Router(name=__name__)


# Состояния FSM.
class StatesCatalog(StatesGroup):
    """Хранит в себе состояния FSM. """

    choice_game = State()
    choice_product = State()
    buy_product = State()
    get_email = State()


# Обработчик нажатия кнопки "Каталог 🛍️".
@router.callback_query(F.data == 'My_shop')
async def category(callback: CallbackQuery, state: FSMContext) -> None:
    """Асинхронный обработчик нажатия кнопки "Каталог 🛍️".\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery и FSMContext.\n
    Присылает каталог игр и открывает состояние FSM 'choice_product' для выбора товара.\n\n """

    await callback.message.delete()

    categories = await MyRequests.get_columns(table='Category', *['id', 'title_game'])

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

    await state.set_state(state=StatesCatalog.choice_game)


# Обработчик выбора игры.
@router.callback_query(F.data.startswith('game_'), StatesCatalog.choice_game)
async def send_catalog_game(callback: CallbackQuery, state: FSMContext) -> None:
    """Асинхронный обработчик нажатия кнопки "Профиль 👤".\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery и FSMContext.\n
    Отправляет каталог выбранной игры и открывает состояние FSM 'choice_product' для выбора товара.\n\n """

    await callback.message.delete()

    game = await MyRequests.get_line(table='Category', column_name='id', value=callback.data.split('_')[1])

    products: list[tuple] = await MyRequests.get_columns(table=f'{game.title_game}', *['id', 'Count', 'Product', 'Price'])

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

    await state.set_state(state=StatesCatalog.choice_product)


# Обработчик выбора товара.
@router.callback_query(F.data.startswith('product_'), StatesCatalog.choice_product)
async def send_product(callback: CallbackQuery, state: FSMContext) -> None:
    """Асинхронный обработчик выбора товара в выбранной игре.\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery и FSMContext.\n
    Присылает информацию о выбранном товаре и присылает меню для выбора действия с товаром,
    открывает состояние FSM "buy_product".\n\n """

    data = await state.get_data()
    game = data.get(__key='game')
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
    await state.set_state(state=StatesCatalog.buy_product)


# Обработчик нажатия кнопки "Купить 💳".
@router.callback_query(F.data == 'Buy', StatesCatalog.buy_product)
async def buy_product_game(callback: CallbackQuery, state: FSMContext) -> None:
    """Асинхронный обработчик нажатия кнопки "Купить 💳".\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery и FSMContext.\n
    Списывает деньги с баланса и запрашивает адрес электронной почты.
    В противном случае, при недостаточном балансе,
    выводит сообщение об ошибке и предложение пополнить баланс.\n\n """

    await callback.message.delete()

    data = await state.get_data()
    game = data.get('game')
    price = data.get('price')

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

        await state.set_state(state=StatesCatalog.get_email)

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


# Обработчик ввода e-mail пользователя.
@router.message(StatesCatalog.get_email, F.text)
async def send_purchase(message: Message, state: FSMContext) -> None:
    """Асинхронный обработчик ввода электронной почты.\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery и FSMContext.\n
    Отправляет благодарное сообщение пользователю и переносит его в главное меню.
    Отправляет сообщение об успешной покупке товара администратору бота.
    Очищается состояние FSM.\n\n """

    data: dict = await state.get_data()

    game = data.get(__key='game')
    price = data.get(__key='price')
    count = data.get(__key='count')
    product = data.get(__key='product')
    email = message.text
    user_id = message.from_user.id

    await message.answer(
        text='ОК. Еще раз спасибо за покупку ❤️\n'
             f'📦 Ресурсы обрабатываются и в течение суток будут отправлены вам на аккаунт в {game}... 🕓\n\n'
             f'В случае ошибки/проблем и прочих вопросов обращаться в поддержку - 👉🏻 @NikoooShopSupport 👈🏻\n\n'
             f'C уважением, администрация проекта @NikoooShop 🤝🏻\n\n',
    )

    await bot.send_message(
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


# Обработчик нажатия кнопки "Назад 🏠".
@router.callback_query(F.data == 'Back', StatesCatalog.buy_product)
async def back_to_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """Асинхронный обработчик нажатия кнопки "Назад 🏠".\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery и FSMContext.\n
    Возвращает в меню с товарами выбранной игры.\n\n """

    await send_catalog_game(callback=callback, state=state)
