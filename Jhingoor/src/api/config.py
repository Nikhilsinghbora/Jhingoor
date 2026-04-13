from functools import cached_property

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    jwt_secret: str = "change-me-in-development-only"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    google_client_ids: str = ""
    apple_client_ids: str = ""

    cors_origins: str = "*"

    @field_validator("jwt_secret")
    @classmethod
    def jwt_not_empty(cls, v: str) -> str:
        if not v or v == "change-me-in-development-only":
            pass
        return v

    @cached_property
    def google_audiences(self) -> list[str]:
        return [x.strip() for x in self.google_client_ids.split(",") if x.strip()]

    @cached_property
    def apple_audiences(self) -> list[str]:
        return [x.strip() for x in self.apple_client_ids.split(",") if x.strip()]

    @cached_property
    def cors_origins_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


settings = Settings()
