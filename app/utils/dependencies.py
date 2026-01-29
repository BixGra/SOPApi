import secrets
from typing import Callable, Generator

from fastapi.params import Depends
from fastapi.requests import HTTPConnection
from sqlalchemy.orm import Session

from app.crud.users import UsersCRUD
from app.utils.connection_manager import ConnectionManager, connection_manager
from app.utils.database import SessionLocal
from app.utils.errors import InvalidTokenError, UserNotFoundError
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


def get_get_token(
    twitch_client: TwitchClient = Depends(get_twitch_client),
    postgres_database: Session = Depends(get_postgres_database),
) -> Generator[Callable]:
    async def get_token(
        http_connexion: HTTPConnection,
    ) -> str | None:
        session_id = http_connexion.cookies.get("session_id")

        if not session_id:
            return

        try:
            users = UsersCRUD(postgres_database).get_user(session_id)
        except UserNotFoundError:
            return
        user = users[0]
        user_id = user.user_id
        token = user.token
        refresh_token = user.refresh_token
        try:
            await twitch_client.validate(token)
        except InvalidTokenError:
            token, refresh_token = await twitch_client.refresh(refresh_token)
            UsersCRUD(postgres_database).update_user(
                session_id=session_id,
                user_id=user_id,
                token=token,
                refresh_token=refresh_token,
            )
        return token

    yield get_token


def get_connection_manager() -> ConnectionManager:
    return connection_manager
