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
from app.schemas.genre import (
    GenreCreate,
    GenreResponse,
    GenreUpdate,
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
    "GenreCreate",
    "GenreResponse",
    "GenreUpdate",
    "RoleCreate",
    "RoleResponse",
    "LoginResponse",
    "TokenResponse",
    "UserCreate",
    "UserResponse",
]