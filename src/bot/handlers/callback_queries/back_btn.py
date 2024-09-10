from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from fsm import FSMSections
from .start_section import show_referral_system_section, show_subscription_section
from ..messages import show_profile_section

router = Router()

@router.callback_query(F.data == "back_cbd")
async def handle_switcher_of_notifications_cbd(
    callback_query: CallbackQuery,
    state: FSMContext
):
    await callback_query.answer()
    match await state.get_state():
        case FSMSections.subscription_section:
            await callback_query.message.delete()
            await show_profile_section(callback_query, state)
        case FSMSections.period_section:
            await show_subscription_section(callback_query, state)
        case FSMSections.payment_section:
            pass
        case FSMSections.referral_system_section:
            await callback_query.message.delete()
            await show_profile_section(callback_query, state)
        case FSMSections.become_referral_section:
            await show_referral_system_section(callback_query, state)
