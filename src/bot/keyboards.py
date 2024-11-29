from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import (
    FAQ_LINK, SUPPORT_BOT_LINK,
    WEEK_SUBSCRIPTION_COST,
    ONE_MONTH_SUBSCRIPTION_COST,
    THREE_MONTHS_SUBSCRIPTION_COST,
    SIX_MONTHS_SUBSCRIPTION_COST,
    YEAR_SUBSCRIPTION_COST
)
from locales import MESSAGES


BACK_BTN = lambda language: InlineKeyboardButton(
    text=MESSAGES["back_btn_text"][language],
    callback_data="back_cbd"
)

def create_profile_markup(language: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=MESSAGES["subscription_btn_text"][language],
                callback_data="subscription_cbd"
            )],
            [InlineKeyboardButton(
                text=MESSAGES["referral_system_btn_text"][language],
                callback_data="referral_system_cbd"
            )],
            [InlineKeyboardButton(
                text=MESSAGES["support_btn_text"][language],
                url=SUPPORT_BOT_LINK
            )],
            [InlineKeyboardButton(
                text="FAQ",
                url=FAQ_LINK
            )]
        ]
    )


def create_subscription_markup(
    language: str,
    notification_status: bool = True,
    has_subscription: bool = False
) -> InlineKeyboardMarkup:
    inline_keyboard=[]
    
    if not has_subscription:
        inline_keyboard.append([InlineKeyboardButton(
            text=MESSAGES["buy_subscription_btn_text"][language],
            callback_data="buy_subscription_cbd"
        )])
    else:
        inline_keyboard.append([InlineKeyboardButton(
            text=MESSAGES["renew_subscription_btn_text"][language],
            callback_data="renew_subscription_cbd"
        )])
    
    if notification_status:
        inline_keyboard.append([InlineKeyboardButton(
            text=MESSAGES["disable_notifications_btn_text"][language],
            callback_data="disable_notifications_cbd"
        )])
    else:
        inline_keyboard.append([InlineKeyboardButton(
            text=MESSAGES["enable_notifications_btn_text"][language],
            callback_data="enable_notifications_cbd"
        )])
    
    inline_keyboard.append([BACK_BTN(language)])
    
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def create_select_of_period_markup(language: str) -> InlineKeyboardMarkup:
    inline_keyboard=[[BACK_BTN(language)]]
    
    subscription_periods = (
        (
            "week_period_of_subscription",
            MESSAGES["week_period_of_subscription_btn_text"][language],
            WEEK_SUBSCRIPTION_COST
        ),
        (
            "one_month_period_of_subscription",
            MESSAGES["one_month_period_of_subscription_btn_text"][language],
            ONE_MONTH_SUBSCRIPTION_COST
        ),
        (
            "three_months_period_of_subscription",
            MESSAGES["three_months_period_of_subscription_btn_text"][language],
            THREE_MONTHS_SUBSCRIPTION_COST
        ),
        (
            "six_months_period_of_subscription",
            MESSAGES["six_months_period_of_subscription_btn_text"][language],
            SIX_MONTHS_SUBSCRIPTION_COST
        ),
        (
            "year_period_of_subscription",
            MESSAGES["year_period_of_subscription_btn_text"][language],
            YEAR_SUBSCRIPTION_COST
        ),
    )
    
    for i, period in enumerate(subscription_periods):
        inline_keyboard.insert(i, [InlineKeyboardButton(
            text=period[1].format(period[2]),
            callback_data=period[0]
        )])
        
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def create_confirm_purchase_markup(
    language: str
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=MESSAGES["confirm_purchase_btn_text"][language],
                callback_data="confirm_purchase_cbd"
            )],
            [BACK_BTN(language)]
        ]
    )


def create_payment_markup(
    language: str
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=MESSAGES["top_up_balance_btn_text"][language],
                pay=True
            )],
            [BACK_BTN(language)]
        ]
    )


def create_referall_system_markup(
    language: str, has_referrer: bool
) -> InlineKeyboardMarkup:
    inline_keyboard=[
        [InlineKeyboardButton(
            text=MESSAGES["get_referral_link_btn_text"][language],
            callback_data="get_referral_link_cbd"
        )],
        [BACK_BTN(language)]
    ]
    
    if not has_referrer:
        inline_keyboard.insert(1, [InlineKeyboardButton(
            text=MESSAGES["become_referral_btn_text"][language],
            callback_data="become_referral_cbd"
        )])
        
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def create_become_referral_markup(language: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[BACK_BTN(language)]]
    )
