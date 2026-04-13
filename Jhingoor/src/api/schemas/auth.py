from pydantic import BaseModel, EmailStr, Field


class SignupIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class GoogleAuthIn(BaseModel):
    id_token: str


class AppleAuthIn(BaseModel):
    identity_token: str
    nonce: str | None = None


class ForgotPasswordIn(BaseModel):
    email: EmailStr
