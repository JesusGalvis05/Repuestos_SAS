from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator

Password = Annotated[SecretStr, Field(min_length=12, max_length=128)]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Login(Input):
    email: EmailStr
    password: SecretStr = Field(min_length=1, max_length=128)


class ChangePassword(Input):
    current_password: SecretStr = Field(min_length=1, max_length=128)
    new_password: Password


class UserCreate(Input):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    password: Password
    roles: list[str] = Field(min_length=1, max_length=4)

    @field_validator("full_name")
    @classmethod
    def nonblank_name(cls, value: str) -> str:
        if len(value.strip()) < 2:
            raise ValueError("Nombre inválido")
        return value.strip()


class UserUpdate(Input):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    active: bool | None = None
    roles: list[str] | None = Field(default=None, min_length=1, max_length=4)

    @field_validator("full_name")
    @classmethod
    def nonblank_name(cls, value: str | None) -> str | None:
        if value is not None and len(value.strip()) < 2:
            raise ValueError("Nombre inválido")
        return value.strip() if value is not None else None


class UserView(BaseModel):
    id: UUID
    email: str
    full_name: str
    active: bool
    roles: list[str]
    permissions: list[str]
    last_login_at: datetime | None


class TokenView(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserView


class UserPage(BaseModel):
    items: list[UserView]
    total: int
    page: int
    page_size: int


class SessionView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    expires_at: datetime
    user_agent: str
