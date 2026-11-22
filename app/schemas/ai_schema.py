
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class TaskAnalysisRequest(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=200,
        description="Title of the task"
    )

    description: str = Field(
        min_length=5,
        max_length=5000,
        description="Detailed task description"
    )


class TaskAnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: str = Field(min_length=1, max_length=100)

    suggested_priority: Literal[
        "LOW",
        "MEDIUM",
        "HIGH",
        "URGENT"
    ]

    summary: str = Field(min_length=1, max_length=500)

    reasoning: str = Field(min_length=1, max_length=500)
