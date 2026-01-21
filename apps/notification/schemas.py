from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from .models import NotificationTypeChoices


class NotificationCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # title: str
    message: str
    notification_type: NotificationTypeChoices = NotificationTypeChoices.SYSTEM


class UserNotificationCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    notification_id: int
    is_read: Optional[bool] = False
    read_at: Optional[datetime] = None


class NotificationListSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    message: str
    notification_type: NotificationTypeChoices
    created_at: datetime
    updated_at: datetime


class UserNotificationListSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    notification_id: int
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
