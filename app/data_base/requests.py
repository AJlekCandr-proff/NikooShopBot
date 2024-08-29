from typing import Any

from sqlalchemy import select, column, insert, update, Text, Integer, delete

from .Models.users import *
from .Models.catalog import *
from app.bot_settings import session_maker


class Requests:
    def __init__(self, tables: dict[str, Any]) -> None:
        """
        Класс для запросов к базе данных.
        Все методы преимущественно асинхронные.

        :param tables: Передаваемые словарем классы моделей таблиц и ключ для обращения к ним.
        """

        self._session = session_maker()
        self.__tables = tables
        self._type_map = {Text: str, Float: float, BigInteger: int, Integer: int}

    async def get_columns(self, table: str, columns_name: list[str]) -> list[tuple] | None:
        """
        Асинхронный метод для работы с базой данных. Извлекает данные из указанных столбцов.

        :param table: Название таблицы.
        :param columns_name: Список названий столбцов.
        :return: Список с кортежами данных из указанных столбцов.
        """

        async with self._session:
            table = self.__tables.get(table)

            query = select(*[column(name) for name in columns_name]).select_from(table)
            result = await self._session.execute(query)

            result = result.fetchall()

            return result

    async def get_line(self, table: str, column_name: str, value: any) -> Any | None:
        """
        Асинхронный метод для работы с базой данных.
        Извлекает данные из строки по значению в указанном столбце.

        :param table: Название таблицы.
        :param column_name: Название столбца.
        :param value: Значение в указанном столбце.
        :return: Объект класса таблицы.
        """

        async with self._session:
            table = self.__tables.get(table)

            query = select(table).where(column(column_name) == value)
            result = await self._session.execute(query)

            result = result.fetchone()

            return result[0] if result is not None else None

    async def add_items(self, table: str, **data: dict[str, any]) -> None:
        """
        Асинхронный метод для работы с базой данных.
        Добавляет данные в указанную таблицу и подставляет значения по умолчанию.

        :param table: Название таблицы.
        :param data: Словарь с данными для ставки.
        """

        async with self._session:
            default = {}
            table = self.__tables.get(table)
            table_columns = table.__table__.columns
            column_default = [
                (column_name.name, column_name.default.arg, column_name.type) for column_name in table_columns if column_name.default is not None
            ]
            specified_args = list(data.keys())

            for name in column_default:
                if name[0] not in specified_args:
                    for type_class, convert_func in self._type_map.items():
                        if isinstance(name[2], type_class):
                            default[name[0]] = convert_func(name[1])
            combined_values = {**default, **data}

            query = insert(table).values(**combined_values).prefix_with('OR IGNORE')
            await self._session.execute(query)

            await self._session.commit()

    async def delete_items(self, table: str, column_name: str, value: any) -> None:
        """
        Асинхронный метод для работы с базой данных.
        Удаляет строку из указанной таблицы.

        :param table: Название таблицы.
        :param column_name: Название столбца.
        :param value: Значение в указанном столбце.
        """

        async with self._session:
            table = self.__tables.get(table)

            query = delete(table).where(column(column_name) == value)
            await self._session.execute(query)

            await self._session.commit()

    async def update_items(self, table: str, column_name: str, value: any, **data: dict[str, any]) -> None:
        """
        Асинхронный метод для работы с базой данных.
        Обновляет данные в таблице в указанной строке.

        :param table: Название таблицы.
        :param column_name: Название столбца.
        :param value: Значение в указанном столбце.
        :param data: Словарь с обновленными данными для вставки.
        """

        async with self._session:
            table = self.__tables.get(table)

            query = update(table).where(column(column_name) == value).values(data)
            await self._session.execute(query)

            await self._session.commit()


MyRequests = Requests(
    {
        'Category': Category,
        'Brawl Stars': BrawlStars,
        'Users': Users,
        'PromoCode': PromoCode,
        'Игры в Steam': GamesSteam,
    },
)
