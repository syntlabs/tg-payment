from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    telegram_id: Optional[int] = Field(...)
    balance: Optional[float] = Field(None)
    enable_notifications: Optional[bool] = Field(None)
    referrer_uuid: Optional[str] = Field(None)

class Transaction(BaseModel):
    user_id: int
    balance_change: float
    date_time: datetime
    comment: str = Field(None)

class Referral(BaseModel):
    referrer_id: int
    referral_id: int

class Subscription(BaseModel):
    owner_id: int
    code: str = Field(None)
    expires_on: datetime

class Device(BaseModel):
    subscription_id: int
    device_uuid: str
    last_used: datetime
