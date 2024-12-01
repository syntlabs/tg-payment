from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from sections import show_referral_system_section, show_subscription_section


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
