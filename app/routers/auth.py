
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.auth_schema import (
    LoginRequest,
    TokenResponse,
    CurrentUserResponse
)
from app.services.auth_service import authenticate_user
from app.utils.dependencies import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# Employee login
@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):

    return authenticate_user(
        db=db,
        login_data=login_data
    )


# Get logged-in employee details
@router.get(
    "/me",
    response_model=CurrentUserResponse
)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):

    return current_user
