from app.routes.artist import router as artist_router
from app.routes.auth import router as auth_router

__all__ = [
    "artist_router",
    "auth_router",
]