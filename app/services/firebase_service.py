
import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, messaging
from dotenv import load_dotenv

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.device_token import DeviceToken




load_dotenv()


def initialize_firebase():
    """
    Initialize Firebase Admin SDK only once.
    """

    try:
        return firebase_admin.get_app()

    except ValueError:
        credentials_path = os.getenv(
            "FIREBASE_CREDENTIALS_PATH",
            "secrets/firebase-service-account.json"
        )

        project_root = Path(__file__).resolve().parents[2]
        credentials_file = project_root / credentials_path

        if not credentials_file.is_file():
            raise FileNotFoundError(
                "Firebase service-account credentials were not found."
            )

        firebase_credentials = credentials.Certificate(
            str(credentials_file)
        )

        return firebase_admin.initialize_app(
            firebase_credentials
        )


def send_push_notification(
    device_token: str,
    title: str,
    body: str,
    data: dict | None = None
):
    """
    Send a push notification to a device using FCM.
    """

    firebase_app = initialize_firebase()

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        data={
            str(key): str(value)
            for key, value in (data or {}).items()
        },
        token=device_token
    )

    return messaging.send(
        message,
        app=firebase_app
    )



logger = logging.getLogger(__name__)


def send_push_to_user(
    db: Session,
    user_id: int,
    title: str,
    body: str,
    data: dict | None = None
):
    """
    Send push notifications to all registered devices of a user.

    Push delivery failures must not interrupt database workflows.
    """

    device_tokens = db.execute(
        select(DeviceToken).where(
            DeviceToken.user_id == user_id
        )
    ).scalars().all()

    successful_deliveries = 0

    for device in device_tokens:
        try:
            send_push_notification(
                device_token=device.device_token,
                title=title,
                body=body,
                data=data
            )

            successful_deliveries += 1

        except Exception:
            logger.exception(
                "Push notification failed for device token ID %s",
                device.id
            )

    return successful_deliveries
