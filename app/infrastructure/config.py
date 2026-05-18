from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Travel Planner API"
    app_version: str = "1.0.0"

    database_url: str = ""
    artwork_api_base_url: str = "https://api.artic.edu/api/v1"
    artwork_cache_ttl: int = 3600

    enable_auth: bool = False
    auth_username: str = ""
    auth_password: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("database_url", "auth_username", "auth_password")
    @classmethod
    def must_be_set(cls, v: str) -> str:
        if not v:
            raise ValueError("must be set via environment variable or .env file")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
