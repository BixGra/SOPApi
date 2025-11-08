from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.params import Depends

from app.schemas.playlist_schemas import (
    GameMode,
    GetPlaylistItemsInput,
    GetPlaylistInput,
    GetGameModeInput,
    Playlist,
    PlaylistItem,
)
from app.utils.dependencies import (
    PostgresManager,
    get_postgres_manager,
)


router = APIRouter(tags=["Playlist"], prefix="/playlist")


@router.get("/get-playlist")
async def get_playlist(
    get_playlist_input: Annotated[GetPlaylistInput, Query()],
    postgres_manager: PostgresManager = Depends(get_postgres_manager),
) -> list[Playlist]:
    results = postgres_manager.get_playlist(get_playlist_input.id)
    return postgres_manager.wrap(Playlist, results)


@router.get("/get-playlists")
async def get_playlists(
    postgres_manager: PostgresManager = Depends(get_postgres_manager),
) -> list[Playlist]:
    results = postgres_manager.get_playlists()
    return postgres_manager.wrap(Playlist, results)


@router.get("/get-playlist-items")
async def get_playlist_items(
    get_playlist_items_input: Annotated[GetPlaylistItemsInput, Query()],
    postgres_manager: PostgresManager = Depends(get_postgres_manager),
) -> list[PlaylistItem]:
    results = postgres_manager.get_playlist_items(
        playlist_id=get_playlist_items_input.playlist_id,
    )
    return postgres_manager.wrap(PlaylistItem, results)


@router.get("/get-game-mode")
async def get_game_mode(
    get_game_mode_input: Annotated[GetGameModeInput, Query()],
    postgres_manager: PostgresManager = Depends(get_postgres_manager),
) -> list[GameMode]:
    results = postgres_manager.get_game_mode(get_game_mode_input.id)
    return postgres_manager.wrap(GameMode, results)


@router.get("/get-game-modes")
async def get_game_modes(
    postgres_manager: PostgresManager = Depends(get_postgres_manager),
) -> list[GameMode]:
    results = postgres_manager.get_game_modes()
    return postgres_manager.wrap(GameMode, results)
