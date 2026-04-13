from __future__ import annotations

import logging
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.errors import bad_request, conflict, unauthorized
from api.oauth_provider import verify_apple_identity_token, verify_google_id_token
from api.security import create_access_token, hash_password, verify_password
from database.models import OAuthAccount, User, UserProfile

logger = logging.getLogger(__name__)


async def signup_user(db: AsyncSession, email: str, password: str) -> User:
    existing = await db.execute(select(User).where(User.email == email.lower()))
    if existing.scalar_one_or_none():
        raise conflict("Email already registered")
    user = User(id=uuid4(), email=email.lower(), password_hash=hash_password(password))
    db.add(user)
    db.add(UserProfile(user_id=user.id))
    await db.commit()
    await db.refresh(user)
    return user


async def login_user(db: AsyncSession, email: str, password: str) -> User:
    res = await db.execute(select(User).where(User.email == email.lower()))
    user = res.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise unauthorized("Invalid email or password")
    return user


def issue_token(user: User) -> str:
    return create_access_token(user.id)


async def login_or_register_google(db: AsyncSession, id_token: str) -> User:
    try:
        claims = verify_google_id_token(id_token)
    except Exception as e:
        logger.info("Google verify failed: %s", e)
        raise bad_request("Invalid Google token") from e
    sub = claims.get("sub")
    email = (claims.get("email") or "").lower() or None
    if not sub:
        raise bad_request("Google token missing subject")

    res = await db.execute(
        select(OAuthAccount).where(OAuthAccount.provider == "google", OAuthAccount.provider_user_id == sub)
    )
    link = res.scalar_one_or_none()
    if link:
        u = await db.get(User, link.user_id)
        if not u:
            raise bad_request("Linked user missing")
        return u

    if email:
        res2 = await db.execute(select(User).where(User.email == email))
        existing = res2.scalar_one_or_none()
        if existing:
            db.add(OAuthAccount(user_id=existing.id, provider="google", provider_user_id=sub))
            await db.commit()
            return existing

    user = User(
        id=uuid4(),
        email=email or f"google_{sub[:40]}@id.jhingoor.app",
        password_hash=None,
    )
    db.add(user)
    db.add(UserProfile(user_id=user.id))
    db.add(OAuthAccount(user_id=user.id, provider="google", provider_user_id=sub))
    await db.commit()
    await db.refresh(user)
    return user


async def login_or_register_apple(db: AsyncSession, identity_token: str, nonce: str | None) -> User:
    try:
        claims = verify_apple_identity_token(identity_token, nonce=nonce)
    except ValueError as e:
        raise bad_request(str(e)) from e
    except Exception as e:
        logger.info("Apple verify failed: %s", e)
        raise bad_request("Invalid Apple token") from e

    sub = claims.get("sub")
    if not sub:
        raise bad_request("Apple token missing subject")

    res = await db.execute(
        select(OAuthAccount).where(OAuthAccount.provider == "apple", OAuthAccount.provider_user_id == sub)
    )
    link = res.scalar_one_or_none()
    if link:
        u = await db.get(User, link.user_id)
        if not u:
            raise bad_request("Linked user missing")
        return u

    email = claims.get("email")
    if isinstance(email, str) and email:
        email = email.lower()
        res2 = await db.execute(select(User).where(User.email == email))
        existing = res2.scalar_one_or_none()
        if existing:
            db.add(OAuthAccount(user_id=existing.id, provider="apple", provider_user_id=sub))
            await db.commit()
            return existing

    placeholder_email = f"apple_{sub[:36]}@id.jhingoor.app"
    user = User(id=uuid4(), email=placeholder_email, password_hash=None)
    db.add(user)
    db.add(UserProfile(user_id=user.id))
    db.add(OAuthAccount(user_id=user.id, provider="apple", provider_user_id=sub))
    await db.commit()
    await db.refresh(user)
    return user
