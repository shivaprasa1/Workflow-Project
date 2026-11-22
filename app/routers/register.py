
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.register_schema import (
    RegisterRequest,
    RegisterResponse
)
from app.services.user_service import create_employee


router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


@router.post(
    "/",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED
)
def register_employee(
    employee: RegisterRequest,
    db: Session = Depends(get_db)
):

    return create_employee(
        db=db,
        employee_data=employee
    )
