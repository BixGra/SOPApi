from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, model_validator

from app.utils.errors import (
    MissingPayloadError,
    MissingTypeFieldError,
    UnknownTypeFieldError,
)

# Poll


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


# poll start


class PollStartOutput(BaseModel):
    poll_id: str


class PollStartOutput(BaseModel):
    type: Literal[PollOutputType.START]
    data: PollStartOutput


# poll get


class PollGetOutputData(BaseModel):
    poll_id: str
    title: str
    choices: list[Choice]
    status: PollStatus


class PollGetOutput(BaseModel):
    type: Literal[PollOutputType.GET]
    data: PollGetOutputData


# poll end


class PollEndOutputData(BaseModel):
    poll_id: str
    title: str
    choices: list[Choice]
    status: Literal[PollStatus.TERMINATED] | Literal[PollStatus.COMPLETED]


class PollEndOutput(BaseModel):
    type: Literal[PollOutputType.END]
    data: PollEndOutputData


# Global


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
        if isinstance(data, dict) and "payload" not in data:
            raise MissingPayloadError()
        if isinstance(data["payload"], dict) and "type" not in data["payload"]:
            raise MissingTypeFieldError()
        if data["payload"]["type"] not in WebSocketOutputType:
            raise UnknownTypeFieldError()
        return data
