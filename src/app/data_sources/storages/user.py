"""user."""
from decimal import Decimal

from passlib.context import CryptContext
from sqlalchemy import delete, update
from sqlalchemy.orm import Session

from src.app.data_sources.storages.log import BalanceLog, CommonLog, LogStorage
from src.app.models import user
from src.app.schemas.user import UpdateUser as SchemaUser

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserStorage(object):
    """User storage."""

    def __init__(self, session: Session):
        """Init."""
        self.session = session

    def add(self, card_number: str, password: str):
        """Add new card."""
        user_card = self.session.query(user.User).filter(
            user.User.card_number == card_number,
        ).first()
        if user_card:
            raise ValueError('card already exists')
        db_user = user.User(
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
        user_card = self.session.query(user.User).filter(
            user.User.card_number == card_number,
        ).first()
        if user_card is None or not user_card.is_active:
            raise ValueError('card not exists')
        return user_card

    def update_user(self, user_change: SchemaUser):
        """Update user."""
        user_update = self.session.query(user.User).filter(
            user.User.card_number == user_change.card_number,
        ).first()
        if user_update is None:
            raise ValueError('card not exists')
        user_update.card_number = user_change.card_number
        user_update._balance = user_change.balance
        user_update.hashed_password = pwd_context.hash(user_change.password)
        user_update.limit = user_change.limit
        user_update.is_active = user_change.is_active

        self.session.commit()

    def close(self, card_number: str):
        """Close user."""
        user_close = self.get_user(card_number)
        user_close.is_active = False
        self.session.commit()


class Transactions(object):  # noqa: WPS214
    """Transactions."""

    def __init__(
            self, storage: UserStorage, history: LogStorage, session: Session,
    ):
        """Init."""
        self.session = session
        self._user_storage: UserStorage = storage
        self._history: LogStorage = history

    def get_balance(self, card_number: str) -> Decimal:
        """Get balance."""
        return self._user_storage.get_user(card_number)._balance

    def withdrawal(self, card_number: str, amount: Decimal):
        """Withdrawal."""
        user_current = self._user_storage.get_user(card_number)
        new_balance = user_current._balance - amount
        if amount > 0 and new_balance > -user_current.limit:
            db_log = BalanceLog(
                card_number=card_number,
                before=user_current._balance,
                after=user_current._balance - amount,
                changes=-amount,
                user_id=user_current.id,
            )
            self.session.execute(
                update(user.User).
                where(user.User.card_number == card_number).
                values(_balance=new_balance),
            )
            self.session.add(db_log)
            self.session.commit()
            self.session.refresh(db_log)

    def deposit(self, card_number: str, amount: Decimal):
        """Deposit."""
        user_current = self._user_storage.get_user(card_number)
        new_balance = user_current._balance + amount
        if amount > 0:
            db_log = BalanceLog(
                card_number=card_number,
                before=user_current._balance,
                after=user_current._balance + amount,
                changes=amount,
                user_id=user_current.id,
            )
            self.session.execute(
                update(user.User).
                where(user.User.card_number == card_number).
                values(_balance=new_balance),
            )
            self.session.add(db_log)
            self.session.commit()
            self.session.refresh(db_log)

    def change_limit(self, card_number: str, new_limit: Decimal):
        """Change limit."""
        user_current = self._user_storage.get_user(card_number)
        db_user = CommonLog(
            card_number=user_current.card_number,
            before=user_current.limit,
            after=new_limit,
            changes=('limit', new_limit),
            user_id=user_current.id,
        )
        self.session.execute(
            update(user.User).
            where(user.User.card_number == card_number).
            values(limit=new_limit),
        )
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)

    def __change_balance(self, card_number: str, amount: Decimal):
        self.session.execute(
            update(user.User).
            where(user.User.card_number == card_number).
            values(_balance=amount),
        )
        self.session.commit()

    def __drop_table(self, csl):
        delete_query = delete(csl)
        self.session.execute(delete_query)
        self.session.commit()

    def __check_amount(self, amount: Decimal):
        return amount > 0
