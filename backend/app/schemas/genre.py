from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GenreCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    image_url: str | None = Field(
        default=None,
        max_length=500,
    )


class GenreUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    image_url: str | None = Field(
        default=None,
        max_length=500,
    )


class GenreResponse(BaseModel):
    id: int
    name: str
    description: str | None
    image_url: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)