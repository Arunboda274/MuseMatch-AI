import re
from pathlib import Path
from uuid import uuid4

from mutagen import File
from mutagen.id3 import APIC


COVER_DIRECTORY = Path("media/covers")


def clean_metadata_text(text: str | None) -> str | None:
    """
    Remove website names and unwanted text from metadata.
    """

    if not text:
        return None

    cleaned = text

    patterns = [
        r"::\s*SenSongsMp3\.Com",
        r"SenSongsMp3\.Com",
        r"Masstamilan",
        r"Pagalworld",
        r"DJPunjab",
        r"Mr-Jatt",
        r"Starmusiq",
        r"Isaimini",
        r"\.Com",
        r"\.Net",
        r"\.Org",
    ]

    for pattern in patterns:
        cleaned = re.sub(
            pattern,
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

    cleaned = cleaned.strip()

    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned,
    )

    return cleaned or None


def extract_metadata(file_path: str | Path) -> dict:
    """
    Extract metadata from an audio file.
    """

    audio = File(file_path)

    metadata = {
        "title": None,
        "artist": None,
        "album": None,
        "genre": None,
        "year": None,
        "track_number": None,
        "cover_image_path": None,
    }

    if audio is None:
        return metadata

    tags = audio.tags

    if tags is None:
        return metadata

    # ---------- TITLE ----------
    if "TIT2" in tags:
        metadata["title"] = clean_metadata_text(
            str(tags["TIT2"])
        )

    # ---------- ARTIST ----------
    if "TPE1" in tags:
        metadata["artist"] = clean_metadata_text(
            str(tags["TPE1"])
        )

    # ---------- ALBUM ----------
    if "TALB" in tags:
        metadata["album"] = clean_metadata_text(
            str(tags["TALB"])
        )

    # ---------- GENRE ----------
    if "TCON" in tags:
        metadata["genre"] = clean_metadata_text(
            str(tags["TCON"])
        )

    # ---------- YEAR ----------
    if "TDRC" in tags:
        metadata["year"] = str(tags["TDRC"])

    # ---------- TRACK ----------
    if "TRCK" in tags:
        metadata["track_number"] = str(tags["TRCK"])

    # ---------- COVER IMAGE ----------
    COVER_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    for tag in tags.values():
        if isinstance(tag, APIC):
            extension = ".jpg"

            if tag.mime == "image/png":
                extension = ".png"

            filename = f"{uuid4().hex}{extension}"
            cover_path = COVER_DIRECTORY / filename

            with open(cover_path, "wb") as image_file:
                image_file.write(tag.data)

            metadata["cover_image_path"] = cover_path.as_posix()
            break

    return metadata