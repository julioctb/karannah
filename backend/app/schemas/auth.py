from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

RoleName = Literal["admin", "encargado", "vendedor"]


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=1)


class BranchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    active: bool


class MeResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: RoleName
    branches: list[BranchRead]


class BranchesResponse(BaseModel):
    branches: list[BranchRead]


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: MeResponse
