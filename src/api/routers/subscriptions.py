"""
ENDPOINT: .../api/v1/subscriptions
"""

from logging import getLogger
from random import choice
from string import ascii_letters, ascii_lowercase, digits

from asyncpg.exceptions import UniqueViolationError
from fastapi import APIRouter, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
)

from database import get_pool_from_request
from models import Subscription


router = APIRouter()

logger = getLogger(__name__)

@router.post("/add")
async def add_or_update_subscription(request: Request, subscription: Subscription):
    pool = get_pool_from_request(request)
    try:
        count, interval_type = subscription.expires_on.split()
    except ValueError:
        return JSONResponse(
                {"message": "`expires_on` must be `n day | month | year`"},
                HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    if "week" in interval_type:
        q = """
            INSERT INTO subscriptions(owner_id, code, expires_on)
            VALUES($1, $2, CURRENT_TIMESTAMP + ($3 || ' week')::INTERVAL)
            ON CONFLICT(owner_id)
            DO UPDATE SET expires_on =
                CASE 
                    WHEN subscriptions.expires_on < CURRENT_TIMESTAMP THEN CURRENT_TIMESTAMP + ($3 || ' week')::INTERVAL
                    ELSE subscriptions.expires_on + ($3 || ' week')::INTERVAL
                END
            WHERE subscriptions.owner_id = $1
            RETURNING *;
            """
    elif "month" in interval_type:
        q = """
            INSERT INTO subscriptions(owner_id, code, expires_on)
            VALUES($1, $2, CURRENT_TIMESTAMP + ($3 || ' month')::INTERVAL)
            ON CONFLICT(owner_id)
            DO UPDATE SET expires_on =
                CASE 
                    WHEN subscriptions.expires_on < CURRENT_TIMESTAMP THEN CURRENT_TIMESTAMP + ($3 || ' month')::INTERVAL
                    ELSE subscriptions.expires_on + ($3 || ' month')::INTERVAL
                END
            WHERE subscriptions.owner_id = $1
            RETURNING *;
            """
    elif "year" in interval_type:
        q = """
            INSERT INTO subscriptions(owner_id, code, expires_on)
            VALUES($1, $2, CURRENT_TIMESTAMP + ($3 || ' year')::INTERVAL)
            ON CONFLICT(owner_id)
            DO UPDATE SET expires_on =
                CASE 
                    WHEN subscriptions.expires_on < CURRENT_TIMESTAMP THEN CURRENT_TIMESTAMP + ($3 || ' year')::INTERVAL
                    ELSE subscriptions.expires_on + ($3 || ' year')::INTERVAL
                END
            WHERE subscriptions.owner_id = $1
            RETURNING *;
            """
    else:
        q = """
            INSERT INTO subscriptions(owner_id, code, expires_on)
            VALUES($1, $2, CURRENT_TIMESTAMP + ($3 || ' day')::INTERVAL)
            ON CONFLICT(owner_id)
            DO UPDATE SET expires_on =
                CASE 
                    WHEN subscriptions.expires_on < CURRENT_TIMESTAMP THEN CURRENT_TIMESTAMP + ($3 || ' day')::INTERVAL
                    ELSE subscriptions.expires_on + ($3 || ' day')::INTERVAL
                END
            WHERE subscriptions.owner_id = $1
            RETURNING *;
            """

    while True:
        subscription.code = _generate_code()
        try:
            
            async with pool.acquire() as con:
                await con.execute(
                    q,
                    subscription.owner_id, subscription.code,
                    count
                )
            break
        except UniqueViolationError:
            # Если сгенерировался код, который уже есть в БД, то идём на следующий круг
            pass
        except Exception:
            # Хьюстон, у нас проблемы! (неизвестная ошибка)
            logger.exception("Couldn't add or update a subscription.")
            return Response(
                {"message": "couldn't add or update a subscription"},
                HTTP_500_INTERNAL_SERVER_ERROR
            )

    return Response(subscription.model_dump_json())


@router.get("/{tg_id_or_code}")
async def get_subscription(request: Request, tg_id_or_code: str):
    """
    `tg_id_or_code` - telegram_id (int) или код активации,
    который пользователь ввёл в приложение
    """
    pool = get_pool_from_request(request)
    async with pool.acquire() as con:
        if tg_id_or_code.isdigit():
            subscription = await con.fetchrow(
                "SELECT * FROM subscriptions WHERE owner_id = $1;", int(tg_id_or_code)
            )
        else:
            subscription = await con.fetchrow(
                "SELECT * FROM subscriptions WHERE code = $1;", tg_id_or_code
            )
    
    if subscription:
        subscription = {k: v for k, v in subscription.items()}
        return JSONResponse(jsonable_encoder(subscription))
    
    if tg_id_or_code.isdigit():
        message_text = f"the subscription for user `{tg_id_or_code}` not found"
    else:
        message_text = f"the subscription with code `{tg_id_or_code}` not found"
        
    return JSONResponse(
        {"message": message_text},
        status_code=HTTP_404_NOT_FOUND
    )


def _generate_code(length: int = 10) -> str:
    return "".join([
        choice(ascii_letters + ascii_lowercase + digits) for _ in range(length)
    ])
