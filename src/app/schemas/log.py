"""Schemas of BD models."""
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel


class HistoryLog(BaseModel):
    """HistoryLog model."""

    card_number: str
    before: Decimal
    after: Decimal
    changes: Decimal
    user_id: int
    datetime_utc: datetime


class CommonLog(BaseModel):
    """HistoryLog model."""

    card_number: str
    before: Any
    after: Any
    changes: Any
    user_id: int
    datetime_utc: datetime
