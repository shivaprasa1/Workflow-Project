
from sqlalchemy import select, func , update
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.notification import Notification


def create_notification(
    db: Session,
    recipient_id: int,
    actor_id: int | None,
    task_id: int | None,
    notification_type: str,
    message: str
):

    # Do not notify a user about their own action.
    if recipient_id == actor_id:
        return None

    notification = Notification(
        recipient_id=recipient_id,
        actor_id=actor_id,
        task_id=task_id,
        notification_type=notification_type,
        message=message,
        is_read=False
    )

    db.add(notification)

    return notification


def get_user_notifications(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20
):

    return db.execute(
        select(Notification)
        .where(Notification.recipient_id == user_id)
        .order_by(Notification.created_at.desc(), Notification.id.desc())
        .offset(skip)
        .limit(limit)
    ).scalars().all()


def get_unread_count(
    db: Session,
    user_id: int
):

    count = db.scalar(
        select(func.count(Notification.id))
        .where(
            Notification.recipient_id == user_id,
            Notification.is_read.is_(False)
        )
    )

    return {"unread_count": count or 0}


def mark_notification_as_read(
    db: Session,
    notification_id: int,
    user_id: int
):

    notification = db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.recipient_id == user_id
        )
    ).scalar_one_or_none()

    if notification is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found."
        )

    notification.is_read = True

    db.commit()
    db.refresh(notification)

    return notification

def mark_all_notifications_as_read(db: Session, user_id: int):
    result = db.execute(
        update(Notification)
        .where(
            Notification.recipient_id == user_id,
            Notification.is_read == False
        )
        .values(is_read=True)
    )

    db.commit()

    return result.rowcount or 0
