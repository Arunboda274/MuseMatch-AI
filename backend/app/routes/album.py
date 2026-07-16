from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.album import (
    AlbumCreate,
    AlbumResponse,
    AlbumUpdate,
)
from app.services.album_service import (
    create_album,
    delete_album,
    get_album_by_id,
    get_album_by_title,
    get_albums,
    get_artists_by_ids,
    update_album,
)
from app.utils.dependencies import get_current_admin


router = APIRouter(
    prefix="/api/v1/albums",
    tags=["Albums"],
)


@router.post(
    "",
    response_model=AlbumResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_album(
    album_data: AlbumCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
) -> AlbumResponse:
    del current_admin

    existing_album = get_album_by_title(
        db=db,
        title=album_data.title,
    )

    if existing_album:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An album with this title already exists.",
        )

    unique_artist_ids = list(set(album_data.artist_ids))

    artists = get_artists_by_ids(
        db=db,
        artist_ids=unique_artist_ids,
    )

    if len(artists) != len(unique_artist_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more artist IDs are invalid.",
        )

    return create_album(
        db=db,
        album_data=album_data,
        artists=artists,
    )


@router.get(
    "",
    response_model=list[AlbumResponse],
)
def list_albums(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[AlbumResponse]:
    return get_albums(
        db=db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{album_id}",
    response_model=AlbumResponse,
)
def get_album(
    album_id: int,
    db: Session = Depends(get_db),
) -> AlbumResponse:
    album = get_album_by_id(
        db=db,
        album_id=album_id,
    )

    if album is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Album not found.",
        )

    return album


@router.put(
    "/{album_id}",
    response_model=AlbumResponse,
)
def edit_album(
    album_id: int,
    album_data: AlbumUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
) -> AlbumResponse:
    del current_admin

    album = get_album_by_id(
        db=db,
        album_id=album_id,
    )

    if album is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Album not found.",
        )

    artists = None

    if album_data.artist_ids is not None:
        unique_artist_ids = list(set(album_data.artist_ids))

        if not unique_artist_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An album must have at least one artist.",
            )

        artists = get_artists_by_ids(
            db=db,
            artist_ids=unique_artist_ids,
        )

        if len(artists) != len(unique_artist_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more artist IDs are invalid.",
            )

    return update_album(
        db=db,
        album=album,
        album_data=album_data,
        artists=artists,
    )


@router.delete(
    "/{album_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_album(
    album_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
) -> None:
    del current_admin

    album = get_album_by_id(
        db=db,
        album_id=album_id,
    )

    if album is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Album not found.",
        )

    delete_album(
        db=db,
        album=album,
    )