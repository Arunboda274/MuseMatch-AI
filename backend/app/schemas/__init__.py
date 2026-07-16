from app.schemas.album import (
    AlbumArtistResponse,
    AlbumCreate,
    AlbumResponse,
    AlbumUpdate,
)
from app.schemas.artist import (
    ArtistCreate,
    ArtistResponse,
    ArtistUpdate,
    RoleCreate,
    RoleResponse,
)
from app.schemas.audio_analysis import AudioAnalysisResponse
from app.schemas.genre import (
    GenreCreate,
    GenreResponse,
    GenreUpdate,
)
from app.schemas.song import (
    SongAlbumResponse,
    SongArtistResponse,
    SongCreate,
    SongFeatureCreate,
    SongFeatureResponse,
    SongGenreResponse,
    SongResponse,
    SongUpdate,
)
from app.schemas.user import (
    LoginResponse,
    TokenResponse,
    UserCreate,
    UserResponse,
)


__all__ = [
    "AlbumArtistResponse",
    "AlbumCreate",
    "AlbumResponse",
    "AlbumUpdate",
    "ArtistCreate",
    "ArtistResponse",
    "ArtistUpdate",
    "AudioAnalysisResponse",
    "GenreCreate",
    "GenreResponse",
    "GenreUpdate",
    "LoginResponse",
    "RoleCreate",
    "RoleResponse",
    "SongAlbumResponse",
    "SongArtistResponse",
    "SongCreate",
    "SongFeatureCreate",
    "SongFeatureResponse",
    "SongGenreResponse",
    "SongResponse",
    "SongUpdate",
    "TokenResponse",
    "UserCreate",
    "UserResponse",
]