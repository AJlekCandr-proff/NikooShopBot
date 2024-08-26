# Необходимых модулей.
from loguru import logger

from pydantic import SecretStr

from pydantic_settings import BaseSettings, SettingsConfigDict

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


# Класс настроек бота.
class Settings(BaseSettings):
    """Хранит в себе переменные окружения проекта."""

    TOKEN: SecretStr
    TOKEN_LAVA: SecretStr
    SHOP_ID: SecretStr
    ADMIN_ID: SecretStr
    SQLALCHEMY_URL: SecretStr

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")


# Создание объекта класса Settings.
settings = Settings()


# Инициализация бота.
bot = Bot(token=settings.TOKEN.get_secret_value(), default=DefaultBotProperties(parse_mode='HTML'))


# Создание объекта регистратора сообщений.
logger = logger


# Создание подключения к базе данных.
engine = create_async_engine(url=settings.SQLALCHEMY_URL.get_secret_value())


# Создание сессии работы с базой данных.
session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, autocommit=False)
