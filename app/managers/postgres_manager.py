from sqlalchemy import (
    Column,
    Integer,
    Text,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.utils.config import get_settings


postgres_url = f"postgresql://{get_settings().postgres_user}:{get_settings().postgres_secret}@{get_settings().postgres_host}/{get_settings().postgres_db}?sslmode=require&channel_binding=require"

engine = create_engine(postgres_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Playlist(Base):
    __tablename__ = "PLAYLISTS"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text)
    description = Column(Text)
    field1 = Column(Text)
    field2 = Column(Text)


class PlaylistItem(Base):
    __tablename__ = "PLAYLIST_ITEMS"
    id = Column(Integer, primary_key=True, autoincrement=True)
    playlist_id = Column(Integer)
    url = Column(Text)
    field1 = Column(Text)
    field2 = Column(Text)


class GameMode(Base):
    __tablename__ = "GAME_MODE"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text)
    answer1 = Column(Text)
    answer2 = Column(Text)


Base.metadata.create_all(bind=engine)


class PostgresManager:
    def __init__(self):
        self.session = SessionLocal

    def get_playlist(self, _id: int) -> Playlist:
        with self.session() as session:
            return session.query(Playlist).filter(Playlist.id == _id).first()

    def get_playlists(self) -> list[Playlist]:
        with self.session() as session:
            return session.query(Playlist)

    def create_playlist(
        self,
        title: str,
        description: str,
        field1: str,
        field2: str,
    ) -> Playlist:
        with self.session() as session:
            new_playlist = Playlist(
                title=title,
                description=description,
                field1=field1,
                field2=field2,
            )
            session.add(new_playlist)

            try:
                session.commit()
                session.refresh(new_playlist)
                return new_playlist
            except Exception as e:
                session.rollback()
                raise e

    def get_playlist_items(self, playlist_id: int) -> list[PlaylistItem]:
        with self.session() as session:
            return session.query(PlaylistItem).filter(
                PlaylistItem.playlist_id == playlist_id
            )

    def create_playlist_item(
        self,
        playlist_id: int,
        url: str,
        field1: str,
        field2: str,
    ) -> PlaylistItem:
        with self.session() as session:
            new_playlist_item = PlaylistItem(
                playlist_id=playlist_id,
                url=url,
                field1=field1,
                field2=field2,
            )
            session.add(new_playlist_item)

            try:
                session.commit()
                session.refresh(new_playlist_item)
                return new_playlist_item
            except Exception as e:
                session.rollback()
                raise f"Error creating user: {e}"

    def get_game_modes(self) -> list[GameMode]:
        with self.session() as session:
            return session.query(GameMode)
