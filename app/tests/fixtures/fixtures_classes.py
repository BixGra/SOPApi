from app.schemas.playlists import GameMode, Playlist, PlaylistItem
from app.schemas.users import User


class FixtureBase:
    _length: int

    def __len__(self):
        return self._length


class FixturePlaylists(FixtureBase):
    def __init__(self, playlists: list[Playlist]):
        self._length = len(playlists)
        for i, playlist in enumerate(playlists, start=1):
            setattr(self, f"playlist{i}", playlist)


class FixturePlaylistItems(FixtureBase):
    def __init__(self, playlist_items: list[PlaylistItem]):
        self._length = len(playlist_items)
        for i, playlist_item in enumerate(playlist_items, start=1):
            setattr(self, f"playlist_item{i}", playlist_item)


class FixturePlaylistsItems(FixtureBase):
    def __init__(self, playlists_items: list[FixturePlaylistItems]):
        self._length = len(playlists_items)
        for i, playlist_items in enumerate(playlists_items, start=1):
            setattr(self, f"playlist{i}_items", playlist_items)


class FixtureGameModes(FixtureBase):
    def __init__(self, game_modes: list[GameMode]):
        self._length = len(game_modes)
        for i, game_mode in enumerate(game_modes, start=1):
            setattr(self, f"game_mode{i}", game_mode)


class FixtureUsers(FixtureBase):
    def __init__(self, users: list[User]):  # TODO
        self._length = len(users)
        for i, user in enumerate(users, start=1):
            setattr(self, f"user{i}", user)
