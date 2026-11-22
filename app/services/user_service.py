
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.register_schema import RegisterRequest
from app.utils.security import hash_password


def create_employee(
    db: Session,
    employee_data: RegisterRequest
):

    email = str(employee_data.email).strip().lower()

    # Check whether email already exists
    existing_employee = db.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()

    if existing_employee:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists."
        )

    # Create new employee
    new_employee = User(

        name=employee_data.name,

        email=email,

        password_hash=hash_password(
            employee_data.password
        ),

        department=employee_data.department,

        role="EMPLOYEE",

        is_active=True
    )

    try:

        db.add(new_employee)

        db.commit()

        db.refresh(new_employee)

        return new_employee

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists."
        )
