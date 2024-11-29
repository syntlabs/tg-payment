"""
ENDPOINT: .../api/v1/transactions
"""

from logging import getLogger

from asyncpg.exceptions import RaiseError
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from database import get_pool_from_request
from models import Transaction


router = APIRouter()

logger = getLogger(__name__)

@router.post("/add")
async def add_transaction(request: Request, transaction: Transaction):
    pool = get_pool_from_request(request)
    async with pool.acquire() as con:
        try:
            await con.execute(
                "INSERT INTO transactions(user_id, balance_change, transaction_type) VALUES($1, $2, $3);",
                transaction.user_id, transaction.balance_change,
                transaction.transaction_type
            )
        except RaiseError as e:
            return JSONResponse(
                {"error": e}, status_code=HTTP_400_BAD_REQUEST
            )
    
    return Response(
        transaction.model_dump_json(), status_code=HTTP_201_CREATED
    )
