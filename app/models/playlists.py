from sqlalchemy import Column, Integer, Text

from app.database import Base


class PlaylistBase(Base):
    __tablename__ = "PLAYLISTS"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text)
    description = Column(Text)
    field1 = Column(Text)
    field2 = Column(Text)


class PlaylistItemBase(Base):
    __tablename__ = "PLAYLIST_ITEMS"
    id = Column(Integer, primary_key=True, autoincrement=True)
    playlist_id = Column(Integer)
    url = Column(Text)
    field1 = Column(Text)
    field2 = Column(Text)


class GameModeBase(Base):
    __tablename__ = "GAME_MODES"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text)
    description = Column(Text)
    answer1 = Column(Text)
    answer2 = Column(Text)
