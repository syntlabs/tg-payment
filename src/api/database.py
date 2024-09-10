from logging import getLogger

from asyncpg import create_pool, Pool
from fastapi import Request

from config import (
    POSTGRES_HOST, POSTGRES_NAME,
    POSTGRES_PASSWORD, POSTGRES_PORT,
    POSTGRES_USER
)


DSN = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_NAME}"

logger = getLogger(__name__)

class Database():
    async def create_pool(self):
        logger.info("Pool has been succsessfully created")
        self.pool = await create_pool(DSN)
    
    async def close_pool(self):
        await self.pool.close()
    
    async def execute():
        pass


def get_pool_from_request(request: Request) -> Pool:
    return request.app.state.db_pool
