
from sqlalchemy import Column, Integer, String, Boolean

from app.database.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(50),
        nullable=False,
        default="EMPLOYEE"
    )

    department = Column(
        String(100),
        nullable=False
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )
