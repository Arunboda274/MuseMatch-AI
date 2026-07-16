from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.album import AlbumType


class AlbumArtistResponse(BaseModel):
    id: int
    name: str
    stage_name: str | None
    image_url: str | None
    verified: bool

    model_config = ConfigDict(from_attributes=True)


class AlbumCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    album_type: AlbumType = AlbumType.ALBUM
    release_date: date | None = None
    cover_image_url: str | None = Field(default=None, max_length=500)
    record_label: str | None = Field(default=None, max_length=200)
    copyright_text: str | None = Field(default=None, max_length=500)
    artist_ids: list[int] = Field(min_length=1)


class AlbumUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    description: str | None = Field(default=None, max_length=5000)
    album_type: AlbumType | None = None
    release_date: date | None = None
    cover_image_url: str | None = Field(default=None, max_length=500)
    record_label: str | None = Field(default=None, max_length=200)
    copyright_text: str | None = Field(default=None, max_length=500)
    artist_ids: list[int] | None = None


class AlbumResponse(BaseModel):
    id: int
    title: str
    description: str | None
    album_type: AlbumType
    release_date: date | None
    cover_image_url: str | None
    record_label: str | None
    copyright_text: str | None
    created_at: datetime
    updated_at: datetime
    artists: list[AlbumArtistResponse]

    model_config = ConfigDict(from_attributes=True)