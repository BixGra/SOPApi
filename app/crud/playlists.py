from app.crud.base import BaseCRUD
from app.models.playlists import GameModeBase, PlaylistBase, PlaylistItemBase
from app.schemas.playlists import GameMode, Playlist, PlaylistItem
from app.utils.errors import (
    BaseError,
    GameModeNotFoundError,
    PlaylistItemsNotFoundError,
    PlaylistNotFoundError,
)


class PlaylistsCRUD(BaseCRUD):
    def get_playlist(self, _id: int) -> list[Playlist]:
        if (
            result := self.session.query(PlaylistBase)
            .filter(PlaylistBase.id == _id)
            .one_or_none()
        ):
            return self.wrap_element(
                Playlist,
                result,
            )
        raise PlaylistNotFoundError

    def get_playlists(self) -> list[Playlist]:
        return self.wrap_elements(Playlist, self.session.query(PlaylistBase).all())

    def create_playlist(
        self,
        title: str,
        description: str,
        field1: str,
        field2: str,
    ) -> list[Playlist]:
        new_playlist = PlaylistBase(
            title=title,
            description=description,
            field1=field1,
            field2=field2,
        )
        self.session.add(new_playlist)

        try:
            self.session.commit()
            self.session.refresh(new_playlist)
            return self.wrap_element(Playlist, new_playlist)
        except Exception as e:
            self.session.rollback()
            raise BaseError("create playlist rollback")

    def get_playlist_items(self, playlist_id: int) -> list[PlaylistItem]:
        if (
            results := self.session.query(PlaylistItemBase)
            .filter(PlaylistItemBase.playlist_id == playlist_id)
            .all()
        ):
            return self.wrap_elements(
                PlaylistItem,
                results,
            )
        raise PlaylistItemsNotFoundError

    def create_playlist_item(
        self,
        playlist_id: int,
        url: str,
        field1: str,
        field2: str,
    ) -> list[PlaylistItem]:
        new_playlist_item = PlaylistItemBase(
            playlist_id=playlist_id,
            url=url,
            field1=field1,
            field2=field2,
        )
        self.session.add(new_playlist_item)

        try:
            self.session.commit()
            self.session.refresh(new_playlist_item)
            return self.wrap_elements(PlaylistItem, new_playlist_item)
        except Exception as e:
            self.session.rollback()
            raise BaseError("create playlist item rollback")

    def get_game_mode(self, _id: int) -> list[GameMode]:
        if (
            result := self.session.query(GameModeBase)
            .filter(GameModeBase.id == _id)
            .one_or_none()
        ):
            return self.wrap_element(
                GameMode,
                result,
            )
        raise GameModeNotFoundError

    def get_game_modes(self) -> list[GameMode]:
        return self.wrap_elements(GameMode, self.session.query(GameModeBase).all())
