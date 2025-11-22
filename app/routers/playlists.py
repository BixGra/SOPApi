from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.crud.playlists import PlaylistsCRUD
from app.dependencies import get_postgres_database
from app.schemas.playlists import (
    GameMode,
    GetGameModeInput,
    GetPlaylistInput,
    GetPlaylistItemsInput,
    Playlist,
    PlaylistItem,
)

router = APIRouter(tags=["Playlists"], prefix="/playlists")


@router.get("/get-playlist")
async def get_playlist(
    get_playlist_input: Annotated[GetPlaylistInput, Query()],
    postgres_database: Session = Depends(get_postgres_database),
) -> list[Playlist]:
    return PlaylistsCRUD(postgres_database).get_playlist(get_playlist_input.id)


@router.get("/get-playlists")
async def get_playlists(
    postgres_database: Session = Depends(get_postgres_database),
) -> list[Playlist]:
    return PlaylistsCRUD(postgres_database).get_playlists()


@router.get("/get-playlist-items")
async def get_playlist_items(
    get_playlist_items_input: Annotated[GetPlaylistItemsInput, Query()],
    postgres_database: Session = Depends(get_postgres_database),
) -> list[PlaylistItem]:
    return PlaylistsCRUD(postgres_database).get_playlist_items(
        playlist_id=get_playlist_items_input.playlist_id,
    )


@router.get("/get-game-mode")
async def get_game_mode(
    get_game_mode_input: Annotated[GetGameModeInput, Query()],
    postgres_database: Session = Depends(get_postgres_database),
) -> list[GameMode]:
    return PlaylistsCRUD(postgres_database).get_game_mode(get_game_mode_input.id)


@router.get("/get-game-modes")
async def get_game_modes(
    postgres_database: Session = Depends(get_postgres_database),
) -> list[GameMode]:
    return PlaylistsCRUD(postgres_database).get_game_modes()
