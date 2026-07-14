"""
Data-access layer. Repositories are the *only* code allowed to construct
SQLAlchemy queries; services call repositories, never `db.query(...)`
directly. This keeps persistence concerns swappable and testable behind
a plain-Python interface.
"""

from app.repositories.user import UserRepository

__all__ = ["UserRepository"]
