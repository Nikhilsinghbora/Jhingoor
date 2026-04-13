"""Auth route smoke tests (no database)."""

from fastapi.testclient import TestClient

from api.main import app


def test_forgot_password_accepted() -> None:
    client = TestClient(app)
    res = client.post("/api/v1/auth/forgot-password", json={"email": "nobody@example.com"})
    assert res.status_code == 202
    body = res.json()
    assert "message" in body


def test_signup_validation_error_on_short_password() -> None:
    client = TestClient(app)
    res = client.post(
        "/api/v1/auth/signup",
        json={"email": "a@b.com", "password": "short"},
    )
    assert res.status_code == 422
