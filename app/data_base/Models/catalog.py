# Импорт необходимых модулей.
from sqlalchemy import String, Float, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.data_base.Models.base import Base


# Класс признаков товара.
class ProductItems(Base):
    """Класс для каталога.
    Хранит в себе общие (базовые) признаки товара. """

    __abstract__ = True

    Product: Mapped[str] = mapped_column(String(25), nullable=False)
    Price: Mapped[float] = mapped_column(Float, nullable=False)
    Category: Mapped[int] = mapped_column(ForeignKey('Category.id'))
    Count: Mapped[int] = mapped_column(BigInteger, nullable=False)


# Класс таблицы категорий.
class Category(Base):
    """Таблица каталога товаров.
    Категории: Игры, приложения и сервисы. """

    __tablename__ = 'Category'

    title_game: Mapped[int] = mapped_column(String(25), nullable=False, unique=True)


# Класс таблицы в Brawl Stars.
class BrawlStars(ProductItems):
    """Таблица каталога товаров.
    Товары для игры Brawl Stars. """

    __tablename__ = 'Brawl Stars'


# Класс таблицы игр в Steam.
class GamesSteam(ProductItems):
    """Таблица каталога. Игры в магазине приложений Steam.
    Игры/приложения для покупки в Steam. """

    __tablename__ = 'Игры в Steam'


# Класс таблицы промокодов.
class PromoCode(Base):
    """Таблица для хранения промо-кодов. """

    __tablename__ = 'PromoCode'

    code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    gift_sum: Mapped[float] = mapped_column(Float, nullable=False)
    limit: Mapped[int] = mapped_column(BigInteger, nullable=False)
