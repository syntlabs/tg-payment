from logging import getLogger

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery
from aiogram.fsm.context import FSMContext

from api_client_session import MySession
from config import API_ENDPOINT
from locales import MESSAGES
from sections import show_profile_section, show_subscription_section
from utils import PeriodEnum, get_user_language


router = Router()
logger = getLogger(__name__)


@router.callback_query(F.data == "confirm_purchase_cbd")
async def handle_confirm_purchase_cbd(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    
    data = await state.get_data()
    selected_period = data.get("period")
    price = data.get("price")
    
    async with MySession() as session:
        await session.post(
            f"{API_ENDPOINT}/subscriptions/add",
            json={
                "owner_id": user_id,
                "expires_on": getattr(PeriodEnum, selected_period).value
            }
        )
        
        await session.post(
            f"{API_ENDPOINT}/transactions/add",
            json={
                "user_id": user_id,
                "balance_change": -price,
                "transaction_type": "subscription_purchase"
            }
        )
    
    await show_subscription_section(callback_query, state)


@router.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(ok=True)


@router.message(F.invoice, F.successful_payment)
async def on_successfull_payment(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    data = await state.get_data()
    selected_period = data.get("period")
    price = data.get("price")
    
    async with MySession() as session:
        await session.post(
            f"{API_ENDPOINT}/transactions/add",
            json={
                "user_id": user_id,
                "balance_change": message.invoice.total_amount,
                "transaction_type": "balance_replenishment"
            }
        )
        
        status, _ = await session.post(
            f"{API_ENDPOINT}/transactions/add",
            json={
                "user_id": user_id,
                "balance_change": -price,
                "transaction_type": "subscription_purchase"
            }
        )
        
        if status != 400:
            await show_profile_section(message, state)
            language = get_user_language(message)
            await message.answer(
                MESSAGES["insufficient_funds_text"][language]
            )
            return
        
        await session.post(
                f"{API_ENDPOINT}/subscriptions/add",
                json={
                    "owner_id": user_id,
                    "expires_on": getattr(PeriodEnum, selected_period).value
                }
            )
    
    await show_subscription_section(message, state)
