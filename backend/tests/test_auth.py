"""
Tests for authentication endpoints and auth utilities.

Uses the TestClient (in-memory SQLite) to test signup, login, refresh, and
protected endpoints without hitting the real Postgres.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client(test_db):
    """Create a TestClient with the test database injected."""
    from app.db.session import get_db

    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_signup_success(client: TestClient) -> None:
    """Happy path: create a new user account."""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "alice@example.com",
            "password": "password123",
            "full_name": "Alice Smith",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["full_name"] == "Alice Smith"
    assert "hashed_password" not in data
    assert data["is_active"] is True
    assert data["is_superuser"] is False


def test_signup_duplicate_email(client: TestClient) -> None:
    """Signup with an email that already exists."""
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "bob@example.com",
            "password": "password123",
        },
    )
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "bob@example.com",
            "password": "different_password",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_signup_weak_password(client: TestClient) -> None:
    """Signup with a password that's too short."""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "charlie@example.com",
            "password": "short",
        },
    )
    assert response.status_code == 422


def test_login_success(client: TestClient) -> None:
    """Happy path: login and receive tokens."""
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "diana@example.com",
            "password": "password123",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "diana@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_email(client: TestClient) -> None:
    """Login with an email that doesn't exist."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 401


def test_login_wrong_password(client: TestClient) -> None:
    """Login with the correct email but wrong password."""
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "eve@example.com",
            "password": "correct_password",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "eve@example.com",
            "password": "wrong_password",
        },
    )
    assert response.status_code == 401


def test_refresh_access_token(client: TestClient) -> None:
    """Refresh an access token using a refresh token."""
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "frank@example.com",
            "password": "password123",
        },
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "frank@example.com",
            "password": "password123",
        },
    )
    refresh_token = login_response.json()["refresh_token"]
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_get_me_authenticated(client: TestClient) -> None:
    """Get current user info when authenticated."""
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "grace@example.com",
            "password": "password123",
            "full_name": "Grace Lee",
        },
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "grace@example.com",
            "password": "password123",
        },
    )
    access_token = login_response.json()["access_token"]
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "grace@example.com"


def test_get_me_unauthenticated(client: TestClient) -> None:
    """Get /me without a token fails."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403


def test_get_me_invalid_token(client: TestClient) -> None:
    """Get /me with an invalid token fails."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"},
    )
    assert response.status_code == 403
