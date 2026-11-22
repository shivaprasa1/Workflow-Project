
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TaskPriority = Literal[
    "LOW",
    "MEDIUM",
    "HIGH",
    "URGENT"
]

TaskStatus = Literal[
    "ASSIGNED",
    "IN_PROGRESS",
    "SUBMITTED",
    "APPROVED",
    "REJECTED"
]


class TaskCreateRequest(BaseModel):

    title: str = Field(
        min_length=3,
        max_length=200
    )

    description: str | None = None

    priority: TaskPriority = "MEDIUM"

    due_date: datetime

    assigned_to: int = Field(gt=0)


class TaskStatusUpdateRequest(BaseModel):

    status: Literal[
        "IN_PROGRESS",
        "SUBMITTED",
        "APPROVED",
        "REJECTED"
    ]


class TaskResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    priority: TaskPriority
    status: TaskStatus
    due_date: datetime
    assigned_to: int
    created_by: int
