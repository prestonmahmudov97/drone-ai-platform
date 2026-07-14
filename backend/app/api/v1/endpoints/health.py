"""
Health check endpoint.

Used by load balancers, monitoring, and deployment infrastructure to verify
the API is running and ready to serve traffic.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str = "ok"


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns 200 OK if the API is running.
    """
    return HealthResponse(status="ok")
