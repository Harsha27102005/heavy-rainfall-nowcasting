# backend/app/schemas/notification.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificationBase(BaseModel):
    warning_id: str
    message: str
    channel: str
    recipient: Optional[str] = None
    status: str = "pending"

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: str
    timestamp: datetime

    model_config = {"from_attributes": True}