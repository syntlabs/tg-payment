"""
ENDPOINT: .../api/v1/devices
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from database import get_pool_from_request
from models import Device


router = APIRouter()


@router.post("/add")
async def add_or_update_device(request: Request, device: Device):
    """
    Вызывать при добавлении устройства.
    Иногда для обновления значения last_used.
    """
    pool = get_pool_from_request(request)
    async with pool.acquire() as con:
        device_rec = await con.execute(
            """
            INSERT INTO devices(subscription_id, device_uuid, last_used)
            VALUES($1, $2, CURRENT_TIMESTAMP)
            ON CONFLICT(device_uuid)
            DO UPDATE SET last_used = CURRENT_TIMESTAMP, subscription_id = $1
            WHERE device_uuid = $2
            RETURNING *;
            """, device.subscription_id, device.device_uuid
        )
    
    return JSONResponse(
        dict(device_rec),
        status_code=HTTP_200_OK if device_rec else HTTP_404_NOT_FOUND
    )


@router.get("/has_subscription/{device_uuid}")
async def has_subscription(request: Request, device_uuid: str):
    """
    Активирована ли у пользователя с уже занесённым
    `device_uuid` подписка на данный момент.
    Response: {"has_subscription": result (bool)}
    """
    pool = get_pool_from_request(request)
    async with pool.acquire() as con:
        result = await con.fetchval(
            """
            SELECT EXISTS (
                SELECT 1 FROM devices d
                LEFT JOIN subscriptions s ON d.subscription_id = s.subscription_id
                WHERE d.device_uuid = $1
            );
            """, device_uuid
        )
    
    return JSONResponse(
        {"has_subscription": result},
        status_code=HTTP_200_OK if result else HTTP_404_NOT_FOUND
    )


@router.post("/prune")
async def prune_devices(request: Request):
    pool = get_pool_from_request(request)
    async with pool.acquire() as con:
        await con.execute(
            "SELECT delete_old_devices();"
        )
    
    return JSONResponse({"message": "successfully removed"})

