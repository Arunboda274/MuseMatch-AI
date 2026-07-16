from pathlib import Path
from typing import Generator

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.song_service import get_song_by_id


router = APIRouter(
    prefix="/api/v1/songs",
    tags=["Songs"],
)

CHUNK_SIZE = 1024 * 1024


def iter_file_range(
    file_path: Path,
    start: int,
    end: int,
) -> Generator[bytes, None, None]:
    with file_path.open("rb") as audio_file:
        audio_file.seek(start)
        remaining = end - start + 1

        while remaining > 0:
            chunk = audio_file.read(
                min(CHUNK_SIZE, remaining)
            )

            if not chunk:
                break

            remaining -= len(chunk)
            yield chunk


@router.get("/{song_id}/stream")
def stream_song(
    song_id: int,
    range_header: str | None = Header(
        default=None,
        alias="Range",
    ),
    db: Session = Depends(get_db),
):
    song = get_song_by_id(
        db=db,
        song_id=song_id,
    )

    if song is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found.",
        )

    audio_path = Path(song.audio_file_path)

    if not audio_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found on the server.",
        )

    file_size = audio_path.stat().st_size
    media_type = song.mime_type or "audio/mpeg"

    start = 0
    end = file_size - 1
    response_status = status.HTTP_200_OK

    if range_header:
        if not range_header.startswith("bytes="):
            raise HTTPException(
                status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                detail="Invalid Range header.",
                headers={
                    "Content-Range": f"bytes */{file_size}",
                },
            )

        requested_range = range_header.replace(
            "bytes=",
            "",
            1,
        ).strip()

        if "," in requested_range:
            raise HTTPException(
                status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                detail="Multiple ranges are not supported.",
                headers={
                    "Content-Range": f"bytes */{file_size}",
                },
            )

        start_text, _, end_text = requested_range.partition("-")

        try:
            if start_text:
                start = int(start_text)

                if end_text:
                    end = int(end_text)
            else:
                suffix_length = int(end_text)

                if suffix_length <= 0:
                    raise ValueError

                start = max(file_size - suffix_length, 0)

        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                detail="Invalid byte range.",
                headers={
                    "Content-Range": f"bytes */{file_size}",
                },
            ) from error

        if start < 0 or start >= file_size or end < start:
            raise HTTPException(
                status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                detail="Requested range is outside the file.",
                headers={
                    "Content-Range": f"bytes */{file_size}",
                },
            )

        end = min(end, file_size - 1)
        response_status = status.HTTP_206_PARTIAL_CONTENT

    content_length = end - start + 1

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(content_length),
        "Content-Disposition": 'inline; filename="song.mp3"',
        "Cache-Control": "public, max-age=3600",
        "X-Content-Type-Options": "nosniff",
    }

    if response_status == status.HTTP_206_PARTIAL_CONTENT:
        headers["Content-Range"] = (
            f"bytes {start}-{end}/{file_size}"
        )

    return StreamingResponse(
        iter_file_range(
            file_path=audio_path,
            start=start,
            end=end,
        ),
        status_code=response_status,
        media_type=media_type,
        headers=headers,
    )