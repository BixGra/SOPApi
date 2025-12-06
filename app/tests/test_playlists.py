import pytest
from sqlalchemy import text

from app.models.playlists import GameModeBase, PlaylistBase, PlaylistItemBase
from app.tests.fixtures.fixtures_artifact import TestingSessionLocal, client


@pytest.fixture
def setup_data():
    # Setup
    postgres_database = TestingSessionLocal()
    playlists = postgres_database.query(PlaylistBase).all()
    for playlist in playlists:
        postgres_database.delete(playlist)
    postgres_database.execute(text('ALTER SEQUENCE "PLAYLISTS_id_seq" RESTART WITH 1;'))

    playlist_items = postgres_database.query(PlaylistItemBase).all()
    for playlist_item in playlist_items:
        postgres_database.delete(playlist_item)
    postgres_database.execute(
        text('ALTER SEQUENCE "PLAYLIST_ITEMS_id_seq" RESTART WITH 1;')
    )

    game_modes = postgres_database.query(GameModeBase).all()
    for game_mode in game_modes:
        postgres_database.delete(game_mode)
    postgres_database.execute(
        text('ALTER SEQUENCE "GAME_MODES_id_seq" RESTART WITH 1;')
    )

    postgres_database.commit()

    # Data

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
    postgres_database.add_all([playlist1, playlist2])

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
    postgres_database.add_all(
        [playlist_item1, playlist_item2, playlist_item3, playlist_item4]
    )

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
    postgres_database.add_all([game_mode1, game_mode2])

    postgres_database.commit()

    yield

    # Teardown
    playlists = postgres_database.query(PlaylistBase).all()
    for playlist in playlists:
        postgres_database.delete(playlist)
    postgres_database.execute(text('ALTER SEQUENCE "PLAYLISTS_id_seq" RESTART WITH 1;'))

    playlist_items = postgres_database.query(PlaylistItemBase).all()
    for playlist_item in playlist_items:
        postgres_database.delete(playlist_item)
    postgres_database.execute(
        text('ALTER SEQUENCE "PLAYLIST_ITEMS_id_seq" RESTART WITH 1;')
    )

    game_modes = postgres_database.query(GameModeBase).all()
    for game_mode in game_modes:
        postgres_database.delete(game_mode)
    postgres_database.execute(
        text('ALTER SEQUENCE "GAME_MODES_id_seq" RESTART WITH 1;')
    )

    postgres_database.commit()

    postgres_database.close()


# /playlists/get-playlists


def test_get_playlists(setup_data):
    response = client.get("/playlists/get-playlists")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "playlist 1"


# /playlists/get-playlist


def test_get_playlist(setup_data):
    response = client.get("/playlists/get-playlist?id=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "playlist 1"


def test_get_playlist_missing_query_parameters(setup_data):
    response = client.get("/playlists/get-playlist")
    assert response.status_code == 422


def test_get_playlist_not_found(setup_data):
    response = client.get("/playlists/get-playlist?id=9999")
    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "P01"


# /playlists/get-playlist-items


def test_get_playlist_items(setup_data):
    response = client.get("/playlists/get-playlist-items?playlist_id=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["url"] == "playlist item 1 url"


def test_get_playlist_items_missing_query_parameters(setup_data):
    response = client.get("/playlists/get-playlist-items")
    assert response.status_code == 422


def test_get_playlist_items_not_found(setup_data):
    response = client.get("/playlists/get-playlist-items?playlist_id=9999")
    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "P02"


# /playlists/get-game-modes


def test_get_game_modes(setup_data):
    response = client.get("/playlists/get-game-modes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "game mode 1"


# /playlists/get-game-mode


def test_get_game_mode(setup_data):
    response = client.get("/playlists/get-game-mode?id=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "game mode 1"


def test_get_game_modemissing_query_parameters(setup_data):
    response = client.get("/playlists/get-game-mode")
    assert response.status_code == 422


def test_get_game_modenot_found(setup_data):
    response = client.get("/playlists/get-game-mode?id=9999")
    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "P03"
