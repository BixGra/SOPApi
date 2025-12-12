class HasLength:
    _length: int

    def __len__(self):
        return self._length


class FixturePlaylist:
    def __init__(
        self, id_: int, title: str, description: str, field1: str, field2: str
    ):
        self.id: int = id_
        self.title: str = title
        self.description: str = description
        self.field1: str = field1
        self.field2: str = field2


class FixturePlaylists(HasLength):
    def __init__(self, playlists: list[FixturePlaylist]):
        self._length = len(playlists)
        for i, playlist in enumerate(playlists, start=1):
            setattr(self, f"playlist{i}", playlist)


class FixturePlaylistItem:
    def __init__(self, id_: int, playlist_id: int, url: str, field1: str, field2: str):
        self.id: int = id_
        self.playlist_id: str = playlist_id
        self.url: str = url
        self.field1: str = field1
        self.field2: str = field2


class FixturePlaylistItems(HasLength):
    def __init__(self, playlist_items: list[FixturePlaylistItem]):
        self._length = len(playlist_items)
        for i, playlist_item in enumerate(playlist_items, start=1):
            setattr(self, f"playlist_item{i}", playlist_item)


class FixturePlaylistsItems(HasLength):
    def __init__(self, playlists_items: list[FixturePlaylistItems]):
        self._length = len(playlists_items)
        for i, playlist_items in enumerate(playlists_items, start=1):
            setattr(self, f"playlist{i}_items", playlist_items)


class FixtureGameMode:
    def __init__(
        self, id_: int, name: str, description: str, answer1: str, answer2: str
    ):
        self.id: int = id_
        self.name: str = name
        self.description: str = description
        self.answer1: str = answer1
        self.answer2: str = answer2


class FixtureGameModes(HasLength):
    def __init__(self, game_modes: list[FixtureGameMode]):
        self._length = len(game_modes)
        for i, game_mode in enumerate(game_modes, start=1):
            setattr(self, f"game_mode{i}", game_mode)


class FixtureUser:
    def __init__(
        self,
        user_id: str,
        email: str,
        username: str,
        token: str,
        refresh_token: str,
        session_id: str,
    ):
        self.user_id: int = user_id
        self.email: str = email
        self.username: str = username
        self.token: str = token
        self.refresh_token: str = refresh_token
        self.session_id = session_id


class FixtureUsers(HasLength):
    def __init__(self, users: list[FixtureUser]):
        self._length = len(users)
        for i, user in enumerate(users, start=1):
            setattr(self, f"user{i}", user)
