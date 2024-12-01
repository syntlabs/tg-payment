from logging import getLogger

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.deep_linking import encode_payload, decode_payload

from api_client_session import MySession
from config import API_ENDPOINT
from fsm import FSMSections
from locales import MESSAGES
from sections import show_profile_section
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


@router.message(Command("help", "profile", "menu", "start"))
async def handle_start_command(
    message: Message, state: FSMContext
):
    if message.text.startswith("/start"):
        await state.update_data({"language": get_user_language(message)})
        
        payload_of_user = encode_payload(str(message.from_user.id))
        async with MySession() as session:
            await session.post(
                f"{API_ENDPOINT}/users/add",
                json={
                    "telegram_id": message.from_user.id,
                    "referrer_uuid": payload_of_user
                }
            )
        
        referrer_id = message.text.replace("/start", "").replace(" ", "")
        if referrer_id:
            try:
                referrer_id = int(decode_payload(referrer_id))
            except UnicodeDecodeError:
                async with MySession() as session:
                    code, resp = await session.get(
                        f"{API_ENDPOINT}/users/{referrer_id}"
                    )
                
                if code == 200:
                    referrer_id = resp.get("telegram_id")
            
            except Exception:
                referrer_id = None
                logger.exception("failed to get referrer_id")
            
            if referrer_id:
                async with MySession() as session:
                    await session.post(
                        f"{API_ENDPOINT}/referrals/add",
                        json={
                            "referrer_id": referrer_id,
                            "referral_id": message.from_user.id
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
            f"{API_ENDPOINT}/users/{message.text}"
        )
    if status_code == 404:
        await message.answer(
            MESSAGES["user_with_such_an_invitation_code_does_not_exist_text"][language]
        )
        return
    
    referrer_id = referrer_json.get("telegram_id")
    async with MySession() as session:
        await session.post(
            f"{API_ENDPOINT}/referrals/add",
            json={
                "referrer_id": referrer_id,
                "referral_id": message.from_user.id
            }
        )
    
    data = await state.get_data()
    temp_message_id = data.get("temp_message")
    if temp_message_id:
        await message.bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=temp_message_id,
            reply_markup=None
        )
    
    await message.answer(
        text=MESSAGES["you_have_successfully_become_referral_text"][language]
    )
    await state.set_state(None)
