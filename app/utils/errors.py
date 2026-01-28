class SOPApiError(Exception):
    error_code: int
    status_code: int
    title: str

    def __str__(self) -> str:
        return f"{self.error_code} : {self.title}"

    def __repr__(self) -> str:
        return str(self)

    def json(self) -> dict:
        return {
            "type": "error",
            "error_code": self.error_code,
            "status_code": self.status_code,
            "title": self.title,
        }


# MARK: Base


class BaseError(SOPApiError):
    def __init__(self, text: str = ""):
        self.error_code = "E00"
        self.status_code = 500
        self.title = text


# MARK: Postgres


class PlaylistNotFoundError(SOPApiError):
    def __init__(self):
        self.error_code = "P01"
        self.status_code = 404
        self.title = "Playlist not found"


class PlaylistItemsNotFoundError(SOPApiError):
    def __init__(self):
        self.error_code = "P02"
        self.status_code = 404
        self.title = "Playlist items not found"


class GameModeNotFoundError(SOPApiError):
    def __init__(self):
        self.error_code = "P03"
        self.status_code = 404
        self.title = "Game mode not found"


class UserNotFoundError(SOPApiError):
    def __init__(self):
        self.error_code = "P04"
        self.status_code = 404
        self.title = "User not found"


# MARK: Twitch


class TwitchStatesError(SOPApiError):
    def __init__(self):
        self.error_code = "T01"
        self.status_code = 400
        self.title = "Error with Twitch states"


class TwitchCallbackError(SOPApiError):
    def __init__(self):
        self.error_code = "T02"
        self.status_code = 400
        self.title = "Error in callback"


class PotentialCSRFError(SOPApiError):
    def __init__(self):
        self.error_code = "T03"
        self.status_code = 403
        self.title = "Potential Cross-Site Request Forgery"


class PollNotFoundError(SOPApiError):
    def __init__(self):
        self.error_code = "T04"
        self.status_code = 404
        self.title = "Poll ID not found for this user"


class InvalidTokenError(SOPApiError):
    def __init__(self):
        self.error_code = "T05"
        self.status_code = 401
        self.title = "User's token is invalid"


# MARK: Websocket


class NotLoggedInError(SOPApiError):
    def __init__(self):
        self.error_code = "W01"
        self.status_code = 401
        self.title = "Tried to connect to websocket while not logged in"


class MissingTypeFieldError(SOPApiError):
    def __init__(self):
        self.error_code = "W02"
        self.status_code = 422
        self.title = "Missing type field"


class UnknownTypeFieldError(SOPApiError):
    def __init__(self):
        self.error_code = "W03"
        self.status_code = 404
        self.title = "Unknown type field"


class MissingPayloadError(SOPApiError):
    def __init__(self):
        self.error_code = "W04"
        self.status_code = 422
        self.title = "Missing payload"


class IncorrectPayloadError(SOPApiError):
    def __init__(self):
        self.error_code = "W05"
        self.status_code = 422
        self.title = "Incorrect payload"


class IncorrectWebsocketInputError(SOPApiError):
    def __init__(self):
        self.error_code = "W06"
        self.status_code = 422
        self.title = "Incorrect websocket input format"


class IncorrectWebsocketOutputError(SOPApiError):
    def __init__(self):
        self.error_code = "W07"
        self.status_code = 422
        self.title = "Incorrect websocket output format"


# MARK: Front End


class NoSessionError(SOPApiError):
    def __init__(self):
        self.error_code = "F01"
        self.status_code = 401
        self.title = "No session running"
