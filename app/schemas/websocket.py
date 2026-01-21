from enum import Enum
from typing import Annotated, Any, Literal

from fastapi import WebSocket
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.utils.errors import (
    IncorrectWebsocketInputError,
    IncorrectWebsocketOutputError,
    MissingPayloadError,
    MissingTypeFieldError,
    UnknownTypeFieldError,
)

# MARK: -MANAGER


class ActiveConnection(BaseModel):
    websocket: WebSocket
    last_seen: float
    model_config = ConfigDict(arbitrary_types_allowed=True)


# MARK: -INPUT - Poll


class PollInputType(str, Enum):
    START = "start"
    END = "end"
    GET = "get"


# MARK: Poll - Start


class PollStartInputData(BaseModel):
    title: str = Field(max_length=60)
    # Between 2 and 5 choices
    # Choices length of 25 chars max
    choices: list[Annotated[str, Field(max_length=25)]] = Field(
        min_length=2, max_length=5
    )
    duration: int = Field(60, ge=15, le=1800)


class PollStartInput(BaseModel):
    type: Literal[PollInputType.START]
    data: PollStartInputData


# MARK: Poll - Get


class PollGetInputData(BaseModel):
    poll_id: str


class PollGetInput(BaseModel):
    type: Literal[PollInputType.GET]
    data: PollGetInputData


# MARK: Poll - End


class PollEndInputData(BaseModel):
    poll_id: str


class PollEndInput(BaseModel):
    type: Literal[PollInputType.END]
    data: PollEndInputData


# MARK: Global


class WebSocketInputType(str, Enum):
    DISCONNECT = "disconnect"
    POLL = "poll"


class DisconnectInput(BaseModel):
    type: Literal[WebSocketInputType.DISCONNECT]


class PollInput(BaseModel):
    type: Literal[WebSocketInputType.POLL]
    data: PollStartInput | PollEndInput | PollGetInput


class WebSocketInput(BaseModel):
    payload: DisconnectInput | PollInput

    @model_validator(mode="before")
    @classmethod
    def check_type(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            raise IncorrectWebsocketInputError()
        if isinstance(data, dict) and not (payload := data.get("payload")):
            raise MissingPayloadError()
        if isinstance(payload, dict) and not (payload_type := payload.get("type")):
            raise MissingTypeFieldError()
        if payload_type not in WebSocketInputType:
            raise UnknownTypeFieldError()
        return data


# MARK: -OUTPUT - Poll


class PollOutputType(str, Enum):
    START = "start"
    END = "end"
    GET = "get"


class PollStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    TERMINATED = "TERMINATED"
    ARCHIVED = "ARCHIVED"
    MODERATED = "MODERATED"
    INVALID = "INVALID"


class Choice(BaseModel):
    title: str
    votes: int


# MARK: Poll - Start


class PollStartOutputData(BaseModel):
    poll_id: str


class PollStartOutput(BaseModel):
    type: Literal[PollOutputType.START]
    data: PollStartOutputData


# MARK: Poll - Get


class PollGetOutputData(BaseModel):
    poll_id: str
    title: str
    choices: list[Choice]
    status: PollStatus


class PollGetOutput(BaseModel):
    type: Literal[PollOutputType.GET]
    data: PollGetOutputData


# MARK: Poll - End


class PollEndOutputData(BaseModel):
    poll_id: str
    title: str
    choices: list[Choice]
    status: Literal[PollStatus.TERMINATED] | Literal[PollStatus.COMPLETED]


class PollEndOutput(BaseModel):
    type: Literal[PollOutputType.END]
    data: PollEndOutputData


# MARK: Global


class WebSocketOutputType(str, Enum):
    CONNECTION_STATUS = "connection_status"
    POLL = "poll"
    ERROR = "error"


class ConnectionStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


class ConnectionStatusOutput(BaseModel):
    type: Literal[WebSocketOutputType.CONNECTION_STATUS]
    status: ConnectionStatus


class ErrorOutput(BaseModel):
    type: Literal[WebSocketOutputType.ERROR]
    error_code: str
    status_code: int
    title: str


class PollOutput(BaseModel):
    type: Literal[WebSocketOutputType.POLL]
    data: PollStartOutput | PollGetOutput | PollEndOutput


class WebSocketOutput(BaseModel):
    payload: ConnectionStatusOutput | ErrorOutput | PollOutput

    @model_validator(mode="before")
    @classmethod
    def check_type(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            raise IncorrectWebsocketOutputError()
        if isinstance(data, dict) and not (payload := data.get("payload")):
            raise MissingPayloadError()
        if isinstance(payload, dict) and not (payload_type := payload.get("type")):
            raise MissingTypeFieldError()
        if payload_type not in WebSocketOutputType:
            raise UnknownTypeFieldError()
        return data
