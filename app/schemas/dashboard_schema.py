
from pydantic import BaseModel


class TaskStatistics(BaseModel):
    total_tasks: int
    assigned_tasks: int
    in_progress_tasks: int
    submitted_tasks: int
    approved_tasks: int
    rejected_tasks: int
    overdue_tasks: int


class EmployeeWorkload(BaseModel):
    employee_id: int
    employee_name: str
    department: str
    total_tasks: int
    in_progress_tasks: int
    completed_tasks: int


class DashboardResponse(BaseModel):
    role: str
    statistics: TaskStatistics
    employee_workload: list[EmployeeWorkload]
