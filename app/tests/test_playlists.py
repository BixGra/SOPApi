from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.models.playlists import GameModeBase, PlaylistBase, PlaylistItemBase
from app.tests.fixtures.fixtures_artifact import (
    TestingSessionLocal,
    override_get_postgres_manager,
)
from app.tests.fixtures.fixtures_classes import (
    FixtureGameMode,
    FixtureGameModes,
    FixturePlaylist,
    FixturePlaylistItem,
    FixturePlaylistItems,
    FixturePlaylists,
    FixturePlaylistsItems,
)
from app.utils.dependencies import get_postgres_database

app.dependency_overrides[get_postgres_database] = override_get_postgres_manager


client = TestClient(app)


@pytest.fixture
def playlists() -> list[PlaylistBase]:
    playlist1 = PlaylistBase(
        title="playlist 1",
        description="description 1",
        field1="field1_1",
        field2="field2_1",
    )
    playlist2 = PlaylistBase(
        title="playlist 2",
        description="description 2",
        field1="field1_2",
        field2="field2_2",
    )
    return [playlist1, playlist2]


@pytest.fixture
def setup_playlists(playlists) -> Generator[FixturePlaylists]:
    # Clean
    postgres_database = TestingSessionLocal()
    playlists_to_clean = postgres_database.query(PlaylistBase).all()
    for playlist in playlists_to_clean:
        postgres_database.delete(playlist)
    postgres_database.execute(text('ALTER SEQUENCE "PLAYLISTS_id_seq" RESTART WITH 1;'))
    postgres_database.commit()

    # Setup
    postgres_database.add_all(playlists)
    postgres_database.commit()
    for playlist in playlists:
        postgres_database.refresh(playlist)

    fixture_playlists = [
        FixturePlaylist(
            id_=playlist.id,
            title=playlist.title,
            description=playlist.description,
            field1=playlist.field1,
            field2=playlist.field2,
        )
        for playlist in playlists
    ]
    yield FixturePlaylists(playlists=fixture_playlists)

    # Teardown
    playlists_to_clean = postgres_database.query(PlaylistBase).all()
    for playlist in playlists_to_clean:
        postgres_database.delete(playlist)
    postgres_database.execute(text('ALTER SEQUENCE "PLAYLISTS_id_seq" RESTART WITH 1;'))
    postgres_database.commit()
    postgres_database.close()


@pytest.fixture
def playlists_items() -> list[list[PlaylistItemBase]]:
    playlist_item1 = PlaylistItemBase(
        playlist_id=1,
        url="playlist item 1 url",
        field1="field1_1",
        field2="field2_1",
    )
    playlist_item2 = PlaylistItemBase(
        playlist_id=1,
        url="playlist item 2 url",
        field1="field1_2",
        field2="field2_2",
    )
    playlist_item3 = PlaylistItemBase(
        playlist_id=2,
        url="playlist item 3 url",
        field1="field1_3",
        field2="field2_3",
    )
    playlist_item4 = PlaylistItemBase(
        playlist_id=2,
        url="playlist item 4 url",
        field1="field1_4",
        field2="field2_4",
    )
    return [
        [playlist_item1, playlist_item2],
        [playlist_item3, playlist_item4],
    ]


@pytest.fixture
def setup_playlists_items(playlists_items) -> Generator[FixturePlaylistsItems]:
    # Clean
    postgres_database = TestingSessionLocal()
    playlist_items_to_clean = postgres_database.query(PlaylistItemBase).all()
    for playlist_item in playlist_items_to_clean:
        postgres_database.delete(playlist_item)
    postgres_database.execute(
        text('ALTER SEQUENCE "PLAYLIST_ITEMS_id_seq" RESTART WITH 1;')
    )
    postgres_database.commit()

    # Setup
    for playlist_items in playlists_items:
        postgres_database.add_all(playlist_items)
        postgres_database.commit()
        for playlist_item in playlist_items:
            postgres_database.refresh(playlist_item)

    fixture_playlists_items = [
        [
            FixturePlaylistItem(
                id_=playlist_item.id,
                playlist_id=playlist_item.playlist_id,
                url=playlist_item.url,
                field1=playlist_item.field1,
                field2=playlist_item.field2,
            )
            for playlist_item in playlist_items
        ]
        for playlist_items in playlists_items
    ]
    fixture_playlists_items = [
        FixturePlaylistItems(playlist_items=fixture_playlist_items)
        for fixture_playlist_items in fixture_playlists_items
    ]
    yield FixturePlaylistsItems(playlists_items=fixture_playlists_items)

    # Teardown
    playlist_items_to_clean = postgres_database.query(PlaylistBase).all()
    for playlist in playlist_items_to_clean:
        postgres_database.delete(playlist)
        postgres_database.execute(
            text('ALTER SEQUENCE "PLAYLIST_ITEMS_id_seq" RESTART WITH 1;')
        )
    postgres_database.commit()
    postgres_database.close()


@pytest.fixture
def game_modes() -> list[GameModeBase]:
    game_mode1 = GameModeBase(
        name="game mode 1",
        description="description 1",
        answer1="answer1_1",
        answer2="answer2_1",
    )
    game_mode2 = GameModeBase(
        name="game mode 2",
        description="description 2",
        answer1="answer1_2",
        answer2="answer2_2",
    )
    return [game_mode1, game_mode2]


@pytest.fixture
def setup_game_modes(game_modes) -> Generator[FixtureGameModes]:
    # Clean
    postgres_database = TestingSessionLocal()
    game_modes_to_clean = postgres_database.query(GameModeBase).all()
    for game_mode in game_modes_to_clean:
        postgres_database.delete(game_mode)
    postgres_database.execute(
        text('ALTER SEQUENCE "GAME_MODES_id_seq" RESTART WITH 1;')
    )
    postgres_database.commit()

    # Setup
    postgres_database.add_all(game_modes)
    postgres_database.commit()
    for game_mode in game_modes:
        postgres_database.refresh(game_mode)

    fixture_game_modes = [
        FixtureGameMode(
            id_=game_mode.id,
            name=game_mode.name,
            description=game_mode.description,
            answer1=game_mode.answer1,
            answer2=game_mode.answer2,
        )
        for game_mode in game_modes
    ]
    yield FixtureGameModes(fixture_game_modes)

    # Teardown
    game_modes_to_clean = postgres_database.query(GameModeBase).all()
    for game_mode in game_modes_to_clean:
        postgres_database.delete(game_mode)
    postgres_database.execute(
        text('ALTER SEQUENCE "GAME_MODES_id_seq" RESTART WITH 1;')
    )
    postgres_database.commit()
    postgres_database.close()


# /playlists/get-playlists


def test_get_playlists_ok(setup_playlists):
    response = client.get("/playlists/get-playlists")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(setup_playlists)
    assert data[0]["title"] == setup_playlists.playlist1.title


# /playlists/get-playlist


def test_get_playlist_ok(setup_playlists):
    response = client.get(f"/playlists/get-playlist?id={setup_playlists.playlist1.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == setup_playlists.playlist1.title


def test_get_playlist_missing_query_parameters_returns_422(setup_playlists):
    response = client.get("/playlists/get-playlist")
    assert response.status_code == 422


def test_get_playlist_not_found_returns_404(setup_playlists):
    response = client.get("/playlists/get-playlist?id=9999")
    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "P01"


# /playlists/get-playlist-items


def test_get_playlist_items_ok(setup_playlists_items):
    response = client.get(
        f"/playlists/get-playlist-items?playlist_id={setup_playlists_items.playlist1_items.playlist_item1.id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(setup_playlists_items.playlist1_items)
    assert data[0]["url"] == setup_playlists_items.playlist1_items.playlist_item1.url


def test_get_playlist_items_missing_query_parameters_returns_422(setup_playlists_items):
    response = client.get("/playlists/get-playlist-items")
    assert response.status_code == 422


def test_get_playlist_items_not_found_returns_404(setup_playlists_items):
    response = client.get("/playlists/get-playlist-items?playlist_id=9999")
    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "P02"


# /playlists/get-game-modes


def test_get_game_modes_ok(setup_game_modes):
    response = client.get("/playlists/get-game-modes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(setup_game_modes)
    assert data[0]["name"] == setup_game_modes.game_mode1.name


# /playlists/get-game-mode


def test_get_game_mode_ok(setup_game_modes):
    response = client.get(
        f"/playlists/get-game-mode?id={setup_game_modes.game_mode1.id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == setup_game_modes.game_mode1.name


def test_get_game_mode_missing_query_parameters_returns_422(setup_game_modes):
    response = client.get("/playlists/get-game-mode")
    assert response.status_code == 422


def test_get_game_mode_not_foundreturns_404(setup_game_modes):
    response = client.get("/playlists/get-game-mode?id=9999")
    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "P03"
