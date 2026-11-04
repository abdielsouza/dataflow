from uuid import uuid4

import pytest
from dataflow_api.main import app
from fastapi.testclient import TestClient


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def user_payload() -> dict[str, str]:
    unique = uuid4().hex[:8]
    return {
        "username": f"user_{unique}",
        "email": f"{unique}@example.com",
        "password": "senha-secreta",
    }


def test_register_user(client: TestClient, user_payload: dict[str, str]) -> None:
    response = client.post("/auth/register", json=user_payload)

    assert response.status_code == 200
    body = response.json()
    assert body["username"] == user_payload["username"]
    assert body["email"] == user_payload["email"]
    assert "password" not in body
    assert "password_hash" not in body


def test_login_user(client: TestClient, user_payload: dict[str, str]) -> None:
    client.post("/auth/register", json=user_payload)

    response = client.post(
        "/auth/login",
        json={
            "email": user_payload["email"],
            "password": user_payload["password"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "access_token" in payload
    assert payload["token_type"] == "bearer"


def test_login_user_with_invalid_credentials_returns_401(
    client: TestClient,
    user_payload: dict[str, str],
) -> None:
    client.post("/auth/register", json=user_payload)

    response = client.post(
        "/auth/login",
        json={
            "email": user_payload["email"],
            "password": "senha-errada",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials."


def test_protected_analyses_endpoints_require_authentication(
    client: TestClient,
    user_payload: dict[str, str],
) -> None:
    client.post("/auth/register", json=user_payload)
    token_response = client.post(
        "/auth/login",
        json={
            "email": user_payload["email"],
            "password": user_payload["password"],
        },
    )
    headers = {"Authorization": f"Bearer {token_response.json()['access_token']}"}

    response = client.get("/analyses", headers=headers)
    assert response.status_code == 200
    assert response.json() == []

    unauthorized = client.get("/analyses")
    assert unauthorized.status_code == 401
    assert unauthorized.json()["detail"] == "Not authenticated"