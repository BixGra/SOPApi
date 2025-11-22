from app.database import SessionLocal


def get_postgres_database():
    try:
        postgres_database = SessionLocal()
        yield postgres_database
    finally:
        postgres_database.close()
