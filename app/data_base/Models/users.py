from sqlalchemy import BigInteger, String, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.data_base.Models.base import Base


class Users(Base):
    """Класс модели таблицы с данными профилей пользователей. """

    __tablename__ = 'Users'

    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(25), nullable=True, unique=True)
    balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
