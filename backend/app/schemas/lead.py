from datetime import datetime
from enum import StrEnum

import phonenumbers
from pydantic import EmailStr, Field, field_validator

from app.schemas.common import APIModel


class LeadStatus(StrEnum):
    NEW = "New"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    LOST = "Lost"


class LeadSource(StrEnum):
    WEBSITE = "Website"
    REFERRAL = "Referral"
    SOCIAL_MEDIA = "Social Media"
    ADVERTISEMENT = "Advertisement"
    COLD_CALL = "Cold Call"
    OTHER = "Other"


def clean_text(value: str) -> str:
    normalized = " ".join(value.split())
    if not normalized:
        raise ValueError("This field cannot be blank.")
    return normalized


class LeadInput(APIModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=32)
    company: str = Field(min_length=1, max_length=120)
    source: LeadSource
    status: LeadStatus = LeadStatus.NEW

    @field_validator("name", "company")
    @classmethod
    def clean_text_fields(cls, value: str) -> str:
        return clean_text(value)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        compact = value.strip()
        try:
            parsed = phonenumbers.parse(compact, None if compact.startswith("+") else "US")
        except phonenumbers.NumberParseException as exc:
            raise ValueError(
                "Enter a valid phone number, including country code if needed."
            ) from exc
        if not phonenumbers.is_valid_number(parsed):
            raise ValueError("Enter a valid phone number, including country code if needed.")
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)


class LeadUpdate(APIModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=7, max_length=32)
    company: str | None = Field(default=None, min_length=1, max_length=120)
    source: LeadSource | None = None
    status: LeadStatus | None = None

    @field_validator("name", "company")
    @classmethod
    def clean_optional_text_fields(cls, value: str | None) -> str | None:
        return clean_text(value) if value is not None else None

    @field_validator("email")
    @classmethod
    def normalize_optional_email(cls, value: str | None) -> str | None:
        return value.strip().lower() if value is not None else None

    @field_validator("phone")
    @classmethod
    def validate_optional_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return LeadInput.validate_phone(value)


class LeadStatusUpdate(APIModel):
    status: LeadStatus


class LeadResponse(APIModel):
    id: str
    name: str
    email: str
    phone: str
    company: str
    source: LeadSource
    status: LeadStatus
    created_at: datetime
    updated_at: datetime


class LeadPage(APIModel):
    items: list[LeadResponse]
    page: int
    limit: int
    total: int
    pages: int


class DashboardStats(APIModel):
    total: int
    new: int
    contacted: int
    qualified: int
    lost: int
