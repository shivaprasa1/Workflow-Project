
from datetime import datetime, timezone

from sqlalchemy import select, func, case
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.user import User


def get_dashboard_data(
    db: Session,
    current_user: User
):

    # Store and compare task deadlines using UTC.
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)

    # Apply role-specific task visibility.
    task_filter = []

    if current_user.role == "MANAGER":
        task_filter.append(
            Task.created_by == current_user.id
        )

    elif current_user.role == "EMPLOYEE":
        task_filter.append(
            Task.assigned_to == current_user.id
        )

    # Calculate task statistics.
    statistics_query = select(
        func.count(Task.id).label("total_tasks"),

        func.coalesce(
            func.sum(
                case((Task.status == "ASSIGNED", 1), else_=0)
            ), 0
        ).label("assigned_tasks"),

        func.coalesce(
            func.sum(
                case((Task.status == "IN_PROGRESS", 1), else_=0)
            ), 0
        ).label("in_progress_tasks"),

        func.coalesce(
            func.sum(
                case((Task.status == "SUBMITTED", 1), else_=0)
            ), 0
        ).label("submitted_tasks"),

        func.coalesce(
            func.sum(
                case((Task.status == "APPROVED", 1), else_=0)
            ), 0
        ).label("approved_tasks"),

        func.coalesce(
            func.sum(
                case((Task.status == "REJECTED", 1), else_=0)
            ), 0
        ).label("rejected_tasks"),

        func.coalesce(
            func.sum(
                case(
                    (
                        (Task.due_date < now_utc)
                        & (Task.status != "APPROVED"),
                        1
                    ),
                    else_=0
                )
            ), 0
        ).label("overdue_tasks")
    ).where(*task_filter)

    stats = db.execute(statistics_query).one()

    # Employee workload is useful for Admin and Manager.
    workload = []

    if current_user.role in ["ADMIN", "MANAGER"]:

        workload_query = (
            select(
                User.id.label("employee_id"),
                User.name.label("employee_name"),
                User.department.label("department"),

                func.count(Task.id).label("total_tasks"),

                func.coalesce(
                    func.sum(
                        case(
                            (Task.status == "IN_PROGRESS", 1),
                            else_=0
                        )
                    ), 0
                ).label("in_progress_tasks"),

                func.coalesce(
                    func.sum(
                        case(
                            (Task.status == "APPROVED", 1),
                            else_=0
                        )
                    ), 0
                ).label("completed_tasks")
            )
            .join(Task, Task.assigned_to == User.id)
            .where(User.role == "EMPLOYEE")
        )

        # Managers only see tasks they created.
        if current_user.role == "MANAGER":

            workload_query = workload_query.where(
                Task.created_by == current_user.id
            )

        workload_query = (
            workload_query
            .group_by(
                User.id,
                User.name,
                User.department
            )
            .order_by(User.name)
        )

        workload = db.execute(
            workload_query
        ).all()

    return {
        "role": current_user.role,

        "statistics": {
            "total_tasks": stats.total_tasks,
            "assigned_tasks": stats.assigned_tasks,
            "in_progress_tasks": stats.in_progress_tasks,
            "submitted_tasks": stats.submitted_tasks,
            "approved_tasks": stats.approved_tasks,
            "rejected_tasks": stats.rejected_tasks,
            "overdue_tasks": stats.overdue_tasks
        },

        "employee_workload": [
            {
                "employee_id": item.employee_id,
                "employee_name": item.employee_name,
                "department": item.department,
                "total_tasks": item.total_tasks,
                "in_progress_tasks": item.in_progress_tasks,
                "completed_tasks": item.completed_tasks
            }
            for item in workload
        ]
    }
