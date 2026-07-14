"""
Authentication endpoints: signup, login, refresh, and current user.

All endpoints handle their own exception-to-HTTP-response conversion. Service
layer exceptions (ValueError) are caught and converted to 400/401 as appropriate.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, TokenRefreshRequest
from app.services.user import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User signup",
)
def signup(
    user_create: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Create a new user account.

    - **email**: Unique email address
    - **password**: At least 8 characters (hashed with bcrypt before storage)
    - **full_name**: Optional full name

    Returns the created user (without password).
    """
    try:
        service = UserService(db)
        user = service.signup(user_create)
        return UserResponse.model_validate(user)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate a user and return JWT tokens.

    Returns:
    - **access_token**: Short-lived JWT for API requests
    - **refresh_token**: Long-lived JWT to mint new access tokens
    - **token_type**: Always "bearer"
    """
    try:
        service = UserService(db)
        return service.login(credentials.email, credentials.password)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
def refresh(
    req: TokenRefreshRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Mint a new access token from a refresh token.

    Refresh tokens expire after 7 days (configurable via REFRESH_TOKEN_EXPIRE_DAYS).
    """
    try:
        service = UserService(db)
        return service.refresh_access_token(req.refresh_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """
    Return the authenticated user's profile.

    Requires a valid access token in the Authorization header:
    ```
    Authorization: Bearer <access_token>
    ```
    """
    return UserResponse.model_validate(current_user)
