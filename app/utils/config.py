from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_user: str
    postgres_secret: str
    postgres_host: str
    postgres_db: str
    environment: Optional[str] = "production"
    model_config = SettingsConfigDict(extra="ignore")


@lru_cache()
def get_settings():
    return Settings()
