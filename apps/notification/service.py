from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.authentication.models import User

from .models import Notification, NotificationTypeChoices, UserNotification


async def create_notification_for_all_users(
    db: AsyncSession,
    message: str,
    notification_type: NotificationTypeChoices = NotificationTypeChoices.SYSTEM,
) -> Notification:
    """Create a notification and send it to all active users"""

    # Create the notification
    notification = Notification(
        message=message,
        notification_type=notification_type,
    )
    db.add(notification)
    await db.flush()  # Get the notification ID

    # Get all active users
    result = await db.execute(select(User).filter(User.is_active))
    active_users = result.scalars().all()

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
    await db.commit()
    await db.refresh(notification)

    return notification


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
