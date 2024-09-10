from logging import getLogger

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from locales import MESSAGES
from utils import get_user_language


router = Router()

logger = getLogger(__name__)

@router.callback_query(F.data.endswith("_period_of_subscription"))
async def handle_buy_subscription_cbd(
    callback_query: CallbackQuery, state: FSMContext
):
    logger.debug(
        "Selected period: %s",
        callback_query.data
        .replace("_period_of_subscription", "")
        .replace("_", " ")
    )
    await callback_query.answer()
