from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.genre import Genre
from app.schemas.genre import GenreCreate, GenreUpdate


def get_genre_by_id(
    db: Session,
    genre_id: int,
) -> Genre | None:
    statement = select(Genre).where(
        Genre.id == genre_id
    )

    return db.scalar(statement)


def get_genre_by_name(
    db: Session,
    name: str,
) -> Genre | None:
    normalized_name = name.strip().lower()

    statement = select(Genre).where(
        func.lower(Genre.name) == normalized_name
    )

    return db.scalar(statement)


def get_genres(
    db: Session,
    skip: int = 0,
    limit: int = 50,
) -> list[Genre]:
    statement = (
        select(Genre)
        .order_by(Genre.name)
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def create_genre(
    db: Session,
    genre_data: GenreCreate,
) -> Genre:
    genre = Genre(
        name=genre_data.name.strip(),
        description=(
            genre_data.description.strip()
            if genre_data.description
            else None
        ),
        image_url=(
            genre_data.image_url.strip()
            if genre_data.image_url
            else None
        ),
    )

    db.add(genre)
    db.commit()
    db.refresh(genre)

    return genre


def update_genre(
    db: Session,
    genre: Genre,
    genre_data: GenreUpdate,
) -> Genre:
    update_data = genre_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        if isinstance(value, str):
            value = value.strip()

        setattr(genre, field, value)

    db.commit()
    db.refresh(genre)

    return genre


def delete_genre(
    db: Session,
    genre: Genre,
) -> None:
    db.delete(genre)
    db.commit()