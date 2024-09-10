from logging import getLogger
from typing import Union

from aiogram import F, Router
from aiogram.filters import CommandStart, Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.deep_linking import encode_payload, decode_payload

from api_client_session import MySession
from config import API_SERVICE_NAME, API_SERVICE_PORT
from fsm import FSMSections
from keyboards import create_profile_markup
from locales import MESSAGES
from utils import get_user_language


router = Router()

logger = getLogger(__name__)

@router.message(F.caption)
async def handle_message_with_caption(message: Message):
    language = get_user_language(message)
    logger.info(language)
    await message.answer(
        MESSAGES
        .get("error_messages_for_user")
        .get("bot_does_not_process_attachments")
        .get(language)
    )


@router.message(or_f(CommandStart(), Command("help"), Command("profile")))
async def handle_start_command(
    message: Message, state: FSMContext
):
    if message.text.startswith("/start"):
        payload_of_user = encode_payload(str(message.from_user.id))
        async with MySession() as session:
            await session.post(
                f"http://{API_SERVICE_NAME}:{API_SERVICE_PORT}/api/v1/users/add",
                json={
                    "telegram_id": message.from_user.id,
                    "referrer_uuid": payload_of_user
                }
            )
        
        referrer_id = message.text.replace("/start", "").replace(" ", "")
        if referrer_id:
            referrer_id = int(decode_payload(referrer_id))
            async with MySession() as session:
                await session.post(
                    f"http://{API_SERVICE_NAME}:{API_SERVICE_PORT}/api/v1/referrals/add",
                    json={
                        "referral_id": message.from_user.id,
                        "referrer_id": referrer_id
                    }
                )
        
        await show_profile_section(message, state, is_start_message=True)
        return

    await show_profile_section(message, state)


@router.message(FSMSections.become_referral_section)
async def handle_become_referral_message(
    message: Message, state: FSMContext
):
    language = get_user_language(message)
    async with MySession() as session:
        status_code, referrer_json = await session.get(
            f"http://{API_SERVICE_NAME}:{API_SERVICE_PORT}/api/v1/users/{message.text}"
        )
    if status_code == 404:
        await message.answer(
            MESSAGES["user_with_such_an_invitation_code_does_not_exist_text"][language]
        )
        return
    
    referrer_id = referrer_json.get("telegram_id")
    async with MySession() as session:
        status_code, referrer_json = await session.post(
            f"http://{API_SERVICE_NAME}:{API_SERVICE_PORT}/api/v1/referrals/add",
            json={
                "referrer_id": referrer_id,
                "referral_id": message.from_user.id
            }
        )
    
    await message.delete()
    await message.answer(
        text=MESSAGES["you_have_successfully_become_referral_text"][language]
    )
    await state.set_state(None)


async def show_profile_section(
    obj: Union[Message, CallbackQuery], state: FSMContext,
    is_start_message: bool = False
):
    async with MySession() as session:
        _, user_json = await session.get(
            f"http://{API_SERVICE_NAME}:{API_SERVICE_PORT}/api/v1/users/{obj.from_user.id}"
        )
    user_balance = user_json.get("balance")
    
    async with MySession() as session:
        _, resp = await session.get(
            f"http://{API_SERVICE_NAME}:{API_SERVICE_PORT}/api/v1/referrals/{obj.from_user.id}"
        )
    referral_qty = len(resp)
    
    language = get_user_language(obj)
    
    message_text = MESSAGES["profile_text"][language].format(user_balance, referral_qty)
    if is_start_message:
        message_text = MESSAGES["start_text"][language] + "\n" + message_text
        
    if isinstance(obj, Message):
        my_message = await obj.answer(
            message_text,
            reply_markup=create_profile_markup(language)
        )
    else:
         my_message = await obj.message.answer(
            message_text,
            reply_markup=create_profile_markup(language)
        )
