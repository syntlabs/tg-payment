from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link

from fsm import FSMSections
from keyboards import create_become_referral_markup
from locales import MESSAGES
from utils import get_user_language


router = Router()

@router.callback_query(F.data == "get_referral_link_cbd")
async def handle_get_referral_link_cbd(
    callback_query: CallbackQuery
):
    language = get_user_language(callback_query)
    link = await create_start_link(
        bot=callback_query.bot,
        payload=str(callback_query.from_user.id),
        encode=True
    )
    await callback_query.answer()
    await callback_query.message.answer(
        MESSAGES["your_referral_link_text"][language].format(link, link.split("start=")[-1]),
        parse_mode=ParseMode.HTML
    )
    

@router.callback_query(F.data == "become_referral_cbd")
async def handle_become_referral_cbd(
    callback_query: CallbackQuery, state: FSMContext
):
    language = get_user_language(callback_query)
    await callback_query.message.edit_text(
        text=MESSAGES["enter_code_of_user_who_invited_you_text"][language],
        reply_markup=create_become_referral_markup(language)
    )
    await callback_query.answer()
    await state.set_state(FSMSections.become_referral_section)
    