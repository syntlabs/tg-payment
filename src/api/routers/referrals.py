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
async def get_info_about_referrals(request: Request, telegram_id: int):
    pool = get_pool_from_request(request)
    async with pool.acquire() as con:
        count = await con.fetchval(
            """
            WITH RECURSIVE referral_chain AS (
                SELECT referrer_id, referral_id
                FROM referrals
                WHERE referrer_id = $1

                UNION ALL

                SELECT r.referrer_id, r.referral_id
                FROM referrals r
                INNER JOIN referral_chain rc ON r.referrer_id = rc.referral_id
            )
            SELECT DISTINCT COUNT(*)
            FROM referral_chain;
            """, telegram_id
        )
        
        total_profit = await con.fetchval(
            """
            SELECT SUM(balance_change)
            FROM transactions
            WHERE transaction_type = 'referral_profit'
            AND user_id = $1;
            """, telegram_id
        ) or 0

    return JSONResponse({"count": count, "total_profit": int(total_profit)})


@router.get("/referrer/{telegram_id}")
async def get_referrer(request: Request, telegram_id: int):
    pool = get_pool_from_request(request)
    async with pool.acquire() as con:
        referrer = await con.fetchval(
            "SELECT referrer_id FROM referrals WHERE referral_id = $1;",
            telegram_id
        )
    if referrer:
        return JSONResponse({"referrer": referrer})
    return Response(status_code=HTTP_404_NOT_FOUND)
