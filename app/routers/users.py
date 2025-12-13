from typing import Annotated

from fastapi import APIRouter, Query, Request
from fastapi.params import Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.crud.users import UsersCRUD
from app.schemas.users import CallbackInput, GetUserInput, IsLoggedIn, User
from app.utils.config import get_settings
from app.utils.dependencies import (
    get_postgres_database,
    get_session_id,
    get_state,
    get_twitch_client,
)
from app.utils.errors import (
    NoSessionError,
    PotentialCSRFError,
    TwitchCallbackError,
    TwitchStatesError,
    UserNotFoundError,
)
from app.utils.twitch import TwitchClient

router = APIRouter(tags=["Users"], prefix="/users")


@router.get("/is-logged-in")
async def is_logged_in(
    request: Request,
    twitch_client: TwitchClient = Depends(get_twitch_client),
    postgres_database: Session = Depends(get_postgres_database),
) -> IsLoggedIn:
    session_id = request.cookies.get("session_id")
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


@router.get("/login")
async def login(
    state: str = Depends(get_state),
    twitch_client: TwitchClient = Depends(get_twitch_client),
) -> RedirectResponse:
    response = RedirectResponse(twitch_client.get_authorization_url(state))
    response.set_cookie(key="state", value=state, domain=get_settings().cookie_domain)
    return response


@router.get("/callback")
async def callback(
    request: Request,
    callback_input: Annotated[CallbackInput, Query()],
    session_id: str = Depends(get_session_id),
    twitch_client: TwitchClient = Depends(get_twitch_client),
    postgres_database: Session = Depends(get_postgres_database),
) -> RedirectResponse:
    if callback_input.error:
        raise TwitchCallbackError
    if not callback_input.state:
        raise TwitchStatesError
    if not request.cookies.get("state") == callback_input.state:
        raise PotentialCSRFError
    user_id, token, refresh_token = await twitch_client.callback(callback_input.code)
    username, email = await twitch_client.get_user(token, user_id)
    if UsersCRUD(postgres_database).exists_user(user_id):
        UsersCRUD(postgres_database).update_user(
            user_id=user_id,
            token=token,
            refresh_token=refresh_token,
            session_id=session_id,
        )
    else:
        UsersCRUD(postgres_database).create_user(
            user_id=user_id,
            email=email,
            username=username,
            token=token,
            refresh_token=refresh_token,
            session_id=session_id,
        )
    response = RedirectResponse(f"{get_settings().front_base_url}/callback")
    response.set_cookie(
        key="session_id", value=session_id, domain=get_settings().cookie_domain
    )
    return response


@router.get("/logout")
async def logout(
    request: Request,
    postgres_database: Session = Depends(get_postgres_database),
):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise NoSessionError
    user = UsersCRUD(postgres_database).get_user(session_id)
    UsersCRUD(postgres_database).update_user(
        user_id=user[0].user_id,
        token="",
        refresh_token="",
        session_id="",
    )
    return


@router.get("/get-user")
async def get_user(
    get_user_input: Annotated[GetUserInput, Query()],
    postgres_database: Session = Depends(get_postgres_database),
) -> User:
    return UsersCRUD(postgres_database).get_user(get_user_input.session_id)[0]
