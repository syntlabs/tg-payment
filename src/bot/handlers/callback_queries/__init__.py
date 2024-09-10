from aiogram import Router

from .back_btn import router as back_btn_router
from .start_section import router as start_section_router
from .subscription_section import router as subscription_section_router
from .period_section import router as period_section_router
from .payment_section import router as payment_section_router
from .referral_system_section import router as referral_system_section_router


router = Router()

router.include_routers(
    back_btn_router,
    payment_section_router,
    period_section_router,
    subscription_section_router,
    start_section_router,
    referral_system_section_router
)
