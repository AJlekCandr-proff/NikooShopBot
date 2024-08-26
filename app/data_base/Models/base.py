# Импорт необходимых модулей.
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# Класс базы данных.
class Base(DeclarativeBase):
    """Класс базы данных."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
