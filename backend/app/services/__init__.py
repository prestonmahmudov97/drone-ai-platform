"""
Business logic layer. Services orchestrate repositories, the vision
abstraction layer, and storage/background-job clients. Route handlers in
`api/` call services; services never import FastAPI/Request objects.
"""

from app.services.user import UserService

__all__ = ["UserService"]
