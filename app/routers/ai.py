
from fastapi import APIRouter, Depends

from app.schemas.ai_schema import (
    TaskAnalysisRequest,
    TaskAnalysisResponse
)
from app.services.ai_service import analyze_task
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/ai",
    tags=["AI Assistant"]
)


@router.post(
    "/analyze-task",
    response_model=TaskAnalysisResponse
)
async def analyze_task_endpoint(
    request: TaskAnalysisRequest,
    current_user=Depends(get_current_user)
):
    result = await analyze_task(
        title=request.title,
        description=request.description
    )

    return result
