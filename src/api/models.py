from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TransactionType(Enum):
    became_referral = 'became_referral'
    referral_profit = 'referral_profit'
    balance_replenishment = 'balance_replenishment'
    subscription_purchase = 'subscription_purchase'

class User(BaseModel):
    telegram_id: Optional[int] = Field(...)
    referrer_uuid: Optional[str] = Field(None)

class Transaction(BaseModel):
    user_id: int
    balance_change: float
    transaction_type: TransactionType
    
    class Config:
        use_enum_values = True

class Referral(BaseModel):
    referrer_id: int
    referral_id: int

class SubscriptionNotification(BaseModel):
    user_id: int
    enable_notifications: bool
    date_of_notification: Optional[datetime] = Field(None)
    notified: bool = Field(True)

class Subscription(BaseModel):
    """`expires_on` the interval after which the subscription will end: 1 month, 3 months, etc."""
    owner_id: int
    code: str = Field(None)
    expires_on: str

class Device(BaseModel):
    subscription_id: int
    device_uuid: str
