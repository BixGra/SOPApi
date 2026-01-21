import secrets
from typing import Callable, Generator

from fastapi.params import Depends
from fastapi.requests import HTTPConnection
from sqlalchemy.orm import Session

from app.crud.users import UsersCRUD
from app.schemas.users import IsLoggedIn
from app.utils.connection_manager import ConnectionManager, connection_manager
from app.utils.database import SessionLocal
from app.utils.errors import UserNotFoundError
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


def get_is_user_logged_in(
    twitch_client: TwitchClient = Depends(get_twitch_client),
    postgres_database: Session = Depends(get_postgres_database),
) -> Generator[Callable]:
    async def is_user_logged_in(
        http_connexion: HTTPConnection,
    ) -> IsLoggedIn:
        session_id = http_connexion.cookies.get("session_id")
        if not session_id:
            return {"is_logged_in": False}
        try:
            user = UsersCRUD(postgres_database).get_user(session_id)
            is_logged_in = await twitch_client.is_token_valid(
                user[0].token, user[0].user_id
            )
            return {"is_logged_in": is_logged_in}
        except UserNotFoundError:
            return {"is_logged_in": False}

    yield is_user_logged_in


def get_connection_manager() -> ConnectionManager:
    return connection_manager
