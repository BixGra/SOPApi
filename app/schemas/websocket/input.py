from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, model_validator

from app.utils.errors import (
    MissingPayloadError,
    MissingTypeFieldError,
    UnknownTypeFieldError,
)

# Poll


class PollInputType(str, Enum):
    START = "start"
    END = "end"
    GET = "get"


# poll start


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


# poll get


class PollGetInputData(BaseModel):
    poll_id: str


class PollGetInput(BaseModel):
    type: Literal[PollInputType.GET]
    data: PollGetInputData


# poll end


class PollEndInputData(BaseModel):
    poll_id: str


class PollEndInput(BaseModel):
    type: Literal[PollInputType.END]
    data: PollEndInputData


# Global


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
        if isinstance(data, dict) and "payload" not in data:
            raise MissingPayloadError()
        if isinstance(data["payload"], dict) and "type" not in data["payload"]:
            raise MissingTypeFieldError()
        if data["payload"]["type"] not in WebSocketInputType:
            raise UnknownTypeFieldError()
        return data
