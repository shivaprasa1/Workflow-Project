
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class DeviceTokenRequest(BaseModel):
    device_token: str = Field(
        min_length=20,
        max_length=500
    )

    platform: Literal["ANDROID", "WEB"]


class DeviceTokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    device_token: str
    platform: str
