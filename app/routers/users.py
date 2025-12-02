from typing import Annotated

from fastapi import APIRouter, Query, Request
from fastapi.params import Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.crud.users import UsersCRUD
from app.schemas.users import GetUserInput, IsLoggedIn, User
from app.utils.config import get_settings
from app.utils.dependencies import get_postgres_database, get_state, get_twitch_client
from app.utils.errors import BaseError, PotentialCSRFError, UserNotFoundError
from app.utils.twitch import TwitchClient

router = APIRouter(tags=["Users"], prefix="/users")


@router.get("/is-logged-in")
async def is_logged_in(
    request: Request,
    twitch_client: TwitchClient = Depends(get_twitch_client),
    postgres_database: Session = Depends(get_postgres_database),
) -> IsLoggedIn:
    user_id = request.cookies.get("user_id")
    if not user_id:
        return {"is_logged_in": False}
    try:
        user = UsersCRUD(postgres_database).get_user(user_id)
        is_logged_in = await twitch_client.is_token_valid(user[0].token, user_id)
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
    error: str = None,
    code: str = None,
    state: str = "",
    twitch_client: TwitchClient = Depends(get_twitch_client),
    postgres_database: Session = Depends(get_postgres_database),
) -> RedirectResponse:
    if error:
        raise BaseError("callback error")
    if not state:
        raise BaseError("state missing error")
    if not request.cookies.get("state") == state:
        raise PotentialCSRFError
    user_id, token, refresh_token = await twitch_client.callback(code)
    username, email = await twitch_client.get_user(token, user_id)
    if UsersCRUD(postgres_database).exists_user(user_id):
        user = UsersCRUD(postgres_database).update_user(
            user_id=user_id,
            token=token,
            refresh_token=refresh_token,
        )
    else:
        user = UsersCRUD(postgres_database).create_user(
            user_id=user_id,
            email=email,
            username=username,
            token=token,
            refresh_token=refresh_token,
        )
    response = RedirectResponse(f"{get_settings().front_base_url}/callback")
    response.set_cookie(key="token", value=token, domain=get_settings().cookie_domain)
    response.set_cookie(
        key="user_id", value=user_id, domain=get_settings().cookie_domain
    )
    return response


@router.get("/logout")
async def logout():
    return


@router.get("/get-user")
async def get_user(
    get_user_input: Annotated[GetUserInput, Query()],
    postgres_database: Session = Depends(get_postgres_database),
) -> User:
    return UsersCRUD(postgres_database).get_user(get_user_input.user_id)[0]
