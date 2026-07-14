"""
FastAPI dependencies for authentication.

These are injected via Depends() in route handlers to enforce auth on
protected endpoints and extract the current user.
"""

from jose import JWTError

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials

from app.auth.jwt import verify_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from sqlalchemy.orm import Session

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Extract and verify the current user from the Authorization header.

    This dependency is used on protected routes. It:
    1. Extracts the Bearer token from the Authorization header
    2. Verifies the JWT signature and expiration
    3. Looks up the user in the database
    4. Returns the User object or raises 401 Unauthorized

    Raises:
        HTTPException: 401 if token is invalid, expired, or user not found.
    """
    token = credentials.credentials
    try:
        payload = verify_token(token, token_type="access")
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    repo = UserRepository(db)
    user = repo.get_active_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency for superuser-only endpoints.

    Raises:
        HTTPException: 403 if user is not a superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return current_user
