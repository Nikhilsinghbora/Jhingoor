from uuid import uuid4

from api.security import create_access_token, hash_password, parse_subject_uuid, verify_password


def test_password_hash_roundtrip() -> None:
    h = hash_password("MySecurePass123!")
    assert verify_password("MySecurePass123!", h)
    assert not verify_password("wrong", h)
    assert not verify_password("x", None)


def test_jwt_roundtrip() -> None:
    uid = uuid4()
    token = create_access_token(uid)
    parsed = parse_subject_uuid(token)
    assert parsed == uid
