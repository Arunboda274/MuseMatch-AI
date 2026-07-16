from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.genre import (
    GenreCreate,
    GenreResponse,
    GenreUpdate,
)
from app.services.genre_service import (
    create_genre,
    delete_genre,
    get_genre_by_id,
    get_genre_by_name,
    get_genres,
    update_genre,
)
from app.utils.dependencies import get_current_admin


router = APIRouter(
    prefix="/api/v1/genres",
    tags=["Genres"],
)


@router.post(
    "",
    response_model=GenreResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_genre(
    genre_data: GenreCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
) -> GenreResponse:
    del current_admin

    existing_genre = get_genre_by_name(
        db=db,
        name=genre_data.name,
    )

    if existing_genre:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This genre already exists.",
        )

    try:
        return create_genre(
            db=db,
            genre_data=genre_data,
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Genre could not be created.",
        )


@router.get(
    "",
    response_model=list[GenreResponse],
)
def list_genres(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
) -> list[GenreResponse]:
    return get_genres(
        db=db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{genre_id}",
    response_model=GenreResponse,
)
def get_genre(
    genre_id: int,
    db: Session = Depends(get_db),
) -> GenreResponse:
    genre = get_genre_by_id(
        db=db,
        genre_id=genre_id,
    )

    if genre is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found.",
        )

    return genre


@router.put(
    "/{genre_id}",
    response_model=GenreResponse,
)
def edit_genre(
    genre_id: int,
    genre_data: GenreUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
) -> GenreResponse:
    del current_admin

    genre = get_genre_by_id(
        db=db,
        genre_id=genre_id,
    )

    if genre is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found.",
        )

    if genre_data.name is not None:
        existing_genre = get_genre_by_name(
            db=db,
            name=genre_data.name,
        )

        if (
            existing_genre is not None
            and existing_genre.id != genre.id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This genre name is already in use.",
            )

    return update_genre(
        db=db,
        genre=genre,
        genre_data=genre_data,
    )


@router.delete(
    "/{genre_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_genre(
    genre_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
) -> None:
    del current_admin

    genre = get_genre_by_id(
        db=db,
        genre_id=genre_id,
    )

    if genre is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found.",
        )

    delete_genre(
        db=db,
        genre=genre,
    )