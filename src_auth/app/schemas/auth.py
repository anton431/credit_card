"""Schemas of BD models."""
from decimal import Decimal

from pydantic import BaseModel


class User(BaseModel):
    """User model."""

    card_number: str
    balance: Decimal


class Token(BaseModel):
    """Token model."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token card_number."""

    card_number: str | None = None
