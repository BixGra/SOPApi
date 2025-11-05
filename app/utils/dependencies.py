from app.managers.postgres_manager import PostgresManager


def get_postgres_manager():
    postgres_manager = PostgresManager()
    try:
        yield postgres_manager
    finally:
        pass
