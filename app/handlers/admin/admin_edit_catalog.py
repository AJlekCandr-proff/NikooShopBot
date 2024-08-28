# Импорт необходимых модулей.
import re

from aiogram import F, Router
from aiogram.types import CallbackQuery, BufferedInputFile, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.views import msg_choice_game, msg_format_product, msg_error_format_product, msg_error_format_text_product
from app.bot_settings import bot
from app.data_base.requests import MyRequests
from .admin_panel import cmd_admin
from app.keyboards.inline_markup import InlineKeyBoard


# Инициализация роутера.
router = Router(name=__name__)


# Состояния FSM.
class StatesAdmin(StatesGroup):
    """Хранит в себе состояния FSM для панели управления. """

    choice_game = State()
    choice_action = State()
    select_item = State()
    get_item = State()


# Обработчик нажатия кнопки "Управление каталогом 🛍️".
@router.callback_query(F.data == 'edit_catalog')
async def edit_catalog(callback: CallbackQuery, state: FSMContext) -> None:
    """Асинхронный обработчик нажатия кнопки "Управление каталогом 🛍️".\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery и FSMContext.\n
    Отправляет меню для выбора игры и дальнейшего редактирования ее каталога.\n\n """

    await callback.message.delete()

    categories = await MyRequests.get_columns(table='Category', columns_name=['id', 'title_game'])

    category_kb = InlineKeyBoard(
        *[
             (game[1], f'edit_{game[0]}') for game in categories

         ] + [
             ('В панель 🏠', 'panel'),
         ],
    )
    await callback.message.answer_photo(
        photo=BufferedInputFile(
            file=open('app/media/Base/catalog.png', 'rb').read(),
            filename='Admin.jpg',
        ),
        caption=msg_choice_game(),
        reply_markup=category_kb(rows=1),
    )

    await state.set_state(state=StatesAdmin.choice_game)


# Обработчик выбора игры.
@router.callback_query(StatesAdmin.choice_game)
async def send_catalog_game(callback: CallbackQuery, state: FSMContext) -> None:
    """Асинхронный обработчик выбора игры для редактирования ее каталога.\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery и FSMContext.\n
    Присылает каталог товаров и действий с ним выбранной игры администратором,
    открывает состояние FSM 'choice_action' для выбора действия.\n\n """

    await callback.message.delete()

    game_id = callback.data.split('_')[1]
    game = await MyRequests.get_line(table='Category', column_name='id', value=game_id)
    products = await MyRequests.get_columns(table=game.title_game, columns_name=['id', 'Count', 'Product', 'Price'])

    await state.update_data(game=game.title_game, id=game_id)

    products_kb = InlineKeyBoard(
        *[
             (
                 f'{product[1]} {product[2].replace("Гемы", "Гемов") if "Гемы" in product[2] else product[2]} | {product[3]} ₽',
                 f'{product[0]}'
             )
             for product in products
        ] + [
            ('➕ Добавить элемент', 'add_item'),
            ('🗑 Удалить элемент', 'delete_item'),
            ('В панель 🏠', 'panel'),
        ],
    )

    await callback.message.answer_photo(
        photo=BufferedInputFile(
            file=open('app/media/Base/catalog.png', 'rb').read(),
            filename='Admin.jpg',
        ),
        caption=f'🎮 Вот каталог игры {game.title_game} 👇🏻',
        reply_markup=products_kb(rows=1),
    )

    await state.set_state(state=StatesAdmin.choice_action)


# Обработчик нажатия кнопки "🗑 Удалить элемент".
@router.callback_query(StatesAdmin.choice_action, F.data == 'delete_item')
async def selected_item(callback: CallbackQuery, state: FSMContext) -> None:
    """Асинхронный обработчик нажатия кнопки "🗑 Удалить элемент".\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery и FSMContext.\n
    Присылает каталог товаров для выбора товара для удаления.\n\n """

    data = await state.get_data()
    game = data.get(__key='game')
    products = await MyRequests.get_columns(table=game, *['id', 'Count', 'Product', 'Price'])

    products_kb = InlineKeyBoard(
        *[
            (
                f'{product[1]} {product[2].replace("Гемы", "Гемов") if "Гемы" in product[2] else product[2]} | {product[3]} ₽',
                f'{product[0]}'
            )
            for product in products
        ]
    )

    await callback.message.edit_caption(
        caption=f'🗑 Выбери элемент для удаления 👇🏻',
        reply_markup=products_kb(rows=1),
    )

    await state.set_state(state=StatesAdmin.select_item)


# Обработчик выбора элемента для удаления из каталога выбранной игры.
@router.callback_query(StatesAdmin.select_item)
async def delete_item(callback: CallbackQuery, state: FSMContext) -> None:
    """Асинхронный обработчик выбора элемента для удаления.\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery и FSMContext.\n
    Удаляет выбранный администратором элемент каталога и переносит на выбор игры. """

    data = await state.get_data()
    game = data.get(__key='game')
    product_id = int(callback.data)

    await MyRequests.delete_items(table=game, column_name='id', value=product_id)

    await callback.message.answer(text='✅ Элемент успешно удален 🗑')

    await send_catalog_game(callback=callback, state=state)


# Обработчик нажатия кнопки "➕ Добавить элемент".
@router.callback_query(F.data == 'add_item', StatesAdmin.choice_action)
async def get_info_item(callback: CallbackQuery, state: FSMContext) -> None:
    """Асинхронный обработчик нажатия кнопки "➕ Добавить элемент".\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery и FSMContext.\n
    Открывает состояние FSM "get_item" и запрашивает информацию о новом товаре в нужном формате.\n\n """

    await callback.message.delete()

    await callback.message.answer(text=msg_format_product())

    await state.set_state(state=StatesAdmin.get_item)


# Обработчик ввода информации о товаре.
@router.message(StatesAdmin.get_item, F.photo)
async def add_item_into_db(message: Message, state: FSMContext) -> None:
    """Асинхронный обработчик ввода информации о новом товаре.\n
    Принимает в себя в качестве аргументов объект класса CallbackQuery и FSMContext.\n
    Проверяет введенную информацию на валидность формата,
    при прохождении проверки добавляет элемент в каталог и переносит в панель администратора, очищает состояние FSM.
    В противном случае, при неверном формате, запрашивает снова информацию о товаре снова.\n\n """

    if message.caption:
        data = await state.get_data()
        text = message.caption

        if re.fullmatch(r'^[\w\s]+\s\d+\s\d+$', text):
            parts: list[str] = text.rsplit(' ', 2)
            title: str = parts[0]
            count = int(parts[1])
            price = float(parts[2])
            game = data['game']

            await MyRequests.add_items(
                table=game,
                Product=title,
                Count=count,
                Category=data.get('id'),
                Price=price
            )

            product = await MyRequests.get_line(table=game, column_name='Product', value=title)

            await bot.download(message.photo[-1].file_id, f'app/media/{data.get("game")}/Product_{product.id}.png')

            await message.answer(text='✅ Элемент успешно добавлен 📝')

            await cmd_admin(message=message)

            await state.clear()

        else:
            await message.answer(text=msg_error_format_text_product())

    else:
        await message.answer(text=msg_error_format_product())

        await state.set_state(state=StatesAdmin.get_item)
