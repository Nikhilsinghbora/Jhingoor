from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.errors import unauthorized
from api.security import parse_subject_uuid
from database.models import User
from database.session import AsyncSessionLocal

security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: DbSession,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> User:
    if not creds or creds.scheme.lower() != "bearer":
        raise unauthorized()
    uid = parse_subject_uuid(creds.credentials)
    if not uid:
        raise unauthorized("Invalid token")
    res = await db.execute(select(User).where(User.id == uid).where(User.is_active.is_(True)))
    user = res.scalar_one_or_none()
    if not user:
        raise unauthorized("User not found")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
