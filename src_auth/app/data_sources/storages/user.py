"""user."""
from decimal import Decimal

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src_auth.app.models.models import User

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserStorage(object):
    """User storage."""

    def __init__(self, session: Session):
        """Init."""
        self.session = session

    def add(self, card_number: str, password: str):
        """Add new card."""
        user_card = self.session.query(User).filter(
            User.card_number == card_number,
        ).first()
        if user_card:
            raise ValueError('card already exists')
        db_user = User(
            card_number=card_number,
            hashed_password=pwd_context.hash(password),
            limit=Decimal(0),
            _balance=Decimal(0),
        )
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)

    def get_user(self, card_number: str):
        """Get user."""
        user_card = self.session.query(User).filter(
            User.card_number == card_number,
        ).first()
        if user_card is None or not user_card.is_active:
            raise ValueError('card not exists')
        return user_card
