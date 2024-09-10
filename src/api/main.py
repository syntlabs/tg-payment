from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI

from database import Database
from routers import router as main_router


logger = getLogger(__name__)

db = Database()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    При старте приложения создаётся pool, по завершению - закрывается.
    """
    await db.create_pool()
    app.state.db_pool = db.pool
    
    yield
    
    await db.close_pool()

app = FastAPI(lifespan=lifespan)
app.include_router(main_router)
