"""Schemas of BD models."""
from decimal import Decimal

from pydantic import BaseModel


class User(BaseModel):
    """User model."""

    card_number: str
    balance: Decimal


class UpdateUser(User):
    """UpdateUser model."""

    password: str
    limit: Decimal
    is_active: bool = True
