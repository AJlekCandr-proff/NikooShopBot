# Импорт необходимых модулей.
from aiogram import Router

from .handlers import router as main_handlers_router


# Инициализация роутера.
router = Router(name=__name__)


# Подключение к главному роутеру других роутеров.
router.include_router(main_handlers_router)
