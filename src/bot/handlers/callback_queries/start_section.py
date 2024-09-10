from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from api_client_session import MySession
from config import API_SERVICE_NAME, API_SERVICE_PORT
from fsm import FSMSections
from keyboards import create_subscription_markup, create_referall_system_markup
from locales import MESSAGES
from utils import get_user_language


router = Router()

@router.callback_query(F.data == "subscription_cbd")
async def handle_subscription_cbd(
    callback_query: CallbackQuery, state: FSMContext
):
    await show_subscription_section(callback_query, state)


@router.callback_query(F.data == "referral_system_cbd")
async def handle_referral_system_cbd(
    callback_query: CallbackQuery, state: FSMContext
):
    await show_referral_system_section(callback_query, state)


async def show_subscription_section(
    callback_query: CallbackQuery, state: FSMContext
):
    language = get_user_language(callback_query)
    async with MySession() as session:
        _, response = await session.get(
            f"http://{API_SERVICE_NAME}:{API_SERVICE_PORT}/api/v1/users/{callback_query.from_user.id}"
        )
    await callback_query.message.edit_text(
        MESSAGES["subscription_text"][language],
        reply_markup=create_subscription_markup(
            language, response.get("enable_notifications", False)
        )
    )
    await callback_query.answer()
    await state.set_state(FSMSections.subscription_section)


async def show_referral_system_section(
    callback_query: CallbackQuery, state: FSMContext
):
    language = get_user_language(callback_query)
    profit_from_referals = 0.00 # TODO: calculate profit
    
    async with MySession() as session:
        _, referrals = await session.get(
            f"http://{API_SERVICE_NAME}:{API_SERVICE_PORT}/api/v1/referrals/{callback_query.from_user.id}"
        )
    referral_qty = len(referrals)
    
    async with MySession() as session:
        _, referrer_rec = await session.get(
            f"http://{API_SERVICE_NAME}:{API_SERVICE_PORT}/api/v1/referrals/referrer/{callback_query.from_user.id}"
        )
    
    await callback_query.message.edit_text(
        MESSAGES["referral_system_text"][language]
        .format(referral_qty, profit_from_referals),
        reply_markup=create_referall_system_markup(language, bool(referrer_rec))
    )
    await callback_query.answer()
    await state.set_state(FSMSections.referral_system_section)
