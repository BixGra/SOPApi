from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.utils.config import get_settings

postgres_url = f"postgresql://{get_settings().postgres_user}:{get_settings().postgres_secret}@{get_settings().postgres_host}/{get_settings().postgres_db}?sslmode=require&channel_binding=require"

engine = create_engine(postgres_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
