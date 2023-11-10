"""Log."""
from datetime import datetime

from sqlalchemy.orm import Session

from src.app.models.log import BalanceLog, CommonLog
from src.app.schemas.log import HistoryLog


class LogStorage(object):
    """Log storage."""

    def __init__(self, session: Session):
        """Init."""
        self.session = session

    def save(self, log: HistoryLog):
        """Save log in other logs."""
        db_user = CommonLog(
            card_number=log.card_number,
            before=log.before,
            after=log.after,
            changes=log.changes,
            user_id=log.user_id,
        )
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)

    def get_balance_history(
        self,
        card_number: str,
        time_from: datetime,
        time_to: datetime,
    ) -> list[BalanceLog]:
        """Get history of balance."""
        return self.session.query(BalanceLog).filter(
            BalanceLog.card_number == card_number,
            BalanceLog._datetime_utc >= time_from,
            BalanceLog._datetime_utc <= time_to,
        ).all()
