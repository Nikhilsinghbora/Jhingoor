"""Verify Google and Apple identity tokens (OIDC)."""

from __future__ import annotations

import logging
from typing import Any

import jwt
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from jwt import PyJWKClient

from api.config import settings

logger = logging.getLogger(__name__)

_apple_jwk_client: PyJWKClient | None = None


def _apple_jwks() -> PyJWKClient:
    global _apple_jwk_client
    if _apple_jwk_client is None:
        _apple_jwk_client = PyJWKClient("https://appleid.apple.com/auth/keys")
    return _apple_jwk_client


def verify_google_id_token(token: str) -> dict[str, Any]:
    audiences = settings.google_audiences
    last_err: Exception | None = None
    if audiences:
        for aud in audiences:
            try:
                return google_id_token.verify_oauth2_token(
                    token, google_requests.Request(), audience=aud
                )
            except Exception as e:
                last_err = e
                continue
        if last_err:
            raise ValueError(f"Google token not accepted for configured audiences: {last_err}") from last_err

    unverified: dict[str, Any] = jwt.decode(token, options={"verify_signature": False})
    aud = unverified.get("aud")
    if isinstance(aud, list):
        aud = aud[0] if aud else None
    if not aud:
        raise ValueError("Google token missing audience")
    return google_id_token.verify_oauth2_token(
        token, google_requests.Request(), audience=str(aud)
    )


def verify_apple_identity_token(token: str, nonce: str | None = None) -> dict[str, Any]:
    audiences = settings.apple_audiences
    if not audiences:
        raise ValueError("APPLE_CLIENT_IDS must be set to verify Apple Sign In")

    signing_key = _apple_jwks().get_signing_key_from_jwt(token)
    decode_kwargs: dict[str, Any] = {
        "algorithms": ["RS256"],
        "issuer": "https://appleid.apple.com",
        "audience": audiences if len(audiences) > 1 else audiences[0],
    }
    payload = jwt.decode(token, signing_key.key, **decode_kwargs)
    if nonce and payload.get("nonce") != nonce:
        raise ValueError("Apple token nonce mismatch")
    return payload
