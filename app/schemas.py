from datetime import datetime, date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class UserGroup(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserCreate(BaseModel):
    username: str = Field(
        min_length=1,
        max_length=100,
    )

    password: str = Field(
        min_length=4,
    )

    group: UserGroup = UserGroup.USER


class UserUpdate(BaseModel):
    username: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    password: str | None = Field(
        default=None,
        min_length=4,
    )

    group: UserGroup | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    group: UserGroup

    model_config = ConfigDict(
        from_attributes=True,
    )


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str


class AdvertisementCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
    )

    description: str = Field(
        min_length=1,
    )

    price: int = Field(
        ge=0,
    )

    author: str = Field(
        min_length=1,
        max_length=255,
    )


class AdvertisementUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        min_length=1,
    )

    price: int | None = Field(
        default=None,
        ge=0,
    )

    author: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )


class AdvertisementResponse(BaseModel):
    id: int
    title: str
    description: str
    price: int
    author: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )