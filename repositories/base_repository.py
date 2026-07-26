import sqlite3
from pathlib import Path


class BaseRepository:
    """
    Classe base responsável por fornecer conexão com o banco de dados.
    Todos os repositories utilizarão esta classe.
    """

    DB_PATH = Path(__file__).resolve().parent.parent / "database" / "elevalocker.db"

    @classmethod
    def get_connection(cls):
        """
        Retorna uma conexão SQLite configurada.
        """
        conn = sqlite3.connect(cls.DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn