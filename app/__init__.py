from aiogram import Router

from .handlers import router as main_handlers_router


router = Router(name=__name__)


router.include_router(main_handlers_router)
