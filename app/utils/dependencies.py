import secrets
from typing import Generator

from sqlalchemy.orm import Session

from app.utils.database import SessionLocal
from app.utils.twitch import TwitchClient


def get_postgres_database() -> Generator[Session]:
    try:
        postgres_database = SessionLocal()
        yield postgres_database
    finally:
        postgres_database.close()


def get_state() -> str:
    return secrets.token_urlsafe(32)


def get_session_id() -> str:
    return secrets.token_urlsafe(32)


def get_twitch_client() -> Generator[TwitchClient]:
    yield TwitchClient()
