"""
ENDPOINT: .../api/v1/users
"""

from logging import getLogger
from typing import Optional, Union

from asyncpg import Pool
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_201_CREATED, HTTP_404_NOT_FOUND
)

from database import get_pool_from_request
from models import User


logger = getLogger(__name__)

router = APIRouter()

@router.post("/add")
async def add_user(request: Request, user: User):
    pool = get_pool_from_request(request)
    
    # Если пользователь повторно прописал /start в боте, то возвращаем существующего пользователя
    user_from_db = await _get_user_by_tg_id(user.telegram_id, pool)    
    if user_from_db:
        return JSONResponse(user_from_db)
    
    async with pool.acquire() as con:
        user_rec = await con.fetchrow(
            "INSERT INTO users(telegram_id, referrer_uuid) VALUES($1, $2) RETURNING *;",
            user.telegram_id, user.referrer_uuid
        )
    
    return JSONResponse({k: v for k, v in user_rec.items()}, HTTP_201_CREATED)


@router.get("/{id}")
async def get_user(request: Request, id: Union[int, str]):
    """id может быть как telegram_id пользователя, так и referrer_uuid"""
    pool = get_pool_from_request(request)
    id = str(id)
    
    # Получение пользователя по telegram_id
    if id.isdigit():
        id = int(id)
        user_from_db = await _get_user_by_tg_id(id, pool)
        
        if user_from_db:
            return JSONResponse(user_from_db)
        
        return JSONResponse(
            {"message": f"user with telegram_id: {id} not found"},
            HTTP_404_NOT_FOUND
        )
    
    # Получение пользователя по referral_uuid
    async with pool.acquire() as con:
        rec = await con.fetchrow(
            "SELECT * FROM users WHERE referrer_uuid = $1;", id
        )
    
    if rec:
        record_mapping = {k: v for k, v in rec.items()}
        return JSONResponse(record_mapping)
    return JSONResponse(
        {"message": f"user with referrer_uuid: {id} not found"},
        HTTP_404_NOT_FOUND
    )


async def _get_user_by_tg_id(telegram_id: int, pool: Pool) -> Optional[User]:
    async with pool.acquire() as con:
        rec = await con.fetchrow(
            "SELECT * FROM users WHERE telegram_id = $1;", telegram_id
        )
    if rec:
        record_mapping = {k: v for k, v in rec.items()}
        return record_mapping
    return None
