from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.audio_analysis import AudioAnalysisResponse
from app.schemas.song import SongCreate, SongResponse
from app.services.audio_analysis_service import analyze_audio_file
from app.services.metadata_service import extract_metadata
from app.services.song_service import (
    create_song,
    get_album_by_id,
    get_artists_by_ids,
    get_genres_by_ids,
    get_song_by_title,
    get_songs,
)
from app.utils.dependencies import get_current_admin


router = APIRouter(
    prefix="/api/v1/songs",
    tags=["Songs"],
)

TEMP_DIRECTORY = Path("media/temp")

ALLOWED_AUDIO_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".flac",
    ".ogg",
    ".m4a",
}

MAX_AUDIO_SIZE_BYTES = 25 * 1024 * 1024


@router.post(
    "/analyze",
    response_model=AudioAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_uploaded_song(
    audio_file: UploadFile = File(...),
    current_admin: User = Depends(get_current_admin),
) -> AudioAnalysisResponse:
    del current_admin

    original_filename = audio_file.filename or "uploaded-audio"
    extension = Path(original_filename).suffix.lower()

    if extension not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unsupported audio format. "
                "Use MP3, WAV, FLAC, OGG or M4A."
            ),
        )

    file_content = await audio_file.read()

    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty.",
        )

    if len(file_content) > MAX_AUDIO_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Audio file must be 25 MB or smaller.",
        )

    TEMP_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_filename = f"{uuid4().hex}{extension}"
    temporary_path = TEMP_DIRECTORY / temporary_filename

    temporary_path.write_bytes(file_content)

    try:
        metadata = extract_metadata(temporary_path)
        analysis = analyze_audio_file(temporary_path)

    except Exception as error:
        temporary_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Audio processing failed: {error}",
        ) from error

    extracted_title = metadata.get("title")

    if not extracted_title:
        extracted_title = Path(original_filename).stem

    return AudioAnalysisResponse(
        original_filename=original_filename,
        temporary_file_path=temporary_path.as_posix(),
        mime_type=audio_file.content_type,
        file_size_bytes=len(file_content),
        title=extracted_title,
        artist=metadata.get("artist"),
        album=metadata.get("album"),
        genre=metadata.get("genre"),
        year=metadata.get("year"),
        track_number=metadata.get("track_number"),
        cover_image_path=metadata.get("cover_image_path"),
        **analysis,
    )


@router.post(
    "",
    response_model=SongResponse,
    status_code=status.HTTP_201_CREATED,
)
def save_song(
    song_data: SongCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
) -> SongResponse:
    del current_admin

    existing_song = get_song_by_title(
        db=db,
        title=song_data.title,
    )

    if existing_song is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A song with this title already exists.",
        )

    temporary_path = Path(song_data.temporary_file_path)

    if not temporary_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Temporary audio file does not exist.",
        )

    album = None

    if song_data.album_id is not None:
        album = get_album_by_id(
            db=db,
            album_id=song_data.album_id,
        )

        if album is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Album ID is invalid.",
            )

    unique_artist_ids = list(set(song_data.artist_ids))

    artists = get_artists_by_ids(
        db=db,
        artist_ids=unique_artist_ids,
    )

    if len(artists) != len(unique_artist_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more artist IDs are invalid.",
        )

    unique_genre_ids = list(set(song_data.genre_ids))

    genres = get_genres_by_ids(
        db=db,
        genre_ids=unique_genre_ids,
    )

    if len(genres) != len(unique_genre_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more genre IDs are invalid.",
        )

    try:
        return create_song(
            db=db,
            song_data=song_data,
            album=album,
            artists=artists,
            genres=genres,
        )

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Song could not be saved.",
        ) from error


@router.get(
    "",
    response_model=list[SongResponse],
)
def list_songs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[SongResponse]:
    return get_songs(
        db=db,
        skip=skip,
        limit=limit,
    )