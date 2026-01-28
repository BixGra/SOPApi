from typing import Generator

from pytest import Session
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from app.utils.errors import PollNotFoundError
from app.utils.twitch import TwitchClient

postgres_url = f"postgresql://postgres:postgres@127.0.0.1:5432/sopapi"
engine = create_engine(postgres_url, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class FakeTwitchClient(TwitchClient):
    async def callback(code: str) -> tuple[str, str, str, int]:
        # Always returns user3
        token = "token3"
        refresh_token = "refresh_token3"
        expires_in = 1234

        return token, refresh_token, expires_in

    async def validate(token: str) -> bool:
        return token if "expired" not in token else None

    async def get_user(token: str, user_id: str) -> tuple[str, str]:
        username = f"{user_id}"
        email = f"user{user_id}@test.com"
        return username, email

    async def get_poll(token: str, user_id: str, poll_id: str) -> dict:
        if poll_id != "poll1":
            raise PollNotFoundError()
        return {
            "poll_id": poll_id,
            "title": "title1",
            "choices": [
                {"title": "choice1", "votes": 1},
                {"title": "choice2", "votes": 2},
            ],
            "status": "ACTIVE",
        }

    async def end_poll(token: str, user_id: str, poll_id: str) -> dict:
        if poll_id != "poll1":
            raise PollNotFoundError()
        return {
            "poll_id": poll_id,
            "title": "title1",
            "choices": [
                {"title": "choice1", "votes": 1},
                {"title": "choice2", "votes": 2},
            ],
            "status": "TERMINATED",
        }

    # TODO custom duration
    async def create_poll(
        token: str, user_id: str, title: str, choices: list[str], duration: int = 60
    ) -> dict:
        return {"poll_id": "poll1"}


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
