from aiogram import Router

from .callback_queries import router as callback_queries_router
from .messages import router as messages_router


router = Router()

router.include_routers(callback_queries_router, messages_router)
