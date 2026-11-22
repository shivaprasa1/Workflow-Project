
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user_schema import (
    UserResponse,
    UpdateUserRoleRequest,
    UpdateUserStatusRequest
)
from app.services.user_management_service import (
    get_all_users,
    get_user_by_id,
    update_user_role,
    update_user_status
)
from app.utils.dependencies import require_roles


router = APIRouter(
    prefix="/users",
    tags=["User Management"]
)


# List all users - Admin only
@router.get("/", response_model=list[UserResponse])
def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN"))
):
    return get_all_users(
        db=db,
        skip=skip,
        limit=limit
    )


# Get user by ID - Admin only
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN"))
):
    return get_user_by_id(
        db=db,
        user_id=user_id
    )


# Update user role - Admin only
@router.patch("/{user_id}/role", response_model=UserResponse)
def change_user_role(
    user_id: int,
    role_data: UpdateUserRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN"))
):
    return update_user_role(
        db=db,
        user_id=user_id,
        new_role=role_data.role,
        current_user_id=current_user.id
    )


# Activate or deactivate user - Admin only
@router.patch("/{user_id}/status", response_model=UserResponse)
def change_user_status(
    user_id: int,
    status_data: UpdateUserStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN"))
):
    return update_user_status(
        db=db,
        user_id=user_id,
        is_active=status_data.is_active,
        current_user_id=current_user.id
    )
