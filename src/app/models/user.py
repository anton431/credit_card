"""models."""
from dataclasses import dataclass

from sqlalchemy import DECIMAL, Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from src.app.config.database import Base


class User(Base):
    """Table User."""

    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    card_number = Column(String(20), unique=True)
    hashed_password = Column(String(100))
    limit = Column(DECIMAL)
    is_active = Column(Boolean, default=True)
    _balance = Column(DECIMAL)

    common_logs = relationship('CommonLog', back_populates='user')
    balance_logs = relationship('BalanceLog', back_populates='user')


@dataclass
class Time(object):
    """Time class for API."""

    year: int = 2023
    month: int = 1
    day: int = 1
    hour: int = 0
    minute: int = 0
    second: int = 0
