
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.task_schema import (
    TaskCreateRequest,
    TaskStatusUpdateRequest,
    TaskResponse
)
from app.services.task_service import (
    create_task,
    get_tasks,
    get_task_by_id,
    update_task_status
)
from app.utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/tasks",
    tags=["Task Management"]
)


# Create a task - Admin and Manager
@router.post(
    "/",
    response_model=TaskResponse,
    status_code=201
)
def create_new_task(
    task_data: TaskCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    )
):
    return create_task(
        db=db,
        task_data=task_data,
        current_user=current_user
    )


# List tasks accessible to the logged-in user
@router.get(
    "/",
    response_model=list[TaskResponse]
)
def list_tasks(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_tasks(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit
    )


# Get one task
@router.get(
    "/{task_id}",
    response_model=TaskResponse
)
def get_single_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_task_by_id(
        db=db,
        task_id=task_id,
        current_user=current_user
    )


# Update task status
@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse
)
def change_task_status(
    task_id: int,
    status_data: TaskStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_task_status(
        db=db,
        task_id=task_id,
        new_status=status_data.status,
        current_user=current_user
    )
