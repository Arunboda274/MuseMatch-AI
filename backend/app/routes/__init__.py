from app.routes.album import router as album_router
from app.routes.artist import router as artist_router
from app.routes.auth import router as auth_router
from app.routes.genre import router as genre_router
from app.routes.song import router as song_router

__all__ = [
    "album_router",
    "artist_router",
    "auth_router",
    "song_router",
    "genre_router",
]