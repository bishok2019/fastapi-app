from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from apps.authentication.models import User
from apps.database import get_db

from .models import Notification, NotificationTypeChoices, UserNotification
from .schemas import NotificationCreateSchema


def create_notification_for_all_users(
    db: Session,
    notification: NotificationCreateSchema,
) -> Notification:
    """Create a notification and send it to all active users"""

    print(
        f"[DEBUG] Creating notification with title: {notification.title}, message: {notification.message}"
    )

    # Create the notification
    notification = Notification(
        message=notification.message,
        notification_type=notification.notification_type,
        title=notification.title,
    )
    db.add(notification)
    db.flush()  # Get the notification ID
    print(f"[DEBUG] Notification created with ID: {notification.id}")

    # Get all active users
    result = db.execute(select(User).filter(User.is_active))
    active_users = result.scalars().all()
    print(f"[DEBUG] Found {len(active_users)} active users")

    # Create user notifications for each active user
    user_notifications = [
        UserNotification(
            user_id=user.id,
            notification_id=notification.id,
            is_read=False,
        )
        for user in active_users
    ]

    db.add_all(user_notifications)
    # db.commit()# don't commit yet
    print(f"[DEBUG] Created {len(user_notifications)} user notifications")

    return notification  # now committed automatically by caller


async def create_notification_for_user(
    db: AsyncSession,
    user_id: int,
    message: str,
    notification_type: NotificationTypeChoices = NotificationTypeChoices.SYSTEM,
) -> Notification:
    """Create a notification for a specific user"""

    notification = Notification(
        message=message,
        notification_type=notification_type,
    )
    db.add(notification)
    await db.flush()

    user_notification = UserNotification(
        user_id=user_id,
        notification_id=notification.id,
        is_read=False,
    )
    db.add(user_notification)
    await db.commit()
    await db.refresh(notification)

    return notification
