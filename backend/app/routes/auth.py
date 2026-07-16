from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    LoginResponse,
    UserCreate,
    UserResponse,
)
from app.services.user_service import (
    authenticate_user,
    create_user,
    get_user_by_email_or_username,
)
from app.utils.dependencies import get_current_user
from app.utils.security import create_access_token


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
) -> User:
    normalized_email = user_data.email.strip().lower()
    normalized_username = user_data.username.strip().lower()

    existing_user = get_user_by_email_or_username(
        db=db,
        email=normalized_email,
        username=normalized_username,
    )

    if existing_user:
        if existing_user.email == normalized_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This username is already taken.",
        )

    return create_user(
        db=db,
        user_data=user_data,
    )


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> LoginResponse:
    user = authenticate_user(
        db=db,
        identifier=form_data.username,
        password=form_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been disabled.",
        )

    access_token = create_access_token(
        subject=str(user.id),
        additional_claims={
            "username": user.username,
            "role": user.role.value,
        },
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user