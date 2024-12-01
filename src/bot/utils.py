"""
This file contains functions for working with user states and data,
ensuring that user data is saved and loaded. As well as misc functions.
"""

from asyncio import sleep
from enum import Enum
from logging import getLogger
from typing import Union

from aiogram import Bot
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import CallbackQuery, Message

from api_client_session import MySession
from config import API_ENDPOINT
from locales import MESSAGES, SUPPORTED_LANGUAGES
from storage import MyMemoryStorage


logger = getLogger(__name__)


class PeriodEnum(Enum):
    week = "1 week"
    one_month = "1 month"
    three_months = "3 months"
    six_months = "6 months"
    year = "1 year"


async def auto_save_storage(storage: MyMemoryStorage) -> None:
    """
    This function saves data to the database and storage every 20 seconds.

    Args:
    storage: The storage to save.
    """
    while True:
        try:
            await storage.save_storage()
        except Exception as e:
            logger.error("Failed to save data: %s", e)
        await sleep(20)


async def start_pruninig_devices():
    while True:
        async with MySession() as session:
            await session.post(
                f"{API_ENDPOINT}/devices/prune"
            )
        await sleep(3600)


async def start_subscription_termination_notification_service(
    bot: Bot, storage: MyMemoryStorage
):
    while True:
        async with MySession() as session:
            status, records = await session.get(
                f"{API_ENDPOINT}/subscription_notifications/all"
            )
            
            if status == 200 and records:
                for rec in records:
                    user_id = rec["user_id"]
                    user_storage_key = StorageKey(
                        bot_id=bot.id,
                        chat_id=rec["user_id"],
                        user_id=rec["user_id"]
                    )
                    user_data = await storage.get_data(user_storage_key)
                    language = user_data.get("language") or "en"
                    
                    await bot.send_message(
                        chat_id=user_id,
                        text=MESSAGES["subscription_is_about_to_expire_text"][language]
                    )
                    
                    await session.patch(
                        f"{API_ENDPOINT}/subscription_notifications/{user_id}",
                        json={
                            "notified": True
                        }
                    )
        
        await sleep(1800)


def get_user_language(obj: Union[CallbackQuery, Message]) -> str:
    language = obj.from_user.language_code
    return language if language in SUPPORTED_LANGUAGES else "en"