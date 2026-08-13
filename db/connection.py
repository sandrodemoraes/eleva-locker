"""
Camada de conexão unificada — SQLite (dev) e PostgreSQL (produção).
"""
import os
import sqlite3
from pathlib import Path

import config


class Row(dict):
    """Dict compatível com sqlite3.Row."""

    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)


class CursorWrapper:

    def __init__(self, cursor, engine):
        self._cursor = cursor
        self._engine = engine
        self.lastrowid = None

    def fetchall(self):
        rows = self._cursor.fetchall()
        if self._engine == "postgresql":
            return [Row(r) for r in rows]
        return rows

    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        if self._engine == "postgresql":
            return Row(row)
        return row


class ConnectionWrapper:
    """Wrapper com interface compatível entre SQLite e PostgreSQL."""

    def __init__(self, conn, engine):
        self._conn = conn
        self._engine = engine

    def _adapt_sql(self, sql):
        if self._engine == "postgresql":
            return sql.replace("?", "%s")
        return sql

    def execute(self, sql, params=()):

        sql = self._adapt_sql(sql)

        if self._engine == "postgresql":
            cur = self._conn.cursor(cursor_factory=__import__(
                "psycopg2.extras", fromlist=["RealDictCursor"]
            ).RealDictCursor)
            cur.execute(sql, params)
            wrapper = CursorWrapper(cur, self._engine)
            return wrapper

        return self._conn.execute(sql, params)

    def cursor(self):

        if self._engine == "postgresql":
            return PostgresCursor(self._conn, self._engine)

        return self._conn.cursor()

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        self.close()
        return False


class PostgresCursor:

    def __init__(self, conn, engine):
        self._conn = conn
        self._engine = engine
        from psycopg2.extras import RealDictCursor
        self._cursor = conn.cursor(cursor_factory=RealDictCursor)
        self.lastrowid = None

    def execute(self, sql, params=()):

        sql = sql.replace("?", "%s")

        if sql.strip().upper().startswith("INSERT") and "RETURNING" not in sql.upper():
            sql = sql.rstrip().rstrip(";") + " RETURNING id"

        self._cursor.execute(sql, params)

        if "RETURNING" in sql.upper():
            row = self._cursor.fetchone()
            self.lastrowid = row["id"] if row else None

    def fetchall(self):
        return [Row(r) for r in self._cursor.fetchall()]

    def fetchone(self):
        row = self._cursor.fetchone()
        return Row(row) if row else None

    def executemany(self, sql, seq_of_params):
        for params in seq_of_params:
            self.execute(sql, params)


def get_engine():
    bancada = os.getenv("ELEVA_BANCADA", "").strip().lower() in ("1", "true", "yes")
    if not bancada:
        bancada = getattr(config, "ELEVA_BANCADA", False)
    if bancada:
        return "sqlite"
    if config.DATABASE_URL and config.DATABASE_URL.startswith("postgres"):
        return "postgresql"
    return "sqlite"


def adapt_ddl(sql, engine=None):
    """Adapta DDL SQLite para PostgreSQL."""
    engine = engine or get_engine()
    if engine != "postgresql":
        return sql
    sql = sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
    sql = sql.replace("AUTOINCREMENT", "")
    sql = sql.replace("DATETIME", "TIMESTAMP")
    return sql


def get_connection():

    engine = get_engine()

    if engine == "postgresql":
        import psycopg2
        import psycopg2.extras

        conn = psycopg2.connect(config.DATABASE_URL)
        conn.autocommit = False

        return ConnectionWrapper(conn, engine)

    db_path = Path(__file__).resolve().parent.parent / "database" / "elevalocker.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    return ConnectionWrapper(conn, engine)


def coluna_existe(cursor_or_conn, tabela, coluna, engine=None):

    engine = engine or get_engine()

    if engine == "postgresql":

        cur = cursor_or_conn.cursor() if hasattr(cursor_or_conn, "cursor") else cursor_or_conn

        cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = %s AND column_name = %s
        """, (tabela, coluna))

        return cur.fetchone() is not None

    cur = cursor_or_conn
    cur.execute(f"PRAGMA table_info({tabela})")
    return any(row[1] == coluna for row in cur.fetchall())


def adicionar_coluna(cursor, tabela, coluna, definicao, engine=None):

    engine = engine or get_engine()

    if coluna_existe(cursor, tabela, coluna, engine):
        return

    if engine == "postgresql":
        pg_def = definicao.replace("AUTOINCREMENT", "").strip()
        cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {pg_def}")
    else:
        cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}")
