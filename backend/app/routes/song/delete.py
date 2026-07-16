from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.song_service import delete_song, get_song_by_id
from app.utils.dependencies import get_current_admin


router = APIRouter(
    prefix="/api/v1/songs",
    tags=["Songs"],
)


@router.delete(
    "/{song_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_song_endpoint(
    song_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
) -> None:
    del current_admin

    song = get_song_by_id(
        db=db,
        song_id=song_id,
    )

    if song is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found.",
        )

    delete_song(
        db=db,
        song=song,
    )