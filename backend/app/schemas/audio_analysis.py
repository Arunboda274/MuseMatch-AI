from pydantic import BaseModel, Field


class AudioAnalysisResponse(BaseModel):
    original_filename: str
    temporary_file_path: str
    mime_type: str | None
    file_size_bytes: int

    title: str | None
    artist: str | None
    album: str | None
    genre: str | None
    year: str | None
    track_number: str | None
    cover_image_path: str | None

    duration_seconds: float = Field(ge=0)
    tempo: float = Field(ge=0)
    energy: float = Field(ge=0, le=1)
    danceability: float = Field(ge=0, le=1)
    acousticness: float = Field(ge=0, le=1)
    instrumentalness: float = Field(ge=0, le=1)
    liveness: float = Field(ge=0, le=1)
    speechiness: float = Field(ge=0, le=1)
    valence: float = Field(ge=0, le=1)
    loudness: float
    sample_rate: float = Field(gt=0)