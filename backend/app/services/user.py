"""
User business logic.

Services orchestrate repositories, auth utilities, and other business logic.
Route handlers call services; services never import FastAPI/Request objects.
"""

from sqlalchemy.orm import Session

from app.auth import hash_password, verify_password, create_access_token, create_refresh_token
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, TokenResponse


class UserService:
    """Business logic for user signup, login, and token refresh."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def signup(self, user_create: UserCreate) -> User:
        """
        Create a new user account.

        Raises:
            ValueError: If email already exists.
        """
        existing = self.repo.get_by_email(user_create.email)
        if existing:
            raise ValueError(f"Email {user_create.email} already registered")

        hashed_password = hash_password(user_create.password)
        user = self.repo.create(user_create, hashed_password)
        return user

    def login(self, email: str, password: str) -> TokenResponse:
        """
        Authenticate a user and return access + refresh tokens.

        Raises:
            ValueError: If email not found or password is incorrect.
        """
        user = self.repo.get_active_by_id(self.repo.get_by_email(email).id)
        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password")

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Mint a new access token from a refresh token.

        Raises:
            ValueError: If refresh token is invalid or user is inactive.
        """
        from app.auth.jwt import verify_token

        try:
            payload = verify_token(refresh_token, token_type="refresh")
            user_id = int(payload.get("sub"))
        except Exception:
            raise ValueError("Invalid or expired refresh token")

        user = self.repo.get_active_by_id(user_id)
        if not user:
            raise ValueError("User not found or inactive")

        access_token = create_access_token(subject=user.id)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
