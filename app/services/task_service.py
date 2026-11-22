
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.user import User
from app.schemas.task_schema import TaskCreateRequest
from datetime import timezone
from app.services.notification_service import create_notification
from app.services.firebase_service import send_push_to_user


def create_task(
    db: Session,
    task_data: TaskCreateRequest,
    current_user: User
):
    # Find the employee receiving the task
    employee = db.execute(
        select(User).where(
            User.id == task_data.assigned_to
        )
    ).scalar_one_or_none()

    if employee is None or not employee.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active assigned employee not found."
        )

    if employee.role != "EMPLOYEE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tasks can only be assigned to employees."
        )

    # Validate deadline
    if task_data.due_date.tzinfo is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide due_date with a timezone."
        )

    # Create task
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        status="ASSIGNED",
        due_date=task_data.due_date.astimezone(
            timezone.utc
        ).replace(tzinfo=None),
        assigned_to=employee.id,
        created_by=current_user.id
    )

    db.add(new_task)
    db.flush()

    message = f"You have been assigned a new task: {new_task.title}"

    # Create in-app notification
    create_notification(
        db=db,
        recipient_id=employee.id,
        actor_id=current_user.id,
        task_id=new_task.id,
        notification_type="TASK_ASSIGNED",
        message=message
    )

    # Save task and notification first
    db.commit()
    db.refresh(new_task)

    # Send Firebase push notification after successful commit
    send_push_to_user(
        db=db,
        user_id=employee.id,
        title="New Task Assigned",
        body=message,
        data={
            "task_id": new_task.id,
            "notification_type": "TASK_ASSIGNED"
        }
    )

    return new_task




def get_tasks(
    db: Session,
    current_user: User,
    skip: int = 0,
    limit: int = 20
):
    query = select(Task).order_by(Task.id.desc())

    # Admin can view all tasks
    if current_user.role == "ADMIN":
        pass

    # Manager can view tasks created by them
    elif current_user.role == "MANAGER":
        query = query.where(
            Task.created_by == current_user.id
        )

    # Employee can view only assigned tasks
    else:
        query = query.where(
            Task.assigned_to == current_user.id
        )

    return db.execute(
        query.offset(skip).limit(limit)
    ).scalars().all()



def get_task_by_id(
    db: Session,
    task_id: int,
    current_user: User
):

    task = db.execute(
        select(Task).where(Task.id == task_id)
    ).scalar_one_or_none()

    if task is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
        )

    # Check task access
    if current_user.role == "ADMIN":
        return task

    if current_user.role == "MANAGER":

        if task.created_by == current_user.id:
            return task

    elif task.assigned_to == current_user.id:

        return task

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have access to this task."
    )



def update_task_status(
    db: Session,
    task_id: int,
    new_status: str,
    current_user: User
):
    task = get_task_by_id(
        db=db,
        task_id=task_id,
        current_user=current_user
    )

    # Employee workflow
    if current_user.role == "EMPLOYEE":

        if new_status in ["APPROVED", "REJECTED"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Employees cannot approve or reject tasks."
            )

        allowed_transitions = {
            "ASSIGNED": ["IN_PROGRESS"],
            "IN_PROGRESS": ["SUBMITTED"],
            "REJECTED": ["IN_PROGRESS"]
        }

        allowed = allowed_transitions.get(task.status, [])

        if new_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid task status transition."
            )

    # Admin and Manager approval workflow
    elif current_user.role in ["ADMIN", "MANAGER"]:

        if new_status not in ["APPROVED", "REJECTED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Managers and Admins can approve or reject submitted tasks."
            )

        if task.status != "SUBMITTED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only submitted tasks can be reviewed."
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update task status."
        )

    task.status = new_status

    # Prepare notification details
    recipient_id = None
    notification_title = None
    notification_message = None

    if new_status == "SUBMITTED":
        recipient_id = task.created_by
        notification_title = "Task Submitted"
        notification_message = (
            f"Task submitted for review: {task.title}"
        )

    elif new_status == "APPROVED":
        recipient_id = task.assigned_to
        notification_title = "Task Approved"
        notification_message = (
            f"Your task has been approved: {task.title}"
        )

    elif new_status == "REJECTED":
        recipient_id = task.assigned_to
        notification_title = "Task Rejected"
        notification_message = (
            f"Your task has been rejected: {task.title}"
        )

    # Create in-app notification
    if recipient_id is not None:
        create_notification(
            db=db,
            recipient_id=recipient_id,
            actor_id=current_user.id,
            task_id=task.id,
            notification_type=f"TASK_{new_status}",
            message=notification_message
        )

    # Save task status and notification first
    db.commit()
    db.refresh(task)

    # Send push notification after successful commit
    if recipient_id is not None:
        send_push_to_user(
            db=db,
            user_id=recipient_id,
            title=notification_title,
            body=notification_message,
            data={
                "task_id": task.id,
                "notification_type": f"TASK_{new_status}"
            }
        )

    return task
