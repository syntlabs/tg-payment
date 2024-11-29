"""
ENDPOINT: .../api/v1/subscription_notifications
"""

from logging import getLogger

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND

from database import get_pool_from_request
from models import SubscriptionNotification


router = APIRouter()

logger = getLogger(__name__)

@router.patch("/{telegram_id}")
async def patch_subscription_notification(
    request: Request, telegram_id: int, subscription_notification: SubscriptionNotification
):
    pool = get_pool_from_request(request)
    
    # Проверка на существование записи
    async with pool.acquire() as con:
        stored_rec = await con.fetchrow(
            "SELECT * FROM subscription_notifications WHERE user_id = $1;", telegram_id
        )

    if not stored_rec:
        return JSONResponse(
        {"message": f"record with telegram_id: {telegram_id} not found"},
        HTTP_404_NOT_FOUND
    )
    
    # Обновление записи
    update_data = subscription_notification.model_dump(exclude_unset=True)
    updated_rec = SubscriptionNotification(**stored_rec).model_copy(update=update_data)
    
    async with pool.acquire() as con:
        await con.execute(
            """
            UPDATE subscription_notifications
            SET enable_notifications = $1, date_of_notification = $2, notified = $3
            WHERE user_id = $4;
            """,
            updated_rec.enable_notifications, updated_rec.date_of_notification,
            updated_rec.notified, telegram_id
        )
    updated_rec.user_id = telegram_id
    return Response(updated_rec.model_dump_json())


@router.get("/all")
async def get_users_to_notify(request: Request):
    pool = get_pool_from_request(request)
    async with pool.acquire() as con:
        records = await con.fetch(
            """
            SELECT user_id FROM subscription_notifications
            WHERE date_of_notification < CURRENT_TIMESTAMP
            AND enable_notifications = true
            AND notified = false;
            """
        )
    
    return JSONResponse([dict(record) for record in records])


@router.get("/{telegram_id}")
async def get_subscription_notification_state(
    request: Request, telegram_id: int
):
    pool = get_pool_from_request(request)
    async with pool.acquire() as con:
        rec = await con.fetchrow(
            """
            SELECT * FROM subscription_notifications
            WHERE user_id = $1;
            """, telegram_id
        )
    if rec:
        record_mapping = {k: v for k, v in rec.items()}
        return Response(SubscriptionNotification(**record_mapping).model_dump_json())
    return JSONResponse(
        {"message": f"record with telegram_id: {telegram_id} not found"},
        status_code=HTTP_404_NOT_FOUND
    )
