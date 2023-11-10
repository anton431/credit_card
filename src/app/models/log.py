"""Models log."""
from sqlalchemy import (DECIMAL, TIMESTAMP, Column, ForeignKey,
                        Integer, String, func)
from sqlalchemy.orm import relationship

from src.app.config.database import Base


class CommonLog(Base):
    """Table CommonLog."""

    __tablename__ = 'commonlog'

    id = Column(Integer, primary_key=True)
    card_number = Column(String(20))
    before = Column(String(300))
    after = Column(String(300))
    changes = Column(String(300))
    user_id = Column(Integer, ForeignKey('User.id'))
    _datetime_utc = Column(TIMESTAMP, default=func.now())

    user = relationship('User', back_populates='common_logs')


class BalanceLog(Base):
    """Table BalanceLog."""

    __tablename__ = 'balancelog'

    id = Column(Integer, primary_key=True)
    card_number = Column(String(20))
    before = Column(DECIMAL)
    after = Column(DECIMAL)
    changes = Column(DECIMAL)
    user_id = Column(Integer, ForeignKey('User.id'))
    _datetime_utc = Column(TIMESTAMP, default=func.now())

    user = relationship('User', back_populates='balance_logs')
