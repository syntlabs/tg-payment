from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from locales import MESSAGES
from utils import get_user_language


router = Router()


#TODO:
"""
После выбора периода подсчитывается сумма (стоимость подписки - имеющийся баланс), необходимая для покупки подписки на выбранный период и выставляется счёт.
После оплаты сообщение со счётом удаляется и отправляется сгенерированный код, по которому пользователь активирует устройства в приложении.
"""
