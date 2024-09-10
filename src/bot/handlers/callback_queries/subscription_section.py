from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from api_client_session import MySession
from config import API_SERVICE_NAME, API_SERVICE_PORT
from fsm import FSMSections
from keyboards import (
    create_select_of_period_markup, create_subscription_markup
)
from locales import MESSAGES
from utils import get_user_language


router = Router()

@router.callback_query(F.data == "buy_subscription_cbd")
async def handle_buy_subscription_cbd(
    callback_query: CallbackQuery, state: FSMContext
):
    language = get_user_language(callback_query)
    await callback_query.message.edit_text(
        MESSAGES["select_of_period_text"][language],
        reply_markup=create_select_of_period_markup(language)
    )
    await callback_query.answer()
    await state.set_state(FSMSections.period_section)


@router.callback_query(
    F.data.in_(("disable_notifications_cbd", "enable_notifications_cbd"))
)
async def handle_switcher_of_notifications_cbd(
    callback_query: CallbackQuery
):
    language = get_user_language(callback_query)
    async with MySession() as session:
        _, user_json = await session.patch(
            f"http://{API_SERVICE_NAME}:{API_SERVICE_PORT}/api/v1/users/{callback_query.from_user.id}",
            json={
                "telegram_id": callback_query.from_user.id,
                "enable_notifications": True if callback_query.data.startswith("enable") else False
            }
        )
    await callback_query.message.edit_reply_markup(
        reply_markup=create_subscription_markup(language, user_json.get("enable_notifications"))
    )
    await callback_query.answer()

#TODO:
"""
Если у пользователя есть подписка, то в этой секции ему дополнительно отображается код активации, а в клавиатуре "Купить подписку" заменяется на "Продлить подписку"
"""
