from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.song import SongResponse
from app.services.song_service import get_song_by_id


router = APIRouter(
    prefix="/api/v1/songs",
    tags=["Songs"],
)


@router.get(
    "/{song_id}",
    response_model=SongResponse,
)
def get_single_song(
    song_id: int,
    db: Session = Depends(get_db),
) -> SongResponse:
    song = get_song_by_id(
        db=db,
        song_id=song_id,
    )

    if song is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found.",
        )

    return song