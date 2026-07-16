from pathlib import Path
from shutil import move
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.album import Album
from app.models.artist import Artist
from app.models.genre import Genre
from app.models.song import Song
from app.models.song_feature import SongFeature
from app.schemas.song import SongCreate, SongFeatureCreate, SongUpdate


SONG_DIRECTORY = Path("media/songs")
TEMP_DIRECTORY = Path("media/temp")


def get_album_by_id(
    db: Session,
    album_id: int,
) -> Album | None:
    statement = select(Album).where(
        Album.id == album_id
    )

    return db.scalar(statement)


def get_artists_by_ids(
    db: Session,
    artist_ids: list[int],
) -> list[Artist]:
    if not artist_ids:
        return []

    statement = select(Artist).where(
        Artist.id.in_(artist_ids)
    )

    return list(db.scalars(statement).all())


def get_genres_by_ids(
    db: Session,
    genre_ids: list[int],
) -> list[Genre]:
    if not genre_ids:
        return []

    statement = select(Genre).where(
        Genre.id.in_(genre_ids)
    )

    return list(db.scalars(statement).all())


def get_song_by_id(
    db: Session,
    song_id: int,
) -> Song | None:
    statement = (
        select(Song)
        .options(
            selectinload(Song.album),
            selectinload(Song.artists),
            selectinload(Song.genres),
            selectinload(Song.features),
        )
        .where(Song.id == song_id)
    )

    return db.scalar(statement)


def get_song_by_title(
    db: Session,
    title: str,
) -> Song | None:
    normalized_title = title.strip().lower()

    statement = select(Song).where(
        func.lower(Song.title) == normalized_title
    )

    return db.scalar(statement)


def get_songs(
    db: Session,
    skip: int = 0,
    limit: int = 20,
) -> list[Song]:
    statement = (
        select(Song)
        .options(
            selectinload(Song.album),
            selectinload(Song.artists),
            selectinload(Song.genres),
            selectinload(Song.features),
        )
        .order_by(Song.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def move_audio_to_song_directory(
    temporary_file_path: str,
) -> Path:
    temporary_path = Path(temporary_file_path)

    if not temporary_path.exists():
        raise FileNotFoundError(
            "Temporary audio file was not found."
        )

    try:
        resolved_temp_directory = TEMP_DIRECTORY.resolve()
        resolved_file = temporary_path.resolve()
    except OSError as error:
        raise ValueError(
            "Temporary audio path is invalid."
        ) from error

    if (
        resolved_temp_directory != resolved_file.parent
        and resolved_temp_directory not in resolved_file.parents
    ):
        raise ValueError(
            "Temporary audio file must be inside media/temp."
        )

    SONG_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    extension = temporary_path.suffix.lower()
    destination_name = f"{uuid4().hex}{extension}"
    destination_path = SONG_DIRECTORY / destination_name

    move(
        str(temporary_path),
        str(destination_path),
    )

    return destination_path


def create_song_feature(
    feature_data: SongFeatureCreate,
) -> SongFeature:
    return SongFeature(
        tempo=feature_data.tempo,
        energy=feature_data.energy,
        danceability=feature_data.danceability,
        acousticness=feature_data.acousticness,
        instrumentalness=feature_data.instrumentalness,
        liveness=feature_data.liveness,
        speechiness=feature_data.speechiness,
        valence=feature_data.valence,
        loudness=feature_data.loudness,
        sample_rate=feature_data.sample_rate,
    )


def create_song(
    db: Session,
    song_data: SongCreate,
    album: Album | None,
    artists: list[Artist],
    genres: list[Genre],
) -> Song:
    permanent_audio_path = move_audio_to_song_directory(
        song_data.temporary_file_path
    )

    song_feature = create_song_feature(
        song_data.features
    )

    song = Song(
        title=song_data.title.strip(),
        album=album,
        language=(
            song_data.language.strip()
            if song_data.language
            else None
        ),
        mood=(
            song_data.mood.strip()
            if song_data.mood
            else None
        ),
        release_date=song_data.release_date,
        duration_seconds=song_data.duration_seconds,
        audio_file_path=permanent_audio_path.as_posix(),
        cover_image_path=(
            song_data.cover_image_path.strip()
            if song_data.cover_image_path
            else None
        ),
        lyrics=(
            song_data.lyrics.strip()
            if song_data.lyrics
            else None
        ),
        explicit=song_data.explicit,
        track_number=song_data.track_number,
        disc_number=song_data.disc_number,
        popularity=song_data.popularity,
        file_size_bytes=song_data.file_size_bytes,
        mime_type=song_data.mime_type,
        bitrate=song_data.bitrate,
        status=song_data.status,
        artists=artists,
        genres=genres,
        features=song_feature,
    )

    try:
        db.add(song)
        db.commit()
        db.refresh(song)

    except Exception:
        db.rollback()
        permanent_audio_path.unlink(missing_ok=True)
        raise

    saved_song = get_song_by_id(
        db=db,
        song_id=song.id,
    )

    if saved_song is None:
        raise RuntimeError(
            "Song was created but could not be loaded."
        )

    return saved_song


def update_song_feature(
    feature: SongFeature,
    feature_data: SongFeatureCreate,
) -> None:
    feature.tempo = feature_data.tempo
    feature.energy = feature_data.energy
    feature.danceability = feature_data.danceability
    feature.acousticness = feature_data.acousticness
    feature.instrumentalness = feature_data.instrumentalness
    feature.liveness = feature_data.liveness
    feature.speechiness = feature_data.speechiness
    feature.valence = feature_data.valence
    feature.loudness = feature_data.loudness
    feature.sample_rate = feature_data.sample_rate


def update_song(
    db: Session,
    song: Song,
    song_data: SongUpdate,
    album: Album | None,
    artists: list[Artist] | None,
    genres: list[Genre] | None,
) -> Song:
    update_data = song_data.model_dump(
        exclude_unset=True,
        exclude={
            "album_id",
            "artist_ids",
            "genre_ids",
            "features",
        },
    )

    for field, value in update_data.items():
        if isinstance(value, str):
            value = value.strip()

        setattr(song, field, value)

    if "album_id" in song_data.model_fields_set:
        song.album = album

    if song_data.artist_ids is not None:
        song.artists = artists or []

    if song_data.genre_ids is not None:
        song.genres = genres or []

    if song_data.features is not None:
        if song.features is None:
            song.features = create_song_feature(
                song_data.features
            )
        else:
            update_song_feature(
                song.features,
                song_data.features,
            )

    db.commit()

    updated_song = get_song_by_id(
        db=db,
        song_id=song.id,
    )

    if updated_song is None:
        raise RuntimeError(
            "Updated song could not be loaded."
        )

    return updated_song


def delete_song(
    db: Session,
    song: Song,
) -> None:
    audio_path = Path(song.audio_file_path)

    db.delete(song)
    db.commit()

    audio_path.unlink(missing_ok=True)