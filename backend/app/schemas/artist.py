from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: str | None = Field(default=None, max_length=500)


class RoleResponse(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ArtistCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    stage_name: str | None = Field(default=None, max_length=150)
    bio: str | None = Field(default=None, max_length=5000)
    country: str | None = Field(default=None, max_length=100)
    image_url: str | None = Field(default=None, max_length=500)
    verified: bool = False
    role_ids: list[int] = Field(default_factory=list)


class ArtistUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    stage_name: str | None = Field(default=None, max_length=150)
    bio: str | None = Field(default=None, max_length=5000)
    country: str | None = Field(default=None, max_length=100)
    image_url: str | None = Field(default=None, max_length=500)
    verified: bool | None = None
    role_ids: list[int] | None = None


class ArtistResponse(BaseModel):
    id: int
    name: str
    stage_name: str | None
    bio: str | None
    country: str | None
    image_url: str | None
    verified: bool
    created_at: datetime
    updated_at: datetime
    roles: list[RoleResponse]

    model_config = ConfigDict(from_attributes=True)