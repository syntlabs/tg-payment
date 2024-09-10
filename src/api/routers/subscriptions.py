"""
ENDPOINT: .../api/v1/subscriptions
"""

from logging import getLogger
from random import choice
from string import ascii_letters, ascii_lowercase, digits

from asyncpg.exceptions import UniqueViolationError
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR
)

from database import get_pool_from_request
from models import Subscription


router = APIRouter()

logger = getLogger(__name__)

@router.post("/add")
async def add_subscription(request: Request, subscription: Subscription):
    pool = get_pool_from_request(request)

    while True:
        subscription.code = _generate_code()
        try:
            async with pool.acquire() as con:
                # Возвращает "INSERT 0 1", если подписка успешно создана, "INSERT 0 0" - в противном случае. Не добавляет запись, если подписка у пользователя уже есть.
                is_created = await con.execute(
                    "INSERT INTO subscriptions(owner_id, code, expires_on) VALUES($1, $2, $3) ON CONFLICT(owner_id) DO NOTHING RETURNING 1",
                    subscription.owner_id, subscription.code,
                    subscription.expires_on
                )
            break
        except UniqueViolationError:
            # Если сгенерировался код, который уже есть в БД, то идём на следующий круг
            pass
        except Exception:
            # Хьюстон, у нас проблемы! (неизвестная ошибка)
            logger.exception("Couldn't add a subscription.")
            return Response(
                {"message": "couldn't add a subscription"},
                HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    if bool(int(is_created[-1])):
        return Response(subscription.model_dump_json(), HTTP_201_CREATED)
    return JSONResponse({"message": "the subscription has already been added"})


def _generate_code(length: int = 10) -> str:
    return "".join([
        choice(ascii_letters + ascii_lowercase + digits) for _ in range(length)
    ])
