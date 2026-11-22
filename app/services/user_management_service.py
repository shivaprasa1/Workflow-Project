
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user_schema import UserRole


def get_all_users(
    db: Session,
    skip: int = 0,
    limit: int = 20
):

    return db.execute(
        select(User)
        .order_by(User.id)
        .offset(skip)
        .limit(limit)
    ).scalars().all()


def get_user_by_id(
    db: Session,
    user_id: int
):

    user = db.execute(
        select(User).where(User.id == user_id)
    ).scalar_one_or_none()

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    return user


def count_active_admins(db: Session) -> int:

    return db.scalar(
        select(func.count())
        .select_from(User)
        .where(
            User.role == "ADMIN",
            User.is_active.is_(True)
        )
    )


def update_user_role(
    db: Session,
    user_id: int,
    new_role: UserRole,
    current_user_id: int
):

    user = get_user_by_id(db, user_id)

    if user.id == current_user_id and new_role != "ADMIN":

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove your own Admin role."
        )

    if (
        user.role == "ADMIN"
        and user.is_active
        and new_role != "ADMIN"
        and count_active_admins(db) <= 1
    ):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The last active Admin cannot be demoted."
        )

    user.role = new_role

    db.commit()
    db.refresh(user)

    return user


def update_user_status(
    db: Session,
    user_id: int,
    is_active: bool,
    current_user_id: int
):

    user = get_user_by_id(db, user_id)

    if user.id == current_user_id and not is_active:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account."
        )

    if (
        user.role == "ADMIN"
        and user.is_active
        and not is_active
        and count_active_admins(db) <= 1
    ):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The last active Admin cannot be deactivated."
        )

    user.is_active = is_active

    db.commit()
    db.refresh(user)

    return user
