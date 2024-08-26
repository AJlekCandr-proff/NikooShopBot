# Импорт необходимых модулей.
from aiogram import Router

from .user import router as main_router_users
from .admin import router as main_router_admins
from .catalog import router as router_catalog
from .main_menu import router as router_main_menu


# Инициализация роутера.
router = Router(name=__name__)


# Подключение к главному роутеру других роутеров.
router.include_routers(
    router_catalog,
    main_router_admins,
    main_router_users,
    router_main_menu,
)
