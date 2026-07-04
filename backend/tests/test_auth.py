from datetime import datetime, timedelta, timezone

from jose import jwt

from app.config import get_settings


def _token(payload, secret=None, algorithm="HS256"):
    settings = get_settings()
    return jwt.encode(payload, secret or settings.auth_bridge_secret, algorithm=algorithm)


def test_valid_token_is_accepted(client, auth_headers):
    res = client.get("/api/me/saved", headers=auth_headers)
    assert res.status_code == 200


def test_missing_authorization_header_returns_401(client):
    res = client.get("/api/me/saved")
    assert res.status_code == 401
    assert res.json()["detail"] == "Missing bearer token"


def test_malformed_authorization_header_returns_401(client):
    res = client.get("/api/me/saved", headers={"Authorization": "NotBearer sometoken"})
    assert res.status_code == 401


def test_token_signed_with_wrong_secret_is_rejected(client):
    bad_token = _token({"sub": "user-123"}, secret="not-the-real-secret")
    res = client.get("/api/me/saved", headers={"Authorization": f"Bearer {bad_token}"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid or expired token"


def test_expired_token_is_rejected(client):
    expired = _token(
        {"sub": "user-123", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)}
    )
    res = client.get("/api/me/saved", headers={"Authorization": f"Bearer {expired}"})
    assert res.status_code == 401


def test_token_without_sub_claim_is_rejected(client):
    no_sub = _token({"email": "traveler@example.com"})
    res = client.get("/api/me/saved", headers={"Authorization": f"Bearer {no_sub}"})
    assert res.status_code == 401


def test_optional_auth_endpoint_works_anonymously(client):
    """/api/destinations only *optionally* authenticates -- no header should still succeed."""
    res = client.get("/api/destinations")
    assert res.status_code == 200


def test_optional_auth_endpoint_ignores_invalid_token_rather_than_rejecting(client):
    """Public endpoints shouldn't 401 just because a stale/bad token was attached."""
    res = client.get("/api/destinations", headers={"Authorization": "Bearer garbage"})
    assert res.status_code == 200
