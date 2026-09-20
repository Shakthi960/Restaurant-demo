"""Pydantic request/response schemas for the public API."""

import re
from datetime import date, time
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

# Indian mobile number — +91 / 0 prefix optional; whitespace allowed.
PHONE_PATTERN = r"^(\+91[\s-]?|0)?[6-9]\d{9}$"


class ReservationIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    phone: str = Field(..., min_length=10, max_length=20)
    email: Optional[EmailStr] = Field(None, max_length=120)
    location: str = Field(..., min_length=2, max_length=40)  # location slug, e.g. "chennai"
    date: date
    time: time
    guests: int = Field(..., ge=1, le=40)

    @field_validator("email", mode="before")
    @classmethod
    def _blank_email_to_none(cls, value):
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        clean = re.sub(r"\s", "", v.strip())
        if not re.match(PHONE_PATTERN, clean):
            raise ValueError("Enter a valid Indian mobile number (e.g. +91 90000 00000).")
        return v.strip()

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("Reservation date cannot be in the past.")
        return v


class ReservationOut(BaseModel):
    id: str
    status: str = "pending"
    message: str = "Your request has been received. You will get a WhatsApp or email confirmation once the restaurant approves your booking."


class ReviewIn(BaseModel):
    author: str = Field(..., min_length=2, max_length=80)
    city: str = Field("", max_length=60)
    rating: int = Field(..., ge=1, le=5)
    review: str = Field(..., min_length=5, max_length=1000)


class ReviewOut(BaseModel):
    id: str
    status: str = "pending_moderation"
    message: str = "Thank you for your review! It will appear on the site after moderation."


class ContactIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    email: EmailStr = Field(..., max_length=120)
    phone: str = Field("", max_length=20)
    message: str = Field(..., min_length=5, max_length=2000)


class ContactOut(BaseModel):
    id: str
    status: str = "received"
    message: str = "Thank you for writing to us. We will be in touch shortly."