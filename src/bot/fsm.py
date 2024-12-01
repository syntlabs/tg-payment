from aiogram.fsm.state import StatesGroup, State


class FSMSections(StatesGroup):
    start_section = State()
    subscription_section = State()
    period_section = State()
    confirm_purchase = State()
    payment_section = State()
    referral_system_section = State()
    become_referral_section = State()
