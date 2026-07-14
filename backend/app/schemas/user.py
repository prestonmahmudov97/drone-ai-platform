"""
Pydantic schemas for user-related requests and responses.

Schemas are request/response contracts that live independently of the ORM.
This keeps API serialization decoupled from the database schema.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user fields, shared across requests/responses."""

    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    """Schema for signup requests."""

    password: str = Field(..., min_length=8, description="At least 8 characters")


class UserLogin(BaseModel):
    """Schema for login requests."""

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user responses (public-safe, no password)."""

    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Schema for token responses (login, refresh)."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    """Schema for token refresh requests."""

    refresh_token: str
