from typing import Callable

from fastapi import APIRouter, WebSocket
from fastapi.params import Depends
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.crud.users import UsersCRUD
from app.schemas.websocket import PollInputType, WebSocketInput, WebSocketInputType
from app.utils.connection_manager import ConnectionManager
from app.utils.dependencies import (
    get_connection_manager,
    get_is_user_logged_in,
    get_postgres_database,
    get_twitch_client,
)
from app.utils.errors import (
    IncorrectPayloadError,
    IncorrectWebsocketInputError,
    MissingPayloadError,
    MissingTypeFieldError,
    NotLoggedInError,
    PollNotFoundError,
    UnknownTypeFieldError,
)
from app.utils.twitch import TwitchClient

router = APIRouter(tags=["Websocket"], prefix="/websocket")


@router.websocket("/connect")
async def connect_websocket(
    websocket: WebSocket,
    twitch_client: TwitchClient = Depends(get_twitch_client),
    postgres_database: Session = Depends(get_postgres_database),
    is_user_logged_in: Callable = Depends(get_is_user_logged_in),
    connection_manager: ConnectionManager = Depends(get_connection_manager),
):
    is_logged_in = await is_user_logged_in(websocket)
    if not is_logged_in["is_logged_in"]:
        raise NotLoggedInError()

    session_id = websocket.cookies.get("session_id")
    user = UsersCRUD(postgres_database).get_user(session_id)[0]

    await connection_manager.connect(session_id, websocket)

    alive = True
    while alive:
        data = await websocket.receive_json()
        try:
            data = WebSocketInput.model_validate(data)
        except IncorrectWebsocketInputError:
            payload = IncorrectWebsocketInputError().json()
            await connection_manager.send_json(session_id, payload)
        except MissingPayloadError:
            payload = MissingPayloadError().json()
            await connection_manager.send_json(session_id, payload)
        except MissingTypeFieldError:
            payload = MissingTypeFieldError().json()
            await connection_manager.send_json(session_id, payload)
        except UnknownTypeFieldError:
            payload = UnknownTypeFieldError().json()
            await connection_manager.send_json(session_id, payload)
        except ValidationError:
            payload = IncorrectPayloadError().json()
            await connection_manager.send_json(session_id, payload)
        else:
            payload = data.payload
            match payload.type:
                case WebSocketInputType.DISCONNECT:
                    alive = False
                    await connection_manager.send_json(
                        session_id,
                        {
                            "type": "connection_status",
                            "status": "disconnected",
                        },
                    )
                    await connection_manager.disconnect(session_id)
                case WebSocketInputType.POLL:
                    match payload.data.type:
                        case PollInputType.START:
                            poll = await twitch_client.create_poll(
                                token=user.token,
                                user_id=user.user_id,
                                title=payload.data.data.title,
                                choices=payload.data.data.choices,
                            )
                            await connection_manager.send_json(
                                session_id,
                                {
                                    "type": "poll",
                                    "data": {
                                        "type": "start",
                                        "data": poll,
                                    },
                                },
                            )
                        case PollInputType.GET:
                            try:
                                poll = await twitch_client.get_poll(
                                    token=user.token,
                                    user_id=user.user_id,
                                    poll_id=payload.data.data.poll_id,
                                )
                            except PollNotFoundError:
                                await connection_manager.send_json(
                                    session_id, PollNotFoundError().json()
                                )
                            else:
                                await connection_manager.send_json(
                                    session_id,
                                    {
                                        "type": "poll",
                                        "data": {
                                            "type": "get",
                                            "data": poll,
                                        },
                                    },
                                )
                        case PollInputType.END:
                            try:
                                poll = await twitch_client.end_poll(
                                    token=user.token,
                                    user_id=user.user_id,
                                    poll_id=payload.data.data.poll_id,
                                )

                            except PollNotFoundError:
                                await connection_manager.send_json(
                                    session_id, PollNotFoundError().json()
                                )
                            else:
                                await connection_manager.send_json(
                                    session_id,
                                    {
                                        "type": "poll",
                                        "data": {
                                            "type": "end",
                                            "data": poll,
                                        },
                                    },
                                )
