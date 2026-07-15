"""
SQLAlchemy ORM models (tables). Each model maps 1:1 to a database table
and contains no business logic beyond relationships/constraints. Wired up
in Milestone 4.
"""

from app.models.user import User
from app.models.upload import Upload

__all__ = ["User", "Upload"]
