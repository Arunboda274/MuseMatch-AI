from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import hash_password, verify_password


def get_user_by_id(
    db: Session,
    user_id: int,
) -> User | None:
    statement = select(User).where(User.id == user_id)
    return db.scalar(statement)


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    normalized_email = email.strip().lower()

    statement = select(User).where(
        User.email == normalized_email
    )

    return db.scalar(statement)


def get_user_by_username(
    db: Session,
    username: str,
) -> User | None:
    normalized_username = username.strip().lower()

    statement = select(User).where(
        User.username == normalized_username
    )

    return db.scalar(statement)


def get_user_by_email_or_username(
    db: Session,
    email: str,
    username: str,
) -> User | None:
    normalized_email = email.strip().lower()
    normalized_username = username.strip().lower()

    statement = select(User).where(
        or_(
            User.email == normalized_email,
            User.username == normalized_username,
        )
    )

    return db.scalar(statement)


def get_user_by_login_identifier(
    db: Session,
    identifier: str,
) -> User | None:
    normalized_identifier = identifier.strip().lower()

    statement = select(User).where(
        or_(
            User.email == normalized_identifier,
            User.username == normalized_identifier,
        )
    )

    return db.scalar(statement)


def authenticate_user(
    db: Session,
    identifier: str,
    password: str,
) -> User | None:
    user = get_user_by_login_identifier(
        db=db,
        identifier=identifier,
    )

    if user is None:
        return None

    if not verify_password(
        plain_password=password,
        hashed_password=user.hashed_password,
    ):
        return None

    return user


def create_user(
    db: Session,
    user_data: UserCreate,
) -> User:
    new_user = User(
        full_name=user_data.full_name.strip(),
        username=user_data.username.strip().lower(),
        email=user_data.email.strip().lower(),
        hashed_password=hash_password(user_data.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user