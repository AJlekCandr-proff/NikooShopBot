from aiogram import Router

from .admin_panel import router as router_cmd_admin
from .admin_letters import router as router_handler_letters
from .admin_statistic import router as router_handler_statistic
from .admin_edit_catalog import router as router_handler_edit_catalog
from .admin_promo import router as router_handler_promo


router = Router(name=__name__)


router.include_routers(
    router_handler_letters,
    router_handler_statistic,
    router_cmd_admin,
    router_handler_edit_catalog,
    router_handler_promo
)
