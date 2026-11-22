
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.device_token_schema import (
    DeviceTokenRequest,
    DeviceTokenResponse
)
from app.services.device_token_service import (
    register_device_token,
    remove_device_token
)
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/device-tokens",
    tags=["Device Tokens"]
)


@router.post(
    "/",
    response_model=DeviceTokenResponse,
    status_code=status.HTTP_201_CREATED
)
def register_device(
    request: DeviceTokenRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return register_device_token(
        db=db,
        user_id=current_user.id,
        device_token=request.device_token,
        platform=request.platform
    )


@router.delete(
    "/",
    status_code=status.HTTP_200_OK
)
def unregister_device(
    device_token: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    removed = remove_device_token(
        db=db,
        user_id=current_user.id,
        device_token=device_token
    )

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device token not found."
        )

    return {
        "message": "Device token removed successfully."
    }
