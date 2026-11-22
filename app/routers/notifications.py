
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.notification_schema import (
    NotificationResponse,
    NotificationCountResponse
)
from app.services.notification_service import (
    get_user_notifications,
    get_unread_count,
    mark_notification_as_read,
    mark_all_notifications_as_read
)
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# Get notification history
@router.get(
    "/",
    response_model=list[NotificationResponse]
)
def list_notifications(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_user_notifications(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )


# Get unread notification count
@router.get(
    "/unread-count",
    response_model=NotificationCountResponse
)
def unread_notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_unread_count(
        db=db,
        user_id=current_user.id
    )


# Mark one notification as read
@router.patch("/{notification_id}/read")
def mark_one_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return mark_notification_as_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )


# Mark all notifications as read
@router.patch("/read-all")
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return mark_all_notifications_as_read(
        db=db,
        user_id=current_user.id
    )
