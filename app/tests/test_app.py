import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.dependencies import get_postgres_database
from app.main import app
from app.models.playlists import GameModeBase, PlaylistBase, PlaylistItemBase

postgres_url = f"postgresql://postgres:postgres@127.0.0.1:5432/sopapi"
engine = create_engine(postgres_url, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_postgres_manager():
    try:
        postgres_database = TestingSessionLocal()
        yield postgres_database
    finally:
        postgres_database.close()


app.dependency_overrides[get_postgres_database] = override_get_postgres_manager


@pytest.fixture
def setup_data():
    # Setup
    postgres_database = TestingSessionLocal()

    playlist_1 = PlaylistBase(
        title="playlist 1",
        description="description 1",
        field1="field1_1",
        field2="field2_1",
    )
    playlist_2 = PlaylistBase(
        title="playlist 2",
        description="description 2",
        field1="field1_2",
        field2="field2_2",
    )
    postgres_database.add_all([playlist_1, playlist_2])

    playlist_item_1 = PlaylistItemBase(
        playlist_id=1,
        url="playlist item 1 url",
        field1="field1_1",
        field2="field2_1",
    )
    playlist_item_2 = PlaylistItemBase(
        playlist_id=1,
        url="playlist item 2 url",
        field1="field1_2",
        field2="field2_2",
    )
    playlist_item_3 = PlaylistItemBase(
        playlist_id=2,
        url="playlist item 3 url",
        field1="field1_3",
        field2="field2_3",
    )
    playlist_item_4 = PlaylistItemBase(
        playlist_id=2,
        url="playlist item 4 url",
        field1="field1_4",
        field2="field2_4",
    )
    postgres_database.add_all(
        [playlist_item_1, playlist_item_2, playlist_item_3, playlist_item_4]
    )

    game_mode_1 = GameModeBase(
        name="game mode 1",
        description="description 1",
        answer1="answer1_1",
        answer2="answer2_1",
    )
    game_mode_2 = GameModeBase(
        name="game mode 2",
        description="description 2",
        answer1="answer1_2",
        answer2="answer2_2",
    )
    postgres_database.add_all([game_mode_1, game_mode_2])

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


client = TestClient(app)


# /


def test_get_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "SOP Api"


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


def test_get_game_mode_missing_query_parameters(setup_data):
    response = client.get("/playlists/get-game-mode")
    assert response.status_code == 422


def test_get_game_mode_not_found(setup_data):
    response = client.get("/playlists/get-game-mode?id=9999")
    assert response.status_code == 404
