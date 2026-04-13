import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db
from api.schemas.auth import (
    AppleAuthIn,
    ForgotPasswordIn,
    GoogleAuthIn,
    LoginIn,
    SignupIn,
    TokenOut,
)
from api.schemas.common import MessageOut
from api.services import auth_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenOut)
async def signup(body: SignupIn, db: AsyncSession = Depends(get_db)) -> TokenOut:
    user = await auth_service.signup_user(db, body.email, body.password)
    token = auth_service.issue_token(user)
    return TokenOut(access_token=token)


@router.post("/login", response_model=TokenOut)
async def login(body: LoginIn, db: AsyncSession = Depends(get_db)) -> TokenOut:
    user = await auth_service.login_user(db, body.email, body.password)
    token = auth_service.issue_token(user)
    return TokenOut(access_token=token)


@router.post("/google", response_model=TokenOut)
async def google_auth(body: GoogleAuthIn, db: AsyncSession = Depends(get_db)) -> TokenOut:
    user = await auth_service.login_or_register_google(db, body.id_token)
    token = auth_service.issue_token(user)
    return TokenOut(access_token=token)


@router.post("/apple", response_model=TokenOut)
async def apple_auth(body: AppleAuthIn, db: AsyncSession = Depends(get_db)) -> TokenOut:
    user = await auth_service.login_or_register_apple(db, body.identity_token, body.nonce)
    token = auth_service.issue_token(user)
    return TokenOut(access_token=token)


@router.post("/forgot-password", status_code=202)
async def forgot_password(body: ForgotPasswordIn) -> MessageOut:
    logger.info("Password reset requested for %s (no email provider configured)", body.email)
    return MessageOut(message="If an account exists for this email, reset instructions will be sent.")
