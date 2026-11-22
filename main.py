
from fastapi import FastAPI

from app.models.user import User
from app.models.task import Task
from app.models.notification import Notification

from app.routers import ai

from app.models.device_token import DeviceToken

from app.routers import device_tokens


from app.routers import (
    register,
    auth,
    users,
    tasks,
    dashboard,
    notifications
)


app = FastAPI(
    title="Smart Workflow Management System",
    description="Backend API for employee and workflow management",
    version="1.0.0"
)


# Register API routers
app.include_router(register.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(dashboard.router)
app.include_router(notifications.router)
app.include_router(ai.router)
app.include_router(device_tokens.router)


@app.get("/")
def home():
    return {
        "project": "Smart Workflow Management System",
        "version": "1.0.0",
        "status": "Running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
