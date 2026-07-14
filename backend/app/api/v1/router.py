"""
Aggregates every endpoint module under `api/v1/endpoints/` into one router.

As milestones add routers (auth, uploads, jobs, reports, ...), they get
registered here and nowhere else — `main.py` only ever mounts this one
object, so it never needs to change as the API surface grows.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health, auth

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
