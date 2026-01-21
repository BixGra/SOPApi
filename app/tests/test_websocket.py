from typing import Generator

import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
from starlette.testclient import WebSocketDenialResponse

from app.main import app
from app.models.users import UserBase
from app.schemas.users import User
from app.tests.fixtures.fixtures_artifact import (
    TestingSessionLocal,
    override_get_postgres_manager,
    override_get_twitch_client,
)
from app.tests.fixtures.fixtures_classes import FixtureUsers
from app.utils.dependencies import get_postgres_database, get_twitch_client
from app.utils.errors import (
    IncorrectPayloadError,
    MissingPayloadError,
    MissingTypeFieldError,
    PollNotFoundError,
    UnknownTypeFieldError,
)

app.dependency_overrides[get_postgres_database] = override_get_postgres_manager
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
    return [user1]


@pytest.fixture
def setup_users(users) -> Generator[FixtureUsers]:
    # Clean
    postgres_database = TestingSessionLocal()
    users_to_clean = postgres_database.query(UserBase).all()
    for user in users_to_clean:
        postgres_database.delete(user)
    postgres_database.commit()

    # Setup
    postgres_database.add_all(users)
    postgres_database.commit()

    fixture_users = [
        User(
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


# /websocket/connect

##############
# connection #
##############


def test_websocket_connection_no_cookies_returns_WebSocketDenialResponse(setup_cookies):
    with pytest.raises(WebSocketDenialResponse) as error:
        with client.websocket_connect("/websocket/connect") as websocket:
            pass


def test_websocket_connection_ok(setup_users, setup_cookies):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        assert data == {"payload": {"type": "connection_status", "status": "connected"}}


def test_websocket_disconnection_ok(setup_users, setup_cookies):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json({"payload": {"type": "disconnect"}})
        data = websocket.receive_json()
        assert data == {
            "payload": {"type": "connection_status", "status": "disconnected"}
        }


##################
# json formating #
##################


def test_websocket_json_missing_payload_returns_MissingPayloadError(
    setup_users, setup_cookies
):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json({"not_a_payload": "anything"})
        data = websocket.receive_json()
        assert "payload" in data
        payload = data["payload"]
        assert payload == MissingPayloadError().json()


def test_websocket_json_missing_type_returns_MissingTypeFieldError(
    setup_users, setup_cookies
):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json({"payload": {"not_a_type": "lorem ipsum"}})
        data = websocket.receive_json()
        assert "payload" in data
        payload = data["payload"]
        assert payload == MissingTypeFieldError().json()


def test_websocket_json_missing_type_returns_UnknownTypeFieldError(
    setup_users, setup_cookies
):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json({"payload": {"type": "unknown_type"}})
        data = websocket.receive_json()
        assert "payload" in data
        payload = data["payload"]
        assert payload == UnknownTypeFieldError().json()


#########
# polls #
#########


# general tests


def test_websocket_poll_missing_type_returns_IncorrectPayloadError(
    setup_users, setup_cookies
):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json(
            {
                "payload": {
                    "type": "poll",
                    "data": {
                        "not_a_type": "anything",
                    },
                }
            }
        )
        data = websocket.receive_json()
        assert "payload" in data
        payload = data["payload"]
        assert payload == IncorrectPayloadError().json()


def test_websocket_poll_wrong_type_returns_IncorrectPayloadError(
    setup_users, setup_cookies
):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json(
            {
                "payload": {
                    "type": "poll",
                    "data": {
                        "type": "wrong_type",
                    },
                }
            }
        )
        data = websocket.receive_json()
        assert "payload" in data
        payload = data["payload"]
        assert payload == IncorrectPayloadError().json()


# create poll


def test_websocket_create_poll_wrong_data_returns_IncorrectPayloadError(
    setup_users, setup_cookies
):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json(
            {
                "payload": {
                    "type": "poll",
                    "data": {
                        "type": "start",
                        "data": "wrong_data",
                    },
                }
            }
        )
        data = websocket.receive_json()
        assert "payload" in data
        payload = data["payload"]
        assert payload == IncorrectPayloadError().json()


def test_websocket_create_poll_missing_title_returns_IncorrectPayloadError(
    setup_users, setup_cookies
):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json(
            {
                "payload": {
                    "type": "poll",
                    "data": {
                        "type": "start",
                        "data": {
                            "choices": ["choice1", "choice2"],
                        },
                    },
                }
            }
        )
        data = websocket.receive_json()
        assert "payload" in data
        payload = data["payload"]
        assert payload == IncorrectPayloadError().json()


def test_websocket_create_poll_missing_choices_returns_IncorrectPayloadError(
    setup_users, setup_cookies
):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json(
            {
                "payload": {
                    "type": "poll",
                    "data": {
                        "type": "start",
                        "data": {
                            "title": "poll 1",
                        },
                    },
                }
            }
        )
        data = websocket.receive_json()
        assert "payload" in data
        payload = data["payload"]
        assert payload == IncorrectPayloadError().json()


def test_websocket_create_poll_title_too_long_returns_IncorrectPayloadError(
    setup_users, setup_cookies
):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json(
            {
                "payload": {
                    "type": "poll",
                    "data": {
                        "type": "start",
                        "data": {
                            "title": "poll title that is way too long for the specifications of twitch api",
                            "choices": [
                                "choice1",
                                "choice2",
                            ],
                        },
                    },
                }
            }
        )
        data = websocket.receive_json()
        assert "payload" in data
        payload = data["payload"]
        assert payload == IncorrectPayloadError().json()


def test_websocket_create_poll_choice_too_long_returns_IncorrectPayloadError(
    setup_users, setup_cookies
):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json(
            {
                "payload": {
                    "type": "poll",
                    "data": {
                        "type": "start",
                        "data": {
                            "title": "poll 1",
                            "choices": [
                                "choice1",
                                "choice2",
                                "choice_way_too_long_that_doesn_t_pass_the_test",
                            ],
                        },
                    },
                }
            }
        )
        data = websocket.receive_json()
        assert "payload" in data
        payload = data["payload"]
        assert payload == IncorrectPayloadError().json()


def test_websocket_create_poll_too_many_choices_returns_IncorrectPayloadError(
    setup_users, setup_cookies
):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json(
            {
                "payload": {
                    "type": "poll",
                    "data": {
                        "type": "start",
                        "data": {
                            "title": "poll 1",
                            "choices": [
                                "choice1",
                                "choice2",
                                "choice3",
                                "choice4",
                                "choice5",
                                "choice6",
                            ],
                        },
                    },
                }
            }
        )
        data = websocket.receive_json()
        assert "payload" in data
        payload = data["payload"]
        assert payload == IncorrectPayloadError().json()


def test_websocket_create_poll_not_enough_choices_returns_IncorrectPayloadError(
    setup_users, setup_cookies
):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json(
            {
                "payload": {
                    "type": "poll",
                    "data": {
                        "type": "start",
                        "data": {
                            "title": "poll 1",
                            "choices": ["choice1"],
                        },
                    },
                }
            }
        )
        data = websocket.receive_json()
        assert "payload" in data
        payload = data["payload"]
        assert payload == IncorrectPayloadError().json()


def test_websocket_create_poll_ok(setup_users, setup_cookies):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json(
            {
                "payload": {
                    "type": "poll",
                    "data": {
                        "type": "start",
                        "data": {
                            "title": "poll 1",
                            "choices": ["choice1", "choice2"],
                        },
                    },
                }
            }
        )
        data = websocket.receive_json()
        assert data == {
            "payload": {
                "type": "poll",
                "data": {
                    "type": "start",
                    "data": {
                        "poll_id": "poll1",
                    },
                },
            }
        }


# get poll


def test_websocket_get_poll_wrong_data_returns_IncorrectPayloadError(
    setup_users, setup_cookies
):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json(
            {
                "payload": {
                    "type": "poll",
                    "data": {
                        "type": "get",
                        "data": "wrong_data",
                    },
                }
            }
        )
        data = websocket.receive_json()
        assert "payload" in data
        payload = data["payload"]
        assert payload == IncorrectPayloadError().json()


def test_websocket_get_poll_missing_id_returns_IncorrectPayloadError(
    setup_users, setup_cookies
):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json(
            {
                "payload": {
                    "type": "poll",
                    "data": {
                        "type": "get",
                        "data": {
                            "not_an_id": "anything",
                        },
                    },
                }
            }
        )
        data = websocket.receive_json()
        assert "payload" in data
        payload = data["payload"]
        assert payload == IncorrectPayloadError().json()


def test_websocket_get_poll_not_found_returns_PollNotFoundError(
    setup_users, setup_cookies
):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json(
            {
                "payload": {
                    "type": "poll",
                    "data": {
                        "type": "get",
                        "data": {
                            "poll_id": "id_that_doesn_t_exists",
                        },
                    },
                }
            }
        )
        data = websocket.receive_json()
        assert "payload" in data
        payload = data["payload"]
        assert payload == PollNotFoundError().json()


def test_websocket_get_poll_ok(setup_users, setup_cookies):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json(
            {
                "payload": {
                    "type": "poll",
                    "data": {
                        "type": "get",
                        "data": {
                            "poll_id": "poll1",
                        },
                    },
                }
            }
        )
        data = websocket.receive_json()
        assert data == {
            "payload": {
                "type": "poll",
                "data": {
                    "type": "get",
                    "data": {
                        "poll_id": "poll1",
                        "title": "title1",
                        "choices": [
                            {"title": "choice1", "votes": 1},
                            {"title": "choice2", "votes": 2},
                        ],
                        "status": "ACTIVE",
                    },
                },
            }
        }


# end poll


def test_websocket_end_poll_wrong_data_returns_IncorrectPayloadError(
    setup_users, setup_cookies
):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json(
            {
                "payload": {
                    "type": "poll",
                    "data": {
                        "type": "end",
                        "data": "wrong_data",
                    },
                }
            }
        )
        data = websocket.receive_json()
        assert "payload" in data
        payload = data["payload"]
        assert payload == IncorrectPayloadError().json()


def test_websocket_end_poll_missing_id_returns_IncorrectPayloadError(
    setup_users, setup_cookies
):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json(
            {
                "payload": {
                    "type": "poll",
                    "data": {
                        "type": "end",
                        "data": {
                            "not_an_id": "anything",
                        },
                    },
                }
            }
        )
        data = websocket.receive_json()
        assert "payload" in data
        payload = data["payload"]
        assert payload == IncorrectPayloadError().json()


def test_websocket_end_poll_not_found_returns_PollNotFoundError(
    setup_users, setup_cookies
):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json(
            {
                "payload": {
                    "type": "poll",
                    "data": {
                        "type": "end",
                        "data": {
                            "poll_id": "id_that_doesn_t_exists",
                        },
                    },
                }
            }
        )
        data = websocket.receive_json()
        assert "payload" in data
        payload = data["payload"]
        assert payload == PollNotFoundError().json()


def test_websocket_end_poll_ok(setup_users, setup_cookies):
    client.cookies.set("session_id", setup_users.user1.session_id)
    with client.websocket_connect("/websocket/connect") as websocket:
        data = websocket.receive_json()
        websocket.send_json(
            {
                "payload": {
                    "type": "poll",
                    "data": {
                        "type": "end",
                        "data": {
                            "poll_id": "poll1",
                        },
                    },
                }
            }
        )
        data = websocket.receive_json()
        assert data == {
            "payload": {
                "type": "poll",
                "data": {
                    "type": "end",
                    "data": {
                        "poll_id": "poll1",
                        "title": "title1",
                        "choices": [
                            {"title": "choice1", "votes": 1},
                            {"title": "choice2", "votes": 2},
                        ],
                        "status": "TERMINATED",
                    },
                },
            }
        }
