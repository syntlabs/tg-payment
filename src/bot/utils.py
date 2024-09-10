"""
This file contains functions for working with user states and data,
ensuring that user data is saved and loaded. As well as misc functions.
"""

from asyncio import sleep
from logging import getLogger
from typing import Union

from aiogram.types import CallbackQuery, Message

from locales import SUPPORTED_LANGUAGES
from storage import MyMemoryStorage


logger = getLogger(__name__)

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


def get_user_language(obj: Union[CallbackQuery, Message]) -> str:
    language = obj.from_user.language_code
    return language if language in SUPPORTED_LANGUAGES else "en"