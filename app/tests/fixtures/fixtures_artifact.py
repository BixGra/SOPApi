from typing import Generator

from pytest import Session
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from app.utils.twitch import TwitchClient

postgres_url = f"postgresql://postgres:postgres@127.0.0.1:5432/sopapi"
engine = create_engine(postgres_url, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class FakeTwitchClient(TwitchClient):
    async def callback(code: str) -> tuple[str, str, str]:
        # Always returns user3
        token = "token3"
        refresh_token = "refresh_token3"
        # expires_in = data["expires_in"]

        user_id = "3"

        return user_id, token, refresh_token

    async def is_token_valid(token: str, user_id: str) -> bool:
        return "expired" not in token

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


fake_state = "12345678"


def override_get_state() -> str:
    return fake_state


fake_session_id = "session_id3"


def override_get_session_id() -> str:
    return fake_session_id


def override_get_twitch_client() -> Generator[TwitchClient]:
    yield FakeTwitchClient
