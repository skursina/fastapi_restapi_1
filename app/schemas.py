from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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