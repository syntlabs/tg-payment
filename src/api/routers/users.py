"""
ENDPOINT: .../api/v1/users
"""

from logging import getLogger
from typing import Optional, Union

from asyncpg import Pool
from fastapi import APIRouter, Request, Response
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
        return Response(user_from_db.model_dump_json())
    
    # Создаём нового
    user = User(
        telegram_id=user.telegram_id, balance=0.00,
        enable_notifications=False,
        referrer_uuid=getattr(user, "referrer_uuid")
    )
    async with pool.acquire() as con:
        await con.execute(
            "INSERT INTO users(telegram_id, balance, enable_notifications, referrer_uuid) VALUES($1, $2, $3, $4);",
            user.telegram_id, user.balance,
            user.enable_notifications, user.referrer_uuid
        )
    
    return Response(user.model_dump_json(), HTTP_201_CREATED)


@router.patch("/{telegram_id}")
async def update_user(
    request: Request, telegram_id: int, updated_user_data: User
):
    pool = get_pool_from_request(request)
    
    # Проверка на существование пользователя
    stored_user_model = await _get_user_by_tg_id(telegram_id, pool)
    if not stored_user_model:
        return JSONResponse(
        {"message": f"user with telegram_id: {telegram_id} not found"},
        HTTP_404_NOT_FOUND
    )
    
    # Обновление пользователя
    update_data = updated_user_data.model_dump(exclude_unset=True)
    updated_user = stored_user_model.model_copy(update=update_data)
    
    async with pool.acquire() as con:
        await con.execute(
            "UPDATE users SET balance=$1, enable_notifications=$2 WHERE telegram_id=$3;",
            updated_user.balance, updated_user.enable_notifications, telegram_id
        )
    updated_user.telegram_id = telegram_id
    return Response(updated_user.model_dump_json())
    


@router.get("/{id}")
async def get_user(request: Request, id: Union[int, str]):
    pool = get_pool_from_request(request)
    id = str(id)
    
    # Получение пользователя по telegram_id
    if id.isdigit():
        id = int(id)
        user_from_db = await _get_user_by_tg_id(id, pool)
        
        if user_from_db:
            return Response(user_from_db.model_dump_json())
        return JSONResponse(
            {"message": f"user with telegram_id: {id} not found"},
            HTTP_404_NOT_FOUND
        )
    
    # Получение пользователя по referral_uuid
    async with pool.acquire() as con:
        rec = await con.fetchrow(
            "SELECT * FROM users WHERE referrer_uuid=$1;", id
        )
    
    if rec:
        record_mapping = {k: v for k, v in rec.items()}
        return Response(User(**record_mapping).model_dump_json())
    return JSONResponse(
        {"message": f"user with referrer_uuid: {id} not found"},
        HTTP_404_NOT_FOUND
    )


async def _get_user_by_tg_id(telegram_id: int, pool: Pool) -> Optional[User]:
    async with pool.acquire() as con:
        rec = await con.fetchrow(
            "SELECT * FROM users WHERE telegram_id=$1;", telegram_id
        )
    if rec:
        record_mapping = {k: v for k, v in rec.items()}
        return User(**record_mapping)
    return None
