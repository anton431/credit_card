"""Create Read Updare Delete."""
from passlib.context import CryptContext

from src.app.data_sources.storages.user import UserStorage

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_password_hash(password):
    """
    Hash the password coming from the user.

    Args:
        - password (str): The password to hash.

    Returns:
        - str: The hashed password.
    """
    return pwd_context.hash(password)


def get_current_user(card_number, session):
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
    storage = UserStorage(session=session)
    return storage.get_user(card_number=card_number)
