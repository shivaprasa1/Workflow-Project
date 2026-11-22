
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.device_token import DeviceToken


def register_device_token(
    db: Session,
    user_id: int,
    device_token: str,
    platform: str
):
    """
    Register a device token or update its owner/platform.
    """

    existing_token = db.execute(
        select(DeviceToken).where(
            DeviceToken.device_token == device_token
        )
    ).scalar_one_or_none()

    if existing_token:
        existing_token.user_id = user_id
        existing_token.platform = platform

        db.commit()
        db.refresh(existing_token)

        return existing_token

    new_token = DeviceToken(
        user_id=user_id,
        device_token=device_token,
        platform=platform
    )

    db.add(new_token)
    db.commit()
    db.refresh(new_token)

    return new_token


def remove_device_token(
    db: Session,
    user_id: int,
    device_token: str
):
    """
    Remove a device token belonging to the current user.
    """

    existing_token = db.execute(
        select(DeviceToken).where(
            DeviceToken.user_id == user_id,
            DeviceToken.device_token == device_token
        )
    ).scalar_one_or_none()

    if existing_token is None:
        return False

    db.delete(existing_token)
    db.commit()

    return True
