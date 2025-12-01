from datetime import datetime

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    user_id: str
    email: str
    username: str
    token: str
    refresh_token: str
    # expires_at: datetime
    model_config = ConfigDict(from_attributes=True)


class IsLoggedIn(BaseModel):
    is_logged_in: bool
    model_config = ConfigDict(from_attributes=True)


class GetUserInput(BaseModel):
    user_id: str
