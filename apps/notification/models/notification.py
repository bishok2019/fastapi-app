import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from base.models import BaseModel


class NotificationTypeChoices(str, enum.Enum):
    NEW_USER = "new_user"
    NEW_STOCK = "new_stock"
    SYSTEM = "system"
    WATCHLIST_UPDATE = "watchlist_update"


class Notification(BaseModel):
    __tablename__ = "notifications"

    # user_id = Column(Integer, index=True, nullable=False)
    title = Column(String(100), nullable=False)
    message = Column(String(255), nullable=False)
    notification_type = Column(
        Enum(NotificationTypeChoices, name="notification_type_enum"),
        nullable=False,
        default=NotificationTypeChoices.SYSTEM,
    )
    # Relationships
    user_notifications = relationship(
        "UserNotification",
        back_populates="notification",
        cascade="all, delete-orphan",
    )


class UserNotification(BaseModel):
    __tablename__ = "user_notifications"

    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    notification_id = Column(
        Integer, ForeignKey("notifications.id"), index=True, nullable=False
    )
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="user_notifications")
    notification = relationship("Notification", back_populates="user_notifications")
