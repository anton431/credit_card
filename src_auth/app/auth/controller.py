"""Create Read Updare Delete."""
from datetime import datetime, timedelta
from typing import Annotated, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src_auth.app.config import config
from src_auth.app.schemas.auth import TokenData
from src_auth.app.data_sources.storages.user import UserStorage

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth')
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_password, hashed_password):
    """
    Check whether the received password matches the saved hash.

    Args:
        - plain_password (str): The plain text password to verify.
        - hashed_password (str): The hashed password to compare against.

    Returns:
        - bool: True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Hash the password coming from the user.

    Args:
        - password (str): The password to hash.

    Returns:
        - str: The hashed password.
    """
    return pwd_context.hash(password)


def authenticate_user(card_number: str, password: str):
    """
    Authenticate and return the user.

    Args:
        - db (Session): The database session.
        - username (str): The username of the user to authenticate.
        - password (str): The password of the user to authenticate.

    Returns:
        - Union[User, bool]: The authenticated user.
    """
    user = config.storage.get_user(card_number)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False

    return user


def create_access_token(
    data_user: dict,
    expires_delta: Union[timedelta, None] = None,
):
    """
    Create a token with an expiration time of 5 minutes.

    Args:
        - data (dict): The data to be encoded in the token.
        - expires_delta (Union[timedelta, None]): The expiration
            time of the token. If None, the token will expire in 5 minutes.

    Returns:
        - str: The encoded JWT token.
    """
    to_encode = data_user.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=5)
    to_encode.update({'exp': expire})

    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)


def get_current_user(
    session: Annotated[Session, Depends(config.get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
):
    """
    Get the JWT tokens and return the current user.

    Args:
        - token (str): The JWT token.
        - db (Session): The database session.

    Returns:
        - The current user.

    Raises:
        - HTTPException: If the token is invalid or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:  # noqa: WPS229
        payload = jwt.decode(
            token, config.SECRET_KEY, algorithms=[config.ALGORITHM],
        )
        card_number: str = payload.get('sub')
        if card_number is None:
            raise credentials_exception
        token_data = TokenData(card_number=card_number)
    except JWTError:   # noqa: WPS329
        raise credentials_exception
    storage = UserStorage(session)
    user = storage.get_user(card_number=token_data.card_number)
    if user is None:
        raise credentials_exception

    return user
