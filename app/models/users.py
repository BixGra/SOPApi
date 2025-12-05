from sqlalchemy import Column, Integer, Text, Time

from app.utils.database import Base


class UserBase(Base):
    __tablename__ = "USERS"
    user_id = Column(Text, primary_key=True)
    email = Column(Text)
    username = Column(Text)
    token = Column(Text)
    refresh_token = Column(Text)
    session_id = Column(Text)
    # expires_at = Column(Time)
