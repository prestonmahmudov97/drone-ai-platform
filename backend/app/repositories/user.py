"""
User data access layer.

The repository is the only place allowed to construct SQLAlchemy queries for
users. Services call repositories, never construct queries directly.
"""

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
    """CRUD operations for User."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_create: UserCreate, hashed_password: str) -> User:
        """
        Create a new user.

        Args:
            user_create: Signup request (email, full_name, password).
            hashed_password: The bcrypt hash of the password.

        Returns:
            The created User object.
        """
        db_user = User(
            email=user_create.email,
            hashed_password=hashed_password,
            full_name=user_create.full_name,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_by_email(self, email: str) -> User | None:
        """Get a user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> User | None:
        """Get a user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_active_by_id(self, user_id: int) -> User | None:
        """Get an active user by ID."""
        return (
            self.db.query(User)
            .filter(User.id == user_id, User.is_active == True)
            .first()
        )
