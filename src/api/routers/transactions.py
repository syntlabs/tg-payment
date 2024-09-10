"""
ENDPOINT: .../api/v1/transactions
"""

from logging import getLogger

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_201_CREATED

from database import get_pool_from_request
from models import Transaction


router = APIRouter()

logger = getLogger(__name__)

@router.post("/add")
async def add_transaction(request: Request, transaction: Transaction):
    pool = get_pool_from_request(request)
    async with pool.acquire() as con:
        await con.execute(
            "INSERT INTO transactions(user_id, balance_change, date_time, comment) VALUES($1, $2, $3, $4);",
            transaction.user_id, transaction.balance_change,
            transaction.date_time, transaction.comment
        )
    return JSONResponse(
        transaction.model_dump_json(), status_code=HTTP_201_CREATED
    )
