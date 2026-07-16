from sqlalchemy import Column, ForeignKey, Table

from app.database import Base


song_artists = Table(
    "song_artists",
    Base.metadata,
    Column(
        "song_id",
        ForeignKey("songs.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "artist_id",
        ForeignKey("artists.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)