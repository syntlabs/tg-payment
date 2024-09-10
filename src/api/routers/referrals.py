"""
ENDPOINT: .../api/v1/referrals
"""

from logging import getLogger

from asyncpg import UniqueViolationError
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR
)

from database import get_pool_from_request
from models import Referral


router = APIRouter()

logger = getLogger(__name__)

@router.post("/add")
async def add_referral(request: Request, referral: Referral):
    pool = get_pool_from_request(request)
    try:
        async with pool.acquire() as con:
            await con.execute(
                "INSERT INTO referrals(referrer_id, referral_id) VALUES($1, $2);",
                referral.referrer_id, referral.referral_id,
            )
        return Response(status_code=HTTP_201_CREATED)
    except UniqueViolationError:
        # Если у пользователя уже есть реферер (пригласивший его пользователь)
        return Response(status_code=HTTP_200_OK)
    except Exception:
        logger.exception("Couldn't add a referral.")
        return Response(status_code=HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/{telegram_id}")
async def get_referrals(request: Request, telegram_id: int):
    pool = get_pool_from_request(request)
    async with pool.acquire() as con:
        records = await con.fetch(
            "SELECT * FROM referrals WHERE referrer_id=$1;",
            telegram_id
        )
    return JSONResponse([
        {k: v for k, v in rec.items()} for rec in records
    ])


@router.get("/referrer/{telegram_id}")
async def get_referrer(request: Request, telegram_id: int):
    pool = get_pool_from_request(request)
    async with pool.acquire() as con:
        rec = await con.fetchrow(
            "SELECT * FROM referrals WHERE referral_id=$1;",
            telegram_id
        )
    if rec:
        return JSONResponse(dict(rec))
    return Response(status_code=HTTP_404_NOT_FOUND)
