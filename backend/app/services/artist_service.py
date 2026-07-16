from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.artist import Artist
from app.models.role import Role
from app.schemas.artist import ArtistCreate, ArtistUpdate, RoleCreate


def create_role(
    db: Session,
    role_data: RoleCreate,
) -> Role:
    role = Role(
        name=role_data.name.strip().lower(),
        description=(
            role_data.description.strip()
            if role_data.description
            else None
        ),
    )

    db.add(role)
    db.commit()
    db.refresh(role)

    return role


def get_roles(db: Session) -> list[Role]:
    statement = select(Role).order_by(Role.name)
    return list(db.scalars(statement).all())


def get_role_by_name(
    db: Session,
    name: str,
) -> Role | None:
    statement = select(Role).where(
        Role.name == name.strip().lower()
    )

    return db.scalar(statement)


def get_roles_by_ids(
    db: Session,
    role_ids: list[int],
) -> list[Role]:
    if not role_ids:
        return []

    statement = select(Role).where(Role.id.in_(role_ids))
    return list(db.scalars(statement).all())


def get_artist_by_name(
    db: Session,
    name: str,
) -> Artist | None:
    statement = select(Artist).where(
        Artist.name == name.strip()
    )

    return db.scalar(statement)


def get_artist_by_id(
    db: Session,
    artist_id: int,
) -> Artist | None:
    statement = (
        select(Artist)
        .options(selectinload(Artist.roles))
        .where(Artist.id == artist_id)
    )

    return db.scalar(statement)


def get_artists(
    db: Session,
    skip: int = 0,
    limit: int = 20,
) -> list[Artist]:
    statement = (
        select(Artist)
        .options(selectinload(Artist.roles))
        .order_by(Artist.name)
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def create_artist(
    db: Session,
    artist_data: ArtistCreate,
    roles: list[Role],
) -> Artist:
    artist = Artist(
        name=artist_data.name.strip(),
        stage_name=(
            artist_data.stage_name.strip()
            if artist_data.stage_name
            else None
        ),
        bio=artist_data.bio.strip() if artist_data.bio else None,
        country=(
            artist_data.country.strip()
            if artist_data.country
            else None
        ),
        image_url=(
            artist_data.image_url.strip()
            if artist_data.image_url
            else None
        ),
        verified=artist_data.verified,
        roles=roles,
    )

    db.add(artist)
    db.commit()

    return get_artist_by_id(db, artist.id)


def update_artist(
    db: Session,
    artist: Artist,
    artist_data: ArtistUpdate,
    roles: list[Role] | None = None,
) -> Artist:
    update_data = artist_data.model_dump(
        exclude_unset=True,
        exclude={"role_ids"},
    )

    for field, value in update_data.items():
        if isinstance(value, str):
            value = value.strip()

        setattr(artist, field, value)

    if artist_data.role_ids is not None:
        artist.roles = roles or []

    db.commit()

    return get_artist_by_id(db, artist.id)


def delete_artist(
    db: Session,
    artist: Artist,
) -> None:
    db.delete(artist)
    db.commit()