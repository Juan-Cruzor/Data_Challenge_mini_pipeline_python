from pydantic import BaseModel, field_validator
from typing import Union, Literal, Optional
from datetime import datetime
import re

PHONE_RE = re.compile(r"^\+?[1-9]\d{7,14}$")


class SearchProperties(BaseModel):
    origin: str = "unknown"
    destination: str = "unknown"
    date: Optional[str] = None

    @field_validator("origin", "destination", mode="before")
    @classmethod
    def normalize_strings(cls, v):
        if isinstance(v, str):
            return v.strip().lower()
        return "unknown"

    # Silently drop fields that don't belong to search events (e.g. amount, phone).
    model_config = {"extra": "ignore"}


class PurchaseProperties(BaseModel):
    amount: float = 0.0  # float to match NUMERIC in PostgreSQL
    payment_method: str = "unknown"
    phone: Optional[str] = None

    @field_validator("payment_method", mode="before")
    @classmethod
    def normalize_payment(cls, v):
        return v.strip().lower() if isinstance(v, str) else "unknown"

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone(cls, v):
        if v is None or str(v).strip() == "":
            return None
        phone = str(v).strip()
        if not PHONE_RE.match(phone):
            raise ValueError(f"invalid phone number: {phone!r}")
        return phone

    # Silently drop fields that don't belong to purchase events (e.g. origin, destination).
    model_config = {"extra": "ignore"}


class SearchEvent(BaseModel):
    event: Literal["search"]
    user_id: str
    timestamp: datetime
    properties: SearchProperties

    # mode="before" so we catch None and empty string before Pydantic
    # tries to coerce the value into a str (which would succeed for None -> "None").
    @field_validator("user_id", mode="before")
    @classmethod
    def validate_user(cls, v):
        if not v or str(v).strip() == "":
            raise ValueError("user_id is required and cannot be empty")
        return str(v).strip()


class PurchaseEvent(BaseModel):
    event: Literal["purchase_complete"]
    user_id: str
    timestamp: datetime
    properties: PurchaseProperties

    @field_validator("user_id", mode="before")
    @classmethod
    def validate_user(cls, v):
        if not v or str(v).strip() == "":
            raise ValueError("user_id is required and cannot be empty")
        return str(v).strip()


# Union so Pydantic picks the right model based on the `event` field.
Event = Union[SearchEvent, PurchaseEvent]
