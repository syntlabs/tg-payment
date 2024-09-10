from fastapi import APIRouter

from .devices import router as devices_router
from .referrals import router as referrals_router
from .subscriptions import router as subscriptions_router
from .transactions import router as transactions_router
from .users import router as users_router


router = APIRouter(prefix="/api/v1")

router.include_router(devices_router, prefix="/devices")
router.include_router(referrals_router, prefix="/referrals")
router.include_router(subscriptions_router, prefix="/subscriptions")
router.include_router(transactions_router, prefix="/transactions")
router.include_router(users_router, prefix="/users")
