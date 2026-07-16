from datetime import date, datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum as SqlEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.song_artist import song_artists
from app.models.song_genre import song_genres

if TYPE_CHECKING:
    from app.models.album import Album
    from app.models.artist import Artist
    from app.models.genre import Genre
    from app.models.song_feature import SongFeature


class SongStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        index=True,
        nullable=False,
    )

    album_id: Mapped[int | None] = mapped_column(
        ForeignKey("albums.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    language: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    mood: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    release_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    duration_seconds: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    audio_file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    cover_image_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    lyrics: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    explicit: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    track_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    disc_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    popularity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    file_size_bytes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    mime_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    bitrate: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    status: Mapped[SongStatus] = mapped_column(
        SqlEnum(
            SongStatus,
            name="song_status",
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ],
        ),
        default=SongStatus.DRAFT,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    album: Mapped["Album | None"] = relationship()

    artists: Mapped[list["Artist"]] = relationship(
        secondary=song_artists,
    )

    genres: Mapped[list["Genre"]] = relationship(
        secondary=song_genres,
    )

    features: Mapped["SongFeature | None"] = relationship(
        back_populates="song",
        uselist=False,
        cascade="all, delete-orphan",
    )