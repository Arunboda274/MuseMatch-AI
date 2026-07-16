from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.song import SongStatus


class SongArtistResponse(BaseModel):
    id: int
    name: str
    stage_name: str | None
    image_url: str | None
    verified: bool

    model_config = ConfigDict(from_attributes=True)


class SongGenreResponse(BaseModel):
    id: int
    name: str
    description: str | None
    image_url: str | None

    model_config = ConfigDict(from_attributes=True)


class SongAlbumResponse(BaseModel):
    id: int
    title: str
    cover_image_url: str | None

    model_config = ConfigDict(from_attributes=True)


class SongFeatureCreate(BaseModel):
    tempo: float = Field(default=0, ge=0)
    energy: float = Field(default=0, ge=0, le=1)
    danceability: float = Field(default=0, ge=0, le=1)
    acousticness: float = Field(default=0, ge=0, le=1)
    instrumentalness: float = Field(default=0, ge=0, le=1)
    liveness: float = Field(default=0, ge=0, le=1)
    speechiness: float = Field(default=0, ge=0, le=1)
    valence: float = Field(default=0, ge=0, le=1)
    loudness: float = 0
    sample_rate: float = Field(default=44100, gt=0)


class SongFeatureResponse(BaseModel):
    id: int
    song_id: int
    tempo: float
    energy: float
    danceability: float
    acousticness: float
    instrumentalness: float
    liveness: float
    speechiness: float
    valence: float
    loudness: float
    sample_rate: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SongCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)

    temporary_file_path: str = Field(
        min_length=1,
        max_length=500,
    )

    cover_image_path: str | None = Field(
        default=None,
        max_length=500,
    )

    album_id: int | None = Field(
        default=None,
        gt=0,
    )

    artist_ids: list[int] = Field(
        min_length=1,
    )

    genre_ids: list[int] = Field(
        min_length=1,
    )

    language: str | None = Field(
        default=None,
        max_length=100,
    )

    mood: str | None = Field(
        default=None,
        max_length=100,
    )

    release_date: date | None = None

    duration_seconds: float = Field(
        gt=0,
    )

    lyrics: str | None = Field(
        default=None,
        max_length=50000,
    )

    explicit: bool = False

    track_number: int | None = Field(
        default=None,
        ge=1,
    )

    disc_number: int | None = Field(
        default=None,
        ge=1,
    )

    popularity: int = Field(
        default=0,
        ge=0,
        le=100,
    )

    mime_type: str | None = Field(
        default=None,
        max_length=100,
    )

    file_size_bytes: int | None = Field(
        default=None,
        ge=0,
    )

    bitrate: int | None = Field(
        default=None,
        ge=0,
    )

    status: SongStatus = SongStatus.DRAFT

    features: SongFeatureCreate


class SongUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    album_id: int | None = Field(
        default=None,
        gt=0,
    )

    artist_ids: list[int] | None = None
    genre_ids: list[int] | None = None

    language: str | None = Field(
        default=None,
        max_length=100,
    )

    mood: str | None = Field(
        default=None,
        max_length=100,
    )

    release_date: date | None = None

    lyrics: str | None = Field(
        default=None,
        max_length=50000,
    )

    explicit: bool | None = None

    track_number: int | None = Field(
        default=None,
        ge=1,
    )

    disc_number: int | None = Field(
        default=None,
        ge=1,
    )

    popularity: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    status: SongStatus | None = None

    features: SongFeatureCreate | None = None


class SongResponse(BaseModel):
    id: int
    title: str
    album_id: int | None
    language: str | None
    mood: str | None
    release_date: date | None
    duration_seconds: float
    audio_file_path: str
    cover_image_path: str | None
    lyrics: str | None
    explicit: bool
    track_number: int | None
    disc_number: int | None
    popularity: int
    file_size_bytes: int | None
    mime_type: str | None
    bitrate: int | None
    status: SongStatus
    created_at: datetime
    updated_at: datetime

    album: SongAlbumResponse | None
    artists: list[SongArtistResponse]
    genres: list[SongGenreResponse]
    features: SongFeatureResponse | None

    model_config = ConfigDict(from_attributes=True)