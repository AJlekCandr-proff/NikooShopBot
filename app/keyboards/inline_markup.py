import re

from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardBuilder, InlineKeyboardMarkup


# Создание класса-конструктора inline-клавиатуры.
class InlineKeyBoard:
    """Класс для создания inline-клавиатур.
    Кнопки и с url, и с callback_data. """

    Inline_markup = InlineKeyboardBuilder()

    __pattern = re.compile(
        r'^(?:http|ftp)s?://',
    )

    def __init__(self, *args: tuple[str, str]) -> None:
        self.buttons = args

    def __call__(self, rows: int) -> InlineKeyboardMarkup:
        """
        Dunder-метод вызова класса как асинхронную функцию для создания inline-клавиатуры.

        :param rows: Кол-во столбцов в inline-клавиатуре.
        :return: Объект класса InlineKeyboardMarkup.
        """

        self.Inline_markup = InlineKeyboardBuilder()

        for button in self.buttons:
            if self.check_url(button[1]):
                self.Inline_markup.add(
                    InlineKeyboardButton(
                        text=button[0], url=button[1],
                    ),
                )
            else:
                self.Inline_markup.add(
                    InlineKeyboardButton(
                        text=button[0], callback_data=button[1],
                    ),
                )
        return self.Inline_markup.adjust(rows).as_markup()

    @classmethod
    def check_url(cls, string: str) -> bool:
        """
        Проверяет строку на url.

        :param string: Проверяемая строка.
        :return: Константа True/False.
        """

        return bool(cls.__pattern.match(string))


# Создание объекта класса InlineKeyBoard для главного меню.
MainMenu = InlineKeyBoard(
    *[
        ('Каталог 🛍️', 'My_shop'),
        ('Профиль 👤', 'Profile'),
        ('Отзывы ⭐️ ', 'https://t.me/NikoooShopBot_otzivi'),
        ('Поддержка ⚙️', 'https://t.me/NikoooShopSupport'),
        ('Пригласить друга 🔗', 'Invite'),
    ],
)


# Создание объекта класса InlineKeyBoard для дополнительного меню.
MenuKb = InlineKeyBoard(
    *[
        ('Купить 💳', 'Buy'),
        ('Назад 🏠', 'back'),
        ('Главное меню 🏠', 'main_menu'),
    ],
)


# Создание объекта класса InlineKeyBoard для профиля.
MenuProfileKb = InlineKeyBoard(
    *[
        ('Пополнить баланс 💳', 'set_balance'),
        ('Ввести промокод 🎁', 'set_promocode'),
        ('Главное меню 🏠', 'main_menu'),
    ],
)

# Создание объекта класса InlineKeyBoard для панели администратора.
AdminKb = InlineKeyBoard(
    *[
        ('Управление каталогом 🛍️', 'edit_catalog'),
        ('Промокоды 🎁', 'get_promo_codes'),
        ('Рассылка 📣', 'send_letters'),
        ('Статистика 📊', 'statistic'),
        ('Отзывы ⭐️ ', 'https://t.me/NikoooShopBot_otzivi'),
        ('Главное меню 🏠', 'main_menu'),
    ],
)


# Создание объекта класса InlineKeyBoard для редактирования промокодов.
EditPromoKb = InlineKeyBoard(
    *[
        ('Добавить промокод 🎁', 'add_promo'),
        ('Удалить промокод 🗑️', 'delete_promo'),
        ('В панель 🏠', 'panel'),
    ],
)


# Создание объекта класса InlineKeyBoard для перехода в главное меню.
StatisticKb = InlineKeyBoard(
    *[
        ('В панель 🏠', 'panel'),
    ],
)
