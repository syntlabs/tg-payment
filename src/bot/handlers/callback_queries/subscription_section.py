from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from api_client_session import MySession
from config import API_ENDPOINT
from sections import show_subscription_section, show_period_section


router = Router()

@router.callback_query(
    F.data.in_(("buy_subscription_cbd", "renew_subscription_cbd"))
)
async def handle_buy_subscription_cbd(
    callback_query: CallbackQuery, state: FSMContext
):
    await show_period_section(callback_query, state)


@router.callback_query(
    F.data.in_(("disable_notifications_cbd", "enable_notifications_cbd"))
)
async def handle_switcher_of_notifications_cbd(
    callback_query: CallbackQuery, state: FSMContext
):
    user_id = callback_query.from_user.id
    async with MySession() as session:
        await session.patch(
            f"{API_ENDPOINT}/subscription_notifications/{user_id}",
            json={
                "user_id": user_id,
                "enable_notifications": True if callback_query.data.startswith("enable") else False
            }
        )
        
    await show_subscription_section(callback_query, state)
