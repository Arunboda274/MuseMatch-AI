from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.artist import (
    ArtistCreate,
    ArtistResponse,
    ArtistUpdate,
    RoleCreate,
    RoleResponse,
)
from app.services.artist_service import (
    create_artist,
    create_role,
    delete_artist,
    get_artist_by_id,
    get_artist_by_name,
    get_artists,
    get_role_by_name,
    get_roles,
    get_roles_by_ids,
    update_artist,
)
from app.utils.dependencies import get_current_admin


router = APIRouter(
    prefix="/api/v1",
)


@router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Roles"],
)
def add_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
) -> RoleResponse:
    del current_admin

    existing_role = get_role_by_name(db, role_data.name)

    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This role already exists.",
        )

    return create_role(db, role_data)


@router.get(
    "/roles",
    response_model=list[RoleResponse],
    tags=["Roles"],
)
def list_roles(
    db: Session = Depends(get_db),
) -> list[RoleResponse]:
    return get_roles(db)


@router.post(
    "/artists",
    response_model=ArtistResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Artists"],
)
def add_artist(
    artist_data: ArtistCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
) -> ArtistResponse:
    del current_admin

    existing_artist = get_artist_by_name(
        db,
        artist_data.name,
    )

    if existing_artist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An artist with this name already exists.",
        )

    roles = get_roles_by_ids(
        db,
        artist_data.role_ids,
    )

    if len(roles) != len(set(artist_data.role_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more role IDs are invalid.",
        )

    try:
        return create_artist(
            db=db,
            artist_data=artist_data,
            roles=roles,
        )
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Artist could not be created.",
        )


@router.get(
    "/artists",
    response_model=list[ArtistResponse],
    tags=["Artists"],
)
def list_artists(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[ArtistResponse]:
    return get_artists(
        db=db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/artists/{artist_id}",
    response_model=ArtistResponse,
    tags=["Artists"],
)
def get_artist(
    artist_id: int,
    db: Session = Depends(get_db),
) -> ArtistResponse:
    artist = get_artist_by_id(db, artist_id)

    if artist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found.",
        )

    return artist


@router.put(
    "/artists/{artist_id}",
    response_model=ArtistResponse,
    tags=["Artists"],
)
def edit_artist(
    artist_id: int,
    artist_data: ArtistUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
) -> ArtistResponse:
    del current_admin

    artist = get_artist_by_id(db, artist_id)

    if artist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found.",
        )

    roles = None

    if artist_data.role_ids is not None:
        roles = get_roles_by_ids(
            db,
            artist_data.role_ids,
        )

        if len(roles) != len(set(artist_data.role_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more role IDs are invalid.",
            )

    return update_artist(
        db=db,
        artist=artist,
        artist_data=artist_data,
        roles=roles,
    )


@router.delete(
    "/artists/{artist_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Artists"],
)
def remove_artist(
    artist_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
) -> None:
    del current_admin

    artist = get_artist_by_id(db, artist_id)

    if artist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found.",
        )

    delete_artist(db, artist)