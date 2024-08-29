from aiogram import Router

from .user_cmd_start import router as router_cmd_start
from .user_profile import router as router_handler_profile
from .user_transaction import router as router_handler_transactions


router = Router(name=__name__)


router.include_routers(
    router_handler_profile,
    router_cmd_start,
    router_handler_transactions,
)
