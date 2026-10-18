from db.connection import get_connection


class BaseRepository:
    """
    Classe base — conexão SQLite ou PostgreSQL via DATABASE_URL.
    """

    @classmethod
    def get_connection(cls):
        return get_connection()

    @classmethod
    def get_engine(cls):
        from db.connection import get_engine
        return get_engine()
