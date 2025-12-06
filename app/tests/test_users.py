import pytest

from app.models.users import UserBase
from app.tests.fixtures.fixtures_artifact import TestingSessionLocal, client
from app.utils.config import get_settings
from app.utils.twitch import authorization_base_url, redirect_uri, response_type, scope


@pytest.fixture
def setup_data():
    # Setup
    postgres_database = TestingSessionLocal()
    users = postgres_database.query(UserBase).all()
    for user in users:
        postgres_database.delete(user)

    # Data

    # Logged in user, working token
    user1 = UserBase(
        user_id="1",
        email="user1@test.com",
        username="user1",
        token="token1",
        refresh_token="refresh_token1",
        session_id="session_id1",
    )
    # Logged in user, expired token
    user2 = UserBase(
        user_id="2",
        email="user2@test.com",
        username="user2",
        token="token2",
        refresh_token="refresh_token2",
        session_id="session_id2",
    )
    postgres_database.add_all([user1, user2])
    postgres_database.commit()

    yield

    # Teardown
    users = postgres_database.query(UserBase).all()
    for user in users:
        postgres_database.delete(user)
    postgres_database.commit()
    postgres_database.close()


# /users/is-logged-in


def test_is_logged_in_no_cookies(setup_data):
    response = client.get("/users/is-logged-in")
    assert response.status_code == 200
    assert response.json() == {"is_logged_in": False}


def test_is_logged_in(setup_data):
    client.cookies.set("session_id", "session_id1")
    response = client.get("/users/is-logged-in")
    assert response.status_code == 200
    assert response.json() == {"is_logged_in": True}
    client.cookies.clear()


def test_is_logged_in_expired_token(setup_data):
    client.cookies.set("session_id", "session_id2")
    response = client.get("/users/is-logged-in")
    assert response.status_code == 200
    assert response.json() == {"is_logged_in": False}
    client.cookies.clear()


# /users/login


def test_login():
    response = client.get("/users/login")
    assert (
        response.url
        == f"https://id.twitch.tv/oauth2/authorize?client_id={get_settings().twitch_id}&response_type=code&state=12345678&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fusers%2Fcallback&scope=channel%3Amanage%3Apolls+channel%3Amanage%3Apredictions+user%3Aread%3Aemail"
    )
    assert client.cookies.get("state") == "12345678"
    client.cookies.clear()


# /users/callback


def test_callback_error():
    response = client.get("/users/callback?error=error")
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "T02"


def test_callback_missing_state():
    response = client.get("/users/callback")
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "T01"


def test_callback_no_cookies():
    response = client.get("/users/callback?state=12345678")
    assert response.status_code == 403
    data = response.json()
    assert data["error_code"] == "T03"


def test_callback_wrong_state():
    client.cookies.set("state", "12345678")
    response = client.get("/users/callback?state=12345677")
    assert response.status_code == 403
    data = response.json()
    assert data["error_code"] == "T03"
    client.cookies.clear()


def test_callback(setup_data):  # We connect user3 once to test user creation
    client.cookies.set("state", "12345678")
    response = client.get("/users/callback?state=12345678&code=code")
    assert response.url == f"{get_settings().front_base_url}/callback"
    assert client.cookies.get("session_id") == "session_id3"
    client.cookies.clear()


def test_callback_multiple(setup_data):  # We connect user3 twice to test user update
    client.cookies.set("state", "12345678")
    response = client.get("/users/callback?state=12345678&code=code")
    assert response.url == f"{get_settings().front_base_url}/callback"
    assert client.cookies.get("session_id") == "session_id3"

    response = client.get("/users/callback?state=12345678&code=code")
    assert response.url == f"{get_settings().front_base_url}/callback"
    assert client.cookies.get("session_id") == "session_id3"
    client.cookies.clear()


# /users/logout


def test_logout_no_cookies():
    response = client.get("/users/logout")
    assert response.status_code == 401
    data = response.json()
    assert data["error_code"] == "F01"


def test_logout(setup_data):
    client.cookies.set("session_id", "session_id1")
    response = client.get("/users/logout")
    assert response.status_code == 200
    client.cookies.clear()
