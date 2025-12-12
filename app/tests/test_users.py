from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.users import UserBase
from app.tests.fixtures.fixtures_artifact import (
    TestingSessionLocal,
    fake_session_id,
    fake_state,
    override_get_postgres_manager,
    override_get_session_id,
    override_get_state,
    override_get_twitch_client,
)
from app.tests.fixtures.fixtures_classes import FixtureUser, FixtureUsers
from app.utils.config import get_settings
from app.utils.dependencies import (
    get_postgres_database,
    get_session_id,
    get_state,
    get_twitch_client,
)

app.dependency_overrides[get_postgres_database] = override_get_postgres_manager
app.dependency_overrides[get_state] = override_get_state
app.dependency_overrides[get_session_id] = override_get_session_id
app.dependency_overrides[get_twitch_client] = override_get_twitch_client

client = TestClient(app)


@pytest.fixture
def users() -> list[UserBase]:
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
        token="expired_token2",
        refresh_token="refresh_token2",
        session_id="session_id2",
    )
    return [user1, user2]


@pytest.fixture
def setup_users(users) -> Generator[FixtureUsers]:
    # Clean
    postgres_database = TestingSessionLocal()
    users_to_clean = postgres_database.query(UserBase).all()
    for user in users_to_clean:
        postgres_database.delete(user)

    # Setup
    postgres_database.add_all(users)
    postgres_database.commit()

    fixture_users = [
        FixtureUser(
            user_id=user.user_id,
            email=user.email,
            username=user.username,
            token=user.token,
            refresh_token=user.refresh_token,
            session_id=user.session_id,
        )
        for user in users
    ]
    yield FixtureUsers(users=fixture_users)

    # Teardown
    users_to_clean = postgres_database.query(UserBase).all()
    for user in users_to_clean:
        postgres_database.delete(user)
    postgres_database.commit()
    postgres_database.close()


@pytest.fixture
def setup_cookies():
    client.cookies.clear()
    yield
    client.cookies.clear()


# /users/is-logged-in


def test_is_logged_in_no_cookies_returns_false(setup_users, setup_cookies):
    response = client.get("/users/is-logged-in")
    assert response.status_code == 200
    assert response.json() == {"is_logged_in": False}


def test_is_logged_in_ok(setup_users, setup_cookies):
    client.cookies.set("session_id", setup_users.user1.session_id)
    response = client.get("/users/is-logged-in")
    assert response.status_code == 200
    assert response.json() == {"is_logged_in": True}


def test_is_logged_in_expired_token_returns_false(setup_users, setup_cookies):
    client.cookies.set("session_id", setup_users.user2.session_id)
    response = client.get("/users/is-logged-in")
    assert response.status_code == 200
    assert response.json() == {"is_logged_in": False}


# /users/login


def test_login_ok(setup_cookies):
    response = client.get("/users/login")
    assert (
        response.url
        == f"https://id.twitch.tv/oauth2/authorize?client_id={get_settings().twitch_id}&response_type=code&state={fake_state}&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fusers%2Fcallback&scope=channel%3Amanage%3Apolls+channel%3Amanage%3Apredictions+user%3Aread%3Aemail"
    )
    assert client.cookies.get("state") == fake_state


# /users/callback


def test_callback_error_returns_400():
    response = client.get("/users/callback?error=error")
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "T02"


def test_callback_missing_state_returns_400():
    response = client.get("/users/callback")
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "T01"


def test_callback_no_cookies_returns_403(setup_cookies):
    response = client.get(f"/users/callback?state={fake_state}")
    assert response.status_code == 403
    data = response.json()
    assert data["error_code"] == "T03"


def test_callback_wrong_state_returns_403(setup_cookies):
    client.cookies.set("state", "wrong_state")
    response = client.get(f"/users/callback?state={fake_state}")
    assert response.status_code == 403
    data = response.json()
    assert data["error_code"] == "T03"


def test_callback_ok(
    setup_users, setup_cookies
):  # Connect user3 once to test user creation
    client.cookies.set("state", fake_state)
    response = client.get(f"/users/callback?state={fake_state}&code=code")
    assert response.url == f"{get_settings().front_base_url}/callback"
    assert client.cookies.get("session_id") == fake_session_id


def test_callback_multiple_ok(
    setup_users, setup_cookies
):  # Connect user3 twice to test user update
    client.cookies.set("state", fake_state)
    response = client.get(f"/users/callback?state={fake_state}&code=code")
    assert response.url == f"{get_settings().front_base_url}/callback"
    assert client.cookies.get("session_id") == fake_session_id

    response = client.get(f"/users/callback?state={fake_state}&code=code")
    assert response.url == f"{get_settings().front_base_url}/callback"
    assert client.cookies.get("session_id") == fake_session_id


# /users/logout


def test_logout_no_cookies_returns_401(setup_cookies):
    response = client.get("/users/logout")
    assert response.status_code == 401
    data = response.json()
    assert data["error_code"] == "F01"


def test_logout_ok(setup_users, setup_cookies):
    client.cookies.set("session_id", setup_users.user1.session_id)
    response = client.get("/users/logout")
    assert response.status_code == 200
