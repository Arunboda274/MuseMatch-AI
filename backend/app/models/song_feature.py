from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.song import Song


class SongFeature(Base):
    __tablename__ = "song_features"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    song_id: Mapped[int] = mapped_column(
        ForeignKey("songs.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    tempo: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    energy: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    danceability: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    acousticness: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    instrumentalness: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    liveness: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    speechiness: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    valence: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    loudness: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    sample_rate: Mapped[float] = mapped_column(
        Float,
        default=0.0,
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

    song: Mapped["Song"] = relationship(
        back_populates="features",
    )