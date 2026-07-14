"""
JWT token issuance and verification.

Tokens carry user identity + minimal claims. Refresh tokens are longer-lived
and used to mint new access tokens without re-authenticating.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.core.config import get_settings


def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    """
    Create a short-lived access token.

    Args:
        subject: User ID (int) or email (str) to embed in the token.
        expires_delta: Lifetime of the token; defaults to ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        Encoded JWT access token.
    """
    settings = get_settings()
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(subject: str | int) -> str:
    """
    Create a longer-lived refresh token.

    Args:
        subject: User ID (int) or email (str) to embed in the token.

    Returns:
        Encoded JWT refresh token.
    """
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> dict[str, Any]:
    """
    Decode and verify a JWT token.

    Args:
        token: The JWT string to verify.
        token_type: Expected token type ("access" or "refresh").

    Returns:
        Decoded token payload.

    Raises:
        JWTError: If the token is invalid, expired, or has the wrong type.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != token_type:
            raise JWTError("Invalid token type")
        return payload
    except JWTError:
        raise
