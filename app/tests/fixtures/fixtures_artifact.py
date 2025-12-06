from typing import Generator

from fastapi.testclient import TestClient
from pytest import Session
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.utils.dependencies import (
    get_postgres_database,
    get_session_id,
    get_state,
    get_twitch_client,
)
from app.utils.twitch import TwitchClient

postgres_url = f"postgresql://postgres:postgres@127.0.0.1:5432/sopapi"
engine = create_engine(postgres_url, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TestTwitchClient(TwitchClient):
    async def callback(code: str) -> tuple[str, str, str]:
        # Always returns user3
        token = "token3"
        refresh_token = "refresh_token3"
        # expires_in = data["expires_in"]

        user_id = "3"

        return user_id, token, refresh_token

    async def is_token_valid(token: str, user_id: str) -> bool:
        return token == "token1"  # Only user1 is logged in with a valid token

    async def get_user(token: str, user_id: str) -> tuple[str, str]:
        username = f"{user_id}"
        email = f"user{user_id}@test.com"
        return username, email


def override_get_postgres_manager() -> Generator[Session]:
    try:
        postgres_database = TestingSessionLocal()
        yield postgres_database
    finally:
        postgres_database.close()


def override_get_state() -> str:
    return "12345678"


# TODO better session_id mock
def override_get_session_id() -> str:
    return "session_id3"


def override_get_twitch_client() -> Generator[TwitchClient]:
    yield TestTwitchClient


app.dependency_overrides[get_postgres_database] = override_get_postgres_manager
app.dependency_overrides[get_state] = override_get_state
app.dependency_overrides[get_session_id] = override_get_session_id
app.dependency_overrides[get_twitch_client] = override_get_twitch_client


client = TestClient(app)
