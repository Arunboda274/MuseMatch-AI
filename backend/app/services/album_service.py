from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.album import Album
from app.models.artist import Artist
from app.schemas.album import AlbumCreate, AlbumUpdate


def get_artists_by_ids(
    db: Session,
    artist_ids: list[int],
) -> list[Artist]:
    if not artist_ids:
        return []

    statement = select(Artist).where(
        Artist.id.in_(artist_ids)
    )

    return list(db.scalars(statement).all())


def get_album_by_id(
    db: Session,
    album_id: int,
) -> Album | None:
    statement = (
        select(Album)
        .options(selectinload(Album.artists))
        .where(Album.id == album_id)
    )

    return db.scalar(statement)


def get_album_by_title(
    db: Session,
    title: str,
) -> Album | None:
    normalized_title = title.strip().lower()

    statement = (
        select(Album)
        .options(selectinload(Album.artists))
        .where(func.lower(Album.title) == normalized_title)
    )

    return db.scalar(statement)


def get_albums(
    db: Session,
    skip: int = 0,
    limit: int = 20,
) -> list[Album]:
    statement = (
        select(Album)
        .options(selectinload(Album.artists))
        .order_by(Album.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def create_album(
    db: Session,
    album_data: AlbumCreate,
    artists: list[Artist],
) -> Album:
    album = Album(
        title=album_data.title.strip(),
        description=(
            album_data.description.strip()
            if album_data.description
            else None
        ),
        album_type=album_data.album_type,
        release_date=album_data.release_date,
        cover_image_url=(
            album_data.cover_image_url.strip()
            if album_data.cover_image_url
            else None
        ),
        record_label=(
            album_data.record_label.strip()
            if album_data.record_label
            else None
        ),
        copyright_text=(
            album_data.copyright_text.strip()
            if album_data.copyright_text
            else None
        ),
        artists=artists,
    )

    db.add(album)
    db.commit()
    db.refresh(album)

    return get_album_by_id(db, album.id)


def update_album(
    db: Session,
    album: Album,
    album_data: AlbumUpdate,
    artists: list[Artist] | None = None,
) -> Album:
    update_data = album_data.model_dump(
        exclude_unset=True,
        exclude={"artist_ids"},
    )

    for field, value in update_data.items():
        if isinstance(value, str):
            value = value.strip()

        setattr(album, field, value)

    if album_data.artist_ids is not None:
        album.artists = artists or []

    db.commit()

    return get_album_by_id(db, album.id)


def delete_album(
    db: Session,
    album: Album,
) -> None:
    db.delete(album)
    db.commit()