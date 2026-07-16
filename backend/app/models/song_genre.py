from sqlalchemy import Column, ForeignKey, Table

from app.database import Base


song_genres = Table(
    "song_genres",
    Base.metadata,
    Column(
        "song_id",
        ForeignKey("songs.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "genre_id",
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)