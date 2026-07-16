from sqlalchemy import Column, ForeignKey, Table

from app.database import Base


artist_roles = Table(
    "artist_roles",
    Base.metadata,
    Column(
        "artist_id",
        ForeignKey("artists.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)