import pytest
import respx
from httpx import Response

from app.utils.config import get_settings
from app.utils.twitch import TwitchClient


@pytest.fixture
def twitch_id_mock():
    with respx.mock(
        base_url="https://id.twitch.tv", assert_all_called=False
    ) as respx_mock:
        respx_mock.post("/oauth2/token", name="token").mock(
            return_value=Response(
                200,
                json={
                    "access_token": "token1",
                    "expires_in": 14124,
                    "refresh_token": "refresh_token1",
                    "scope": [
                        "channel:manage:polls",
                        "user:read:email",
                    ],
                    "token_type": "bearer",
                },
            )
        )
        respx_mock.get("/oauth2/validate", name="validate").mock(
            return_value=Response(
                200,
                json={
                    "client_id": get_settings().twitch_id,
                    "login": "user1",
                    "scopes": [
                        "channel:manage:polls",
                        "user:read:email",
                    ],
                    "user_id": "user1",
                    "expires_in": 5520838,
                },
            )
        )
        yield respx_mock


@pytest.fixture
def twitch_api_mock():
    with respx.mock(
        base_url="https://api.twitch.tv", assert_all_called=False
    ) as respx_mock:
        respx_mock.post("/oauth2/token", name="token").mock(
            return_value=Response(
                200,
                json={
                    "access_token": "token1",
                    "expires_in": 14124,
                    "refresh_token": "refresh_token1",
                    "scope": [
                        "channel:manage:polls",
                        "user:read:email",
                    ],
                    "token_type": "bearer",
                },
            )
        )
        respx_mock.post("/oauth2/validate", name="validate").mock(
            return_value=Response(
                200,
                json={
                    "client_id": get_settings().twitch_id,
                    "login": "user1",
                    "scopes": [
                        "channel:manage:polls",
                        "user:read:email",
                    ],
                    "user_id": "user1",
                    "expires_in": 5520838,
                },
            )
        )
        respx_mock.get("/helix/users", name="get_user").mock(
            return_value=Response(
                200,
                json={
                    "data": [
                        {
                            "id": "user1",
                            "login": "user1",
                            "display_name": "user1",
                            "type": "",
                            "broadcaster_type": "partner",
                            "description": "User description.",
                            "profile_image_url": "image.png",
                            "offline_image_url": "image.png",
                            "view_count": 10,
                            "email": "user1@example.com",
                            "created_at": "2016-12-14T20:32:28Z",
                        }
                    ]
                },
            )
        )
        respx_mock.post("/helix/polls", name="create_poll").mock(
            return_value=Response(
                200,
                json={
                    "data": [
                        {
                            "id": "poll1",
                            "broadcaster_id": "user1",
                            "broadcaster_name": "user1",
                            "broadcaster_login": "user1",
                            "title": "title",
                            "choices": [
                                {
                                    "id": "choice1",
                                    "title": "choice1",
                                    "votes": 1,
                                    "channel_points_votes": 0,
                                    "bits_votes": 0,
                                },
                                {
                                    "id": "choice2",
                                    "title": "choice2",
                                    "votes": 2,
                                    "channel_points_votes": 0,
                                    "bits_votes": 0,
                                },
                            ],
                            "bits_voting_enabled": False,
                            "bits_per_vote": 0,
                            "channel_points_voting_enabled": False,
                            "channel_points_per_vote": 0,
                            "status": "ACTIVE",
                            "duration": 60,
                            "started_at": "2021-03-19T06:08:33.871278372Z",
                        }
                    ]
                },
            )
        )
        respx_mock.get("/helix/polls", name="get_poll").mock(
            return_value=Response(
                200,
                json={
                    "data": [
                        {
                            "id": "poll1",
                            "broadcaster_id": "user1",
                            "broadcaster_name": "user1",
                            "broadcaster_login": "user1",
                            "title": "title",
                            "choices": [
                                {
                                    "id": "choice1",
                                    "title": "choice1",
                                    "votes": 1,
                                    "channel_points_votes": 0,
                                    "bits_votes": 0,
                                },
                                {
                                    "id": "choice2",
                                    "title": "choice2",
                                    "votes": 2,
                                    "channel_points_votes": 0,
                                    "bits_votes": 0,
                                },
                            ],
                            "bits_voting_enabled": False,
                            "bits_per_vote": 0,
                            "channel_points_voting_enabled": False,
                            "channel_points_per_vote": 0,
                            "status": "ACTIVE",
                            "duration": 60,
                            "started_at": "2021-03-19T06:08:33.871278372Z",
                        }
                    ],
                    "pagination": {},
                },
            )
        )
        respx_mock.patch("/helix/polls", name="end_poll").mock(
            return_value=Response(
                200,
                json={
                    "data": [
                        {
                            "id": "poll1",
                            "broadcaster_id": "user1",
                            "broadcaster_name": "user1",
                            "broadcaster_login": "user1",
                            "title": "title",
                            "choices": [
                                {
                                    "id": "choice1",
                                    "title": "choice1",
                                    "votes": 1,
                                    "channel_points_votes": 0,
                                    "bits_votes": 0,
                                },
                                {
                                    "id": "choice2",
                                    "title": "choice2",
                                    "votes": 2,
                                    "channel_points_votes": 0,
                                    "bits_votes": 0,
                                },
                            ],
                            "bits_voting_enabled": False,
                            "bits_per_vote": 0,
                            "channel_points_voting_enabled": False,
                            "channel_points_per_vote": 0,
                            "status": "TERMINATED",
                            "duration": 60,
                            "started_at": "2021-03-19T06:08:33.871278372Z",
                            "ended_at": "2021-03-19T06:11:26.746889614Z",
                        }
                    ]
                },
            )
        )
        yield respx_mock


@pytest.fixture
def twitch_client():
    return TwitchClient()


############
# requests #
############


@pytest.mark.asyncio
async def test_callback_request_ok(twitch_id_mock, twitch_client):
    await twitch_client.callback("code")

    assert twitch_id_mock["token"].called
    route = twitch_id_mock["token"]
    url = str(route.calls.last.request.url)
    assert "https://id.twitch.tv/oauth2/token" in url
    data = str(route.calls.last.request.content)
    assert f"client_id={get_settings().twitch_id}" in data
    assert f"client_secret={get_settings().twitch_secret}" in data
    assert "http%3A%2F%2Flocalhost%3A8000%2Fusers%2Fcallback" in data
    assert f"grant_type=authorization_code" in data
    assert f"code=code" in data

    assert twitch_id_mock["validate"].called
    route = twitch_id_mock["validate"]
    url = str(route.calls.last.request.url)
    assert "https://id.twitch.tv/oauth2/validate" in url


@pytest.mark.asyncio
async def test_is_valid_token_request_ok(twitch_api_mock, twitch_client):
    await twitch_client.get_user(token="token1", user_id="user1")
    assert twitch_api_mock["get_user"].called
    route = twitch_api_mock["get_user"]
    url = str(route.calls.last.request.url)
    assert "https://api.twitch.tv/helix/users" in url
    assert "id=user1" in url


@pytest.mark.asyncio
async def test_get_user_request_ok(twitch_api_mock, twitch_client):
    await twitch_client.get_user(token="token1", user_id="user1")
    assert twitch_api_mock["get_user"].called
    route = twitch_api_mock["get_user"]
    url = str(route.calls.last.request.url)
    assert "https://api.twitch.tv/helix/users" in url


@pytest.mark.asyncio
async def test_create_poll_request_ok(twitch_api_mock, twitch_client):
    await twitch_client.create_poll(
        token="token1",
        user_id="user1",
        title="poll",
        choices=["choice1", "choice2"],
    )
    assert twitch_api_mock["create_poll"].called
    route = twitch_api_mock["create_poll"]
    url = str(route.calls.last.request.url)
    assert "https://api.twitch.tv/helix/polls" in url
    data = str(route.calls.last.request.content)
    assert "broadcaster_id=user1" in data
    assert "title=poll" in data
    assert (
        "choices=%7B%27title%27%3A+%27choice1%27%7D&choices=%7B%27title%27%3A+%27choice2%27%7D"
        in data
    )
    assert "duration=60" in data


@pytest.mark.asyncio
async def test_get_poll_request_ok(twitch_api_mock, twitch_client):
    await twitch_client.get_poll(
        token="token1",
        user_id="user1",
        poll_id="poll1",
    )
    assert twitch_api_mock["get_poll"].called
    route = twitch_api_mock["get_poll"]
    url = str(route.calls.last.request.url)
    assert "https://api.twitch.tv/helix/polls" in url
    assert "broadcaster_id=user1" in url
    assert "id=poll1" in url


@pytest.mark.asyncio
async def test_end_poll_request_ok(twitch_api_mock, twitch_client):
    await twitch_client.end_poll(token="token1", user_id="user1", poll_id="poll1")
    assert twitch_api_mock["end_poll"].called
    route = twitch_api_mock["end_poll"]
    url = str(route.calls.last.request.url)
    assert "https://api.twitch.tv/helix/polls" in url
    data = str(route.calls.last.request.content)
    assert "broadcaster_id=user1" in data
    assert "id=poll1" in data
    assert "status=TERMINATED" in data


###########
# outuput #
###########


@pytest.mark.asyncio
async def test_get_authorization_url_ok(twitch_client):
    fake_state = "fake_state"
    url = twitch_client.get_authorization_url(fake_state)
    assert (
        url
        == f"https://id.twitch.tv/oauth2/authorize?client_id={get_settings().twitch_id}&response_type=code&state={fake_state}&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fusers%2Fcallback&scope=channel%3Amanage%3Apolls+user%3Aread%3Aemail"
    )


@pytest.mark.asyncio
async def test_callback_request_ok(twitch_id_mock, twitch_client):
    user_id, token, refresh_token = await twitch_client.callback("fake_code")
    assert user_id == "user1"
    assert token == "token1"
    assert refresh_token == "refresh_token1"


@pytest.mark.asyncio
async def test_is_valid_token_request_ok(twitch_api_mock, twitch_client):
    is_valid = await twitch_client.is_token_valid(token="token1", user_id="user1")
    assert is_valid == True


@pytest.mark.asyncio
async def test_get_user_output_ok(twitch_api_mock, twitch_client):
    user, email = await twitch_client.get_user(token="token1", user_id="user1")
    assert user == "user1"
    assert email == "user1@example.com"


@pytest.mark.asyncio
async def test_create_poll_output_ok(twitch_api_mock, twitch_client):
    output = await twitch_client.create_poll(
        token="token1",
        user_id="user1",
        title="poll",
        choices=["choice1", "choice2"],
    )
    assert output == {"poll_id": "poll1"}


@pytest.mark.asyncio
async def test_get_poll_output_ok(twitch_api_mock, twitch_client):
    output = await twitch_client.get_poll(
        token="token1",
        user_id="user1",
        poll_id="poll1",
    )
    assert output == {
        "poll_id": "poll1",
        "title": "title",
        "choices": [{"title": "choice1", "votes": 1}, {"title": "choice2", "votes": 2}],
        "status": "ACTIVE",
    }


@pytest.mark.asyncio
async def test_end_poll_output_ok(twitch_api_mock, twitch_client):
    output = await twitch_client.end_poll(
        token="token1",
        user_id="user1",
        poll_id="poll1",
    )
    assert output == {
        "poll_id": "poll1",
        "title": "title",
        "choices": [{"title": "choice1", "votes": 1}, {"title": "choice2", "votes": 2}],
        "status": "TERMINATED",
    }
