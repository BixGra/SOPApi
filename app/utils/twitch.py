import httpx

from app.utils.config import get_settings
from app.utils.errors import BaseError, InvalidTokenError
from app.utils.tools import data_to_query_parameters

redirect_uri = f"{get_settings().base_url}/users/callback"

authorization_base_url = "https://id.twitch.tv/oauth2/authorize"
token_url = "https://id.twitch.tv/oauth2/token"
validate_url = "https://id.twitch.tv/oauth2/validate"

get_users = "https://api.twitch.tv/helix/users"
get_polls = "https://api.twitch.tv/helix/polls"
create_poll = "https://api.twitch.tv/helix/polls"

scope = " ".join(
    [
        "channel:manage:polls",
        "user:read:email",
    ]
)
response_type = "code"


class TwitchClient:
    def __init__(self):
        self.client = httpx.AsyncClient()

    @staticmethod
    def get_authorization_url(state: str) -> str:
        return (
            authorization_base_url
            + "?"
            + data_to_query_parameters(
                {
                    "client_id": get_settings().twitch_id,
                    "response_type": response_type,
                    "state": state,
                    "redirect_uri": redirect_uri,
                    "scope": scope,
                }
            )
        )

    async def callback(self, code: str) -> tuple[str, str, int]:
        response = await self.client.post(
            token_url,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "client_id": get_settings().twitch_id,
                "client_secret": get_settings().twitch_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
                "code": code,
            },
        )
        status_code = response.status_code
        if status_code != 200:
            raise BaseError("twitch get token")
        data = response.json()
        token = data["access_token"]
        refresh_token = data["refresh_token"]
        expires_in = data["expires_in"]

        return token, refresh_token, expires_in

    async def validate(self, token: str) -> str:
        response = await self.client.get(
            validate_url,
            headers={
                "Authorization": f"Bearer {token}",
            },
        )
        status_code = response.status_code
        if status_code == 401:
            raise InvalidTokenError()
        if status_code != 200:
            raise BaseError("twitch validate")
        data = response.json()
        user_id = data["user_id"]
        return user_id

    async def refresh(self, refresh_token: str) -> tuple[str, str]:
        response = await self.client.post(
            token_url,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "client_id": get_settings().twitch_id,
                "client_secret": get_settings().twitch_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )
        status_code = response.status_code
        if status_code != 200:
            raise BaseError("twitch refresh")
        data = response.json()
        token = data["access_token"]
        refresh_token = data["refresh_token"]

        return token, refresh_token

    async def get_user(self, token: str, user_id: str) -> tuple[str, str]:
        response = await self.client.get(
            get_users,
            headers={
                "Authorization": f"Bearer {token}",
                "Client-Id": get_settings().twitch_id,
            },
            params={"id": user_id},
        )
        status_code = response.status_code
        if status_code != 200:
            raise BaseError("twitch get error")
        data = response.json()["data"]
        user = data[0]
        username = user["display_name"]
        email = user["email"]
        return username, email

    async def get_poll(self, token: str, user_id: str, poll_id: str) -> dict:
        response = await self.client.get(
            create_poll,
            headers={
                "Authorization": f"Bearer {token}",
                "Client-Id": get_settings().twitch_id,
            },
            params={"broadcaster_id": user_id, "id": poll_id},
        )
        status_code = response.status_code
        if status_code != 200:
            raise BaseError("twitch get poll error")
        data = response.json()["data"]
        poll = data[0]
        output = {
            "poll_id": poll["id"],
            "title": poll["title"],
            "choices": [
                {"title": choice["title"], "votes": choice["votes"]}
                for choice in poll["choices"]
            ],
            "status": poll["status"],
        }
        return output

    # TODO custom duration
    async def create_poll(
        self,
        token: str,
        user_id: str,
        title: str,
        choices: list[str],
        duration: int = 60,
    ) -> dict:
        response = await self.client.post(
            create_poll,
            headers={
                "Authorization": f"Bearer {token}",
                "Client-Id": get_settings().twitch_id,
            },
            data={
                "broadcaster_id": user_id,
                "title": title,
                "choices": [{"title": choice} for choice in choices],
                "duration": duration,
            },
        )
        status_code = response.status_code
        if status_code != 200:
            raise BaseError("twitch create poll error")
        data = response.json()["data"]
        poll = data[0]
        output = {"poll_id": poll["id"]}
        return output

    async def end_poll(self, token: str, user_id: str, poll_id: str) -> dict:
        response = await self.client.patch(
            create_poll,
            headers={
                "Authorization": f"Bearer {token}",
                "Client-Id": get_settings().twitch_id,
            },
            data={"broadcaster_id": user_id, "id": poll_id, "status": "TERMINATED"},
        )
        status_code = response.status_code
        if status_code != 200:
            raise BaseError("twitch end poll error")
        data = response.json()["data"]
        poll = data[0]
        output = {
            "poll_id": poll["id"],
            "title": poll["title"],
            "choices": [
                {"title": choice["title"], "votes": choice["votes"]}
                for choice in poll["choices"]
            ],
            "status": poll["status"],
        }
        return output
