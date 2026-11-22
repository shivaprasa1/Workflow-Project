
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth_schema import LoginRequest
from app.utils.security import (
    verify_password,
    create_access_token
)


def authenticate_user(
    db: Session,
    login_data: LoginRequest
):

    email = str(login_data.email).strip().lower()

    # Find employee using email
    employee = db.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()

    # Reject invalid email or password
    if employee is None or not verify_password(
    login_data.password,
    employee.password_hash
):
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password."
    )

    if not employee.is_active:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password."
    )


    # Reject inactive accounts
    if not employee.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is inactive."
        )

    # Generate JWT token
    access_token = create_access_token(employee.email)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
