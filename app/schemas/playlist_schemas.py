from pydantic import BaseModel, ConfigDict


class Playlist(BaseModel):
    id: int
    title: str
    description: str
    field1: str
    field2: str
    model_config = ConfigDict(from_attributes=True)


class PlaylistItem(BaseModel):
    id: int
    playlist_id: int
    url: str
    field1: str
    field2: str
    model_config = ConfigDict(from_attributes=True)


class GameMode(BaseModel):
    id: int
    name: str
    description: str
    answer1: str
    answer2: str
    model_config = ConfigDict(from_attributes=True)


class GetPlaylistInput(BaseModel):
    id: int


class GetPlaylistItemsInput(BaseModel):
    playlist_id: int


class GetGameModeInput(BaseModel):
    id: int
