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
            "error_code": self.error_code,
            "status_code": self.status_code,
            "title": self.title,
        }


class BaseError(SOPApiError):
    def __init__(self, text: str = ""):
        self.error_code = "E00"
        self.status_code = 500
        self.title = text


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
