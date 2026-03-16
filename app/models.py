
from pydantic import BaseModel, field_validator
from typing import Union, Literal
from datetime import datetime
import re


class SearchProperties(BaseModel):

    origin: str
    destination: str
    date: str

    @field_validator("*", mode="before")
    @classmethod
    def normalize_strings(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v


class PurchaseProperties(BaseModel):

    amount: int
    payment_method: str
    phone: str

    @field_validator("payment_method", mode="before")
    @classmethod
    def normalize_payment(cls, v):
        return v.lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):

        pattern = r"^\+?[1-9]\d{7,14}$"

        if not re.match(pattern, v):
            raise ValueError("invalid phone")

        return v


class SearchEvent(BaseModel):

    event: Literal["search"]
    user_id: str
    timestamp: datetime
    properties: SearchProperties

    @field_validator("user_id")
    @classmethod
    def validate_user(cls, v):

        if not v:
            raise ValueError("user_id required")

        return v


class PurchaseEvent(BaseModel):

    event: Literal["purchase_complete"]
    user_id: str
    timestamp: datetime
    properties: PurchaseProperties

    @field_validator("user_id")
    @classmethod
    def validate_user(cls, v):

        if not v:
            raise ValueError("user_id required")

        return v


Event = Union[SearchEvent, PurchaseEvent]