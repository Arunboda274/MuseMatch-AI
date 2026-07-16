from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.song import SongResponse, SongUpdate
from app.services.song_service import (
    get_album_by_id,
    get_artists_by_ids,
    get_genres_by_ids,
    get_song_by_id,
    update_song,
)
from app.utils.dependencies import get_current_admin

router = APIRouter(
    prefix="/api/v1/songs",
    tags=["Songs"],
)


@router.put(
    "/{song_id}",
    response_model=SongResponse,
)
def update_song_endpoint(
    song_id: int,
    song_data: SongUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    del current_admin

    song = get_song_by_id(db, song_id)

    if song is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found.",
        )

    album = None

    if song_data.album_id is not None:
        album = get_album_by_id(
            db,
            song_data.album_id,
        )

        if album is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid album ID.",
            )

    artists = None

    if song_data.artist_ids is not None:

        artists = get_artists_by_ids(
            db,
            song_data.artist_ids,
        )

        if len(artists) != len(song_data.artist_ids):
            raise HTTPException(
                status_code=400,
                detail="Invalid artist IDs.",
            )

    genres = None

    if song_data.genre_ids is not None:

        genres = get_genres_by_ids(
            db,
            song_data.genre_ids,
        )

        if len(genres) != len(song_data.genre_ids):
            raise HTTPException(
                status_code=400,
                detail="Invalid genre IDs.",
            )

    return update_song(
        db=db,
        song=song,
        song_data=song_data,
        album=album,
        artists=artists,
        genres=genres,
    )