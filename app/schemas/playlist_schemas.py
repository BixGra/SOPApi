from pydantic import BaseModel


class Playlist(BaseModel):
    id: int
    title: str
    description: str
    field1: str
    field2: str


class PlaylistItem(BaseModel):
    id: int
    playlist_id: int
    url: str
    field1: str
    field2: str


class GameMode(BaseModel):
    id: int
    name: str
    description: str
    answer1: str
    answer2: str


class GetPlaylistItemsInput(BaseModel):
    playlist_id: int


class GetGameModeInput(BaseModel):
    id: int
