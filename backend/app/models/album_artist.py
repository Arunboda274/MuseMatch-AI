from sqlalchemy import Column, ForeignKey, Table

from app.database import Base


album_artists = Table(
    "album_artists",
    Base.metadata,
    Column(
        "album_id",
        ForeignKey("albums.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "artist_id",
        ForeignKey("artists.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)