from sqlalchemy import String, Float, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.data_base.Models.base import Base


class ProductItems(Base):
    """Абстрактный класс для классов моделей таблиц каталога.
    Хранит в себе общие (базовые) признаки товара. """

    __abstract__ = True

    Product: Mapped[str] = mapped_column(String(25), nullable=False)
    Price: Mapped[float] = mapped_column(Float, nullable=False)
    Category_id: Mapped[int] = mapped_column(ForeignKey('Category.id'))
    Count: Mapped[int] = mapped_column(BigInteger, nullable=False)


class Category(Base):
    """Класс модели таблицы каталога товаров.
    Категории: Игры, приложения и сервисы. """

    __tablename__ = 'Category'

    title_game: Mapped[int] = mapped_column(String(25), nullable=False, unique=True)

    relationship(argument='BrawlStars', back_populates='Category')
    relationship(argument='GamesSteam', back_populates='Category')


class BrawlStars(ProductItems):
    """Класс модели таблицы каталога товаров.
    Товары для игры Brawl Stars. """

    __tablename__ = 'Brawl Stars'

    Category: Mapped["Category"] = relationship(argument="Category", back_populates='Brawl Stars')


class GamesSteam(ProductItems):
    """Класс модели таблицы каталога. Игры в магазине приложений Steam.
    Игры/приложения для покупки в Steam. """

    __tablename__ = 'Игры в Steam'

    Category: Mapped["Category"] = relationship(argument="Category", back_populates='Игры в Steam')


class PromoCode(Base):
    """Класс модели таблицы для хранения промо-кодов. """

    __tablename__ = 'PromoCode'

    code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    gift_sum: Mapped[float] = mapped_column(Float, nullable=False)
    limit: Mapped[int] = mapped_column(BigInteger, nullable=False)
