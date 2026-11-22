
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey
)
from sqlalchemy.sql import func

from app.database.database import Base


class Notification(Base):

    __tablename__ = "notifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    recipient_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    actor_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    task_id = Column(
        Integer,
        ForeignKey("tasks.id"),
        nullable=True
    )

    notification_type = Column(
        String(50),
        nullable=False
    )

    message = Column(
        Text,
        nullable=False
    )

    is_read = Column(
        Boolean,
        nullable=False,
        default=False
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )
