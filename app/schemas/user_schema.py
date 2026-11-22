
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr


UserRole = Literal["ADMIN", "MANAGER", "EMPLOYEE"]


class UserResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: UserRole
    department: str
    is_active: bool


class UpdateUserRoleRequest(BaseModel):

    role: UserRole


class UpdateUserStatusRequest(BaseModel):

    is_active: bool
