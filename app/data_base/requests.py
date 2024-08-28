# Импорт необходимых модулей.
from typing import Any

from sqlalchemy import select, column, insert, update, Text, Integer, delete

from .Models.users import *
from .Models.catalog import *
from app.bot_settings import session_maker


# Класс для запросов к базе данных.
class Requests:
    """Класс для запросов к базе данных.
    Для корректной работы, при создании объекта класса
    необходимо указать ВСЕ таблицы в используемой базе данных.
    Все методы преимущественно асинхронные. """

    def __init__(self, *args: tuple[str, Any]) -> None:
        self._session = session_maker()
        self.__tables = dict(args)
        self._type_map = {
            Text: str,
            Float: float,
            BigInteger: int,
            Integer: int
        }

    async def get_columns(self, table: str, columns_name: list[str]) -> list[tuple] | None:
        """Возвращает список кортежей с данных указанных столбцов из указанной таблицы, либо None.
        Метод асинхронный. """

        async with self._session:
            table = self.__tables.get(table)

            query = select([column(name) for name in columns_name]).select_from(table)
            result = await self._session.execute(query)

            result = result.fetchall()

            return result

    async def get_line(self, table: str, column_name: str, value: Any) -> Any | None:
        """Возвращает строку с данным из указанной таблицы.
        Данные возвращаются в виде класса таблицы, либо None.
        Метод асинхронный. """

        async with self._session:
            table = self.__tables.get(table)

            query = select(table).where(column(column_name) == value)
            result = await self._session.execute(query)

            result = result.fetchone()

            if result is not None:
                return result[0]
            else:
                return None

    async def add_items(self, table: str, **kwargs: dict) -> None:
        """Добавляет данные в указанную таблицу.
        Метод асинхронный. """

        async with self._session:
            default = {}
            table = self.__tables.get(table)
            table_columns = table.__table__.columns
            column_default = [
                (column_name.name, column_name.default.arg, column_name.type) for column_name in table_columns if column_name.default is not None
            ]
            specified_args = list(kwargs.keys())

            for name in column_default:
                if name[0] not in specified_args:
                    for type_class, convert_func in self._type_map.items():
                        if isinstance(name[2], type_class):
                            try:
                                default[name[0]] = convert_func(name[1])
                                print(f"Преобразование {name[1]} в {convert_func.__name__}.")
                            except ValueError:
                                print(f"Ошибка преобразования {name[1]} в {convert_func.__name__}.")

            combined_values = {**default, **kwargs}

            query = insert(table).values(**combined_values).prefix_with('OR IGNORE')
            await self._session.execute(query)

            await self._session.commit()

    async def delete_items(self, table: str, column_name: str, value: Any) -> None:
        """Удаляет строку из указанной таблицы.
        Метод асинхронный. """

        async with self._session:
            table = self.__tables.get(table)

            query = delete(table).where(column(column_name) == value)
            await self._session.execute(query)

            await self._session.commit()

    async def update_items(self, table: str, column_name: str, value: Any, **kwargs: dict) -> None:
        """Обновляет данные в указанном строке и в таблице.
        Метод асинхронный. """

        async with self._session:
            table = self.__tables.get(table)

            query = update(table).where(column(column_name) == value).values(kwargs)
            await self._session.execute(query)

            await self._session.commit()


# Создание объекта класса Requests.
MyRequests = Requests(
    *[
        ('Category', Category),
        ('Brawl Stars', BrawlStars),
        ('Users', Users),
        ('PromoCode', PromoCode),
        ('Игры в Steam', GamesSteam),
    ],
)
