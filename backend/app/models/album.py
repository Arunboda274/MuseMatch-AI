from datetime import date, datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum as SqlEnum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.album_artist import album_artists

if TYPE_CHECKING:
    from app.models.artist import Artist


class AlbumType(str, Enum):
    ALBUM = "album"
    SINGLE = "single"
    EP = "ep"
    COMPILATION = "compilation"
    SOUNDTRACK = "soundtrack"


class Album(Base):
    __tablename__ = "albums"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        index=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    album_type: Mapped[AlbumType] = mapped_column(
        SqlEnum(
            AlbumType,
            name="album_type",
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ],
        ),
        default=AlbumType.ALBUM,
        nullable=False,
    )

    release_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    cover_image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    record_label: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    copyright_text: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
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

    artists: Mapped[list["Artist"]] = relationship(
        secondary=album_artists,
        back_populates="albums",
    )