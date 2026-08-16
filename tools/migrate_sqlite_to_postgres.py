#!/usr/bin/env python3
"""
Migra dados do SQLite local para PostgreSQL.
Uso: DATABASE_URL=postgresql://... python tools/migrate_sqlite_to_postgres.py
"""
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SQLITE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "database", "elevalocker.db",
)

TABELAS = [
    "sites", "usuarios", "empresas", "planos", "contratos", "faturas",
    "armarios", "esp32", "compartimentos", "encomendas", "logs",
    "notificacoes", "api_keys",
]


def migrar():

    dest_url = os.getenv("DATABASE_URL", "")

    if not dest_url.startswith("postgres"):
        print("Defina DATABASE_URL com PostgreSQL.")
        sys.exit(1)

    if not os.path.exists(SQLITE_PATH):
        print(f"SQLite não encontrado: {SQLITE_PATH}")
        sys.exit(1)

    os.environ["DATABASE_URL"] = dest_url

    from database import criar_banco
    from db.connection import get_connection

    criar_banco()

    src = sqlite3.connect(SQLITE_PATH)
    src.row_factory = sqlite3.Row

    with get_connection() as dest:
        cur = dest.cursor()

        for tabela in TABELAS:
            try:
                rows = src.execute(f"SELECT * FROM {tabela}").fetchall()
            except sqlite3.OperationalError:
                continue

            if not rows:
                continue

            cols = rows[0].keys()
            placeholders = ", ".join(["?"] * len(cols))
            col_names = ", ".join(cols)

            for row in rows:
                cur.execute(
                    f"INSERT INTO {tabela} ({col_names}) VALUES ({placeholders}) "
                    f"ON CONFLICT DO NOTHING",
                    tuple(row[c] for c in cols),
                )

            print(f"  {tabela}: {len(rows)} registros")

        dest.commit()

    src.close()
    print("Migração concluída.")


if __name__ == "__main__":
    migrar()
