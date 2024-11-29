from datetime import datetime
from typing import Union

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from api_client_session import MySession
from config import API_ENDPOINT, PERCENTAGE_OF_REFERRALS
from fsm import FSMSections
from keyboards import (
    create_profile_markup,
    create_referall_system_markup,
    create_select_of_period_markup,
    create_subscription_markup
)
from locales import MESSAGES
from utils import get_user_language

from logging import getLogger

logger = getLogger(__name__)

async def show_profile_section(
    obj: Union[Message, CallbackQuery], state: FSMContext,
    is_start_message: bool = False
):
    user_id = obj.from_user.id
    async with MySession() as session:
        sub_code, sub_pesp = await session.get(
            f"{API_ENDPOINT}/subscriptions/{user_id}"
        )
        
        _, users_resp = await session.get(
            f"{API_ENDPOINT}/users/{user_id}"
        )
        
        _, referrals_resp = await session.get(
            f"{API_ENDPOINT}/referrals/{user_id}"
        )
    
    language = get_user_language(obj)
    
    user_balance = int(users_resp.get("balance"))        
    total_profit = referrals_resp.get("total_profit")
    
    if sub_code == 200:
        subscription_text = MESSAGES["with_subscription_text"][language].format(
            sub_pesp.get("code"),
            datetime.strptime(
                sub_pesp.get("expires_on"),
                "%Y-%m-%dT%H:%M:%S.%f"
            ).strftime("%Y-%m-%d. %H:%M:%S (UTC)")
        ) + "\n\n"
    else:
        subscription_text = ""

    user_balance_text = MESSAGES["user_balance_text"][language].format(user_balance) + "\n"
    referral_profit_text = MESSAGES["referral_profit_text"][language].format(total_profit)
    
    message_text = subscription_text + user_balance_text + referral_profit_text
    
    if is_start_message:
        message_text = MESSAGES["start_text"][language].format(PERCENTAGE_OF_REFERRALS) + "\n\n" + message_text
        
    if isinstance(obj, Message):
        await obj.answer(
            message_text,
            reply_markup=create_profile_markup(language)
        )
    else:
         await obj.message.answer(
            message_text,
            reply_markup=create_profile_markup(language)
        )
    
    await state.set_state(FSMSections.start_section)


async def show_subscription_section(
    obj: Union[Message, CallbackQuery], state: FSMContext
):
    if isinstance(obj, CallbackQuery):
        await obj.answer()
    
    user_id = obj.from_user.id
    async with MySession() as session:
        sub_code, sub_pesp = await session.get(
            f"{API_ENDPOINT}/subscriptions/{user_id}"
        )
        
        _, notif_resp = await session.get(
            f"{API_ENDPOINT}/subscription_notifications/{user_id}"
        )
    
    language = get_user_language(obj)
    
    if isinstance(obj, CallbackQuery):
        obj_edit_text = obj.message.edit_text
    else:
        obj_edit_text = obj.edit_text
    
    if sub_code == 404:
        await obj_edit_text(
            MESSAGES["wo_subscription_text"][language],
            reply_markup=create_subscription_markup(
                language, notif_resp.get("enable_notifications"), False
            )
        )
    elif sub_code == 200:
        await obj_edit_text(
            MESSAGES["with_subscription_text"][language]
            .format(
                sub_pesp.get("code"),
                datetime.strptime(
                    sub_pesp.get("expires_on"),
                    "%Y-%m-%dT%H:%M:%S.%f"
                ).strftime("%Y-%m-%d. %H:%M:%S (UTC)")
            ),
            reply_markup=create_subscription_markup(
                language, notif_resp.get("enable_notifications"), True
            )
        )
    
    await state.set_state(FSMSections.subscription_section)


async def show_period_section(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.answer()
    async with MySession() as session:
        _, user_json = await session.get(
            f"{API_ENDPOINT}/users/{callback_query.from_user.id}"
        )
    user_balance = int(user_json.get("balance"))

    language = get_user_language(callback_query)
    if callback_query.message.invoice:
        await callback_query.bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=MESSAGES["user_balance_text"][language].format(user_balance) + "\n\n" +
            MESSAGES["select_of_period_text"][language],
            reply_markup=create_select_of_period_markup(language)
        )
        await callback_query.message.delete()
    else: 
        await callback_query.message.edit_text(
            MESSAGES["user_balance_text"][language].format(user_balance) + "\n\n" +
            MESSAGES["select_of_period_text"][language],
            reply_markup=create_select_of_period_markup(language)
        )
    
    await state.set_state(FSMSections.period_section)


async def show_referral_system_section(
    callback_query: CallbackQuery, state: FSMContext
):
    user_id = callback_query.from_user.id
    language = get_user_language(callback_query)
    
    async with MySession() as session:
        status_code, resp = await session.get(
            f"{API_ENDPOINT}/referrals/{user_id}"
        )
    number_of_referrals = resp.get("count") if status_code == 200 else 0
    total_profit = resp.get("total_profit") if status_code == 200 else 0
    
    async with MySession() as session:
        _, referrer_rec = await session.get(
            f"{API_ENDPOINT}/referrals/referrer/{user_id}"
        )
    
    await callback_query.message.edit_text(
        MESSAGES["referral_system_text"][language]
        .format(PERCENTAGE_OF_REFERRALS, number_of_referrals, total_profit),
        reply_markup=create_referall_system_markup(language, bool(referrer_rec))
    )
    await callback_query.answer()
    await state.set_state(FSMSections.referral_system_section)
