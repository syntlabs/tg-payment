from logging import getLogger

from aiogram import F, Router
from aiogram.types import CallbackQuery, LabeledPrice
from aiogram.fsm.context import FSMContext

from api_client_session import MySession
import config
from fsm import FSMSections
from keyboards import create_confirm_purchase_markup, create_payment_markup
from locales import MESSAGES
from utils import get_user_language


router = Router()

logger = getLogger(__name__)

@router.callback_query(F.data.endswith("_period_of_subscription"))
async def handle_buy_subscription_cbd(
    callback_query: CallbackQuery, state: FSMContext
):
    selected_period = callback_query.data.replace("_period_of_subscription", "")
    price = getattr(config, f"{selected_period.upper()}_SUBSCRIPTION_COST")
    user_id = callback_query.from_user.id
    language = get_user_language(callback_query)
    
    await callback_query.answer()

    async with MySession() as session:
        _, response = await session.get(
            f"{config.API_ENDPOINT}/users/{user_id}"
        )
    
    user_balance = response.get("balance")
    for_additional_payment_of = price - int(user_balance)
    
    if for_additional_payment_of <= 0:
        await state.update_data({
            "period": selected_period,
            "price": price
        })
        
        selected_period_text = MESSAGES[f"{selected_period}_period_of_subscription_btn_text"][language].format(price)
        await callback_query.message.edit_text(
            text=MESSAGES["confirm_purchase_text"][language].format(selected_period_text),
            reply_markup=create_confirm_purchase_markup(language)
        )
        
        await state.set_state(FSMSections.confirm_purchase)
    
    else:
        prices = [LabeledPrice(label="XTR", amount=for_additional_payment_of)]
        await callback_query.message.answer_invoice(
            title=MESSAGES["balance_replenishment_text"][language],
            description=MESSAGES["payment_text"][language].format(for_additional_payment_of),
            payload=f"{for_additional_payment_of}_stars",
            currency="XTR",
            prices=prices,
            reply_markup=create_payment_markup(language)
        )
        
        await callback_query.message.delete()
        
        await state.set_state(FSMSections.payment_section)
