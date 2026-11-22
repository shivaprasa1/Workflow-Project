
from app.models.device_token import DeviceToken
from app.services import firebase_service


def test_send_push_to_user_success(db_session, monkeypatch):
    device = DeviceToken(
        user_id=1,
        device_token="firebase_test_token_123456",
        platform="ANDROID",
    )

    db_session.add(device)
    db_session.commit()

    sent_notifications = []

    def mock_send_push_notification(
        device_token,
        title,
        body,
        data=None,
    ):
        sent_notifications.append({
            "device_token": device_token,
            "title": title,
            "body": body,
            "data": data,
        })
        return "mock-message-id"

    monkeypatch.setattr(
        firebase_service,
        "send_push_notification",
        mock_send_push_notification,
    )

    result = firebase_service.send_push_to_user(
        db=db_session,
        user_id=1,
        title="New Task Assigned",
        body="You have received a new task.",
        data={"task_id": 10},
    )

    assert result == 1
    assert len(sent_notifications) == 1
    assert sent_notifications[0]["device_token"] == (
        "firebase_test_token_123456"
    )
    assert sent_notifications[0]["title"] == "New Task Assigned"
    assert sent_notifications[0]["data"] == {"task_id": 10}


def test_send_push_to_user_without_devices(db_session, monkeypatch):
    def mock_send_push_notification(*args, **kwargs):
        raise AssertionError("Firebase should not be called")

    monkeypatch.setattr(
        firebase_service,
        "send_push_notification",
        mock_send_push_notification,
    )

    result = firebase_service.send_push_to_user(
        db=db_session,
        user_id=999,
        title="Test",
        body="Test notification",
    )

    assert result == 0


def test_push_failure_does_not_interrupt_workflow(
    db_session,
    monkeypatch,
):
    device = DeviceToken(
        user_id=1,
        device_token="firebase_failure_token_123456",
        platform="ANDROID",
    )

    db_session.add(device)
    db_session.commit()

    def mock_send_push_notification(*args, **kwargs):
        raise RuntimeError("Simulated Firebase failure")

    monkeypatch.setattr(
        firebase_service,
        "send_push_notification",
        mock_send_push_notification,
    )

    result = firebase_service.send_push_to_user(
        db=db_session,
        user_id=1,
        title="Task Update",
        body="Your task was updated.",
    )

    # Push failure must not crash the application workflow.
    assert result == 0

    # The device token must remain in the database.
    saved_device = db_session.query(DeviceToken).filter_by(
        device_token="firebase_failure_token_123456"
    ).first()

    assert saved_device is not None
