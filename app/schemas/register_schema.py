
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints
)


class RegisterRequest(BaseModel):

    name: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=2,
            max_length=100
        )
    ]

    email: EmailStr

    password: Annotated[
        str,
        Field(min_length=8, max_length=128)
    ]

    department: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=2,
            max_length=100
        )
    ]


class RegisterResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: str
    department: str
