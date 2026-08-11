#!/usr/bin/env python3
"""
Restaura moradores para autocomplete do totem.

Problema comum após trocar banco (Postgres→SQLite) ou mudar id do armário:
  - usuários sumiram do SQLite
  - armario_id=3 mas totem usa id=2
  - perfil errado (Operador em vez de Usuário)

Faz:
  1. Copia moradores do backup_01 se o banco atual tiver menos
  2. Vincula todos perfil 'Usuário' ao armário Matriz atual
  3. Corrige armario_id antigo (ex.: 3 → 2)

Uso:
  python tools/restaurar_moradores.py
  python tools/restaurar_moradores.py --listar
"""
import argparse
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

from env_bancada import aplicar_bancada_processo

aplicar_bancada_processo()

NOME_ARMARIO = "ELEVA Locker Matriz"
BACKUP_DB = ROOT / "backups" / "backup_01" / "database" / "elevalocker.db"
DB_ATUAL = ROOT / "database" / "elevalocker.db"


def obter_armario_matriz(conn):
    row = conn.execute(
        "SELECT id, nome FROM armarios WHERE nome = ? LIMIT 1",
        (NOME_ARMARIO,),
    ).fetchone()
    if row:
        return row["id"]
    row = conn.execute(
        "SELECT id FROM armarios ORDER BY id LIMIT 1"
    ).fetchone()
    return row["id"] if row else None


def contar_moradores(conn):
    return conn.execute("""
        SELECT COUNT(*) AS n FROM usuarios
        WHERE status = 1 AND perfil = 'Usuário'
    """).fetchone()["n"]


def listar_moradores(conn, armario_id=None):
    filtro = ""
    params = []
    if armario_id:
        filtro = "AND (armario_id IS NULL OR armario_id = ?)"
        params.append(armario_id)
    return conn.execute(f"""
        SELECT id, nome, telefone, perfil, armario_id, status
        FROM usuarios
        WHERE perfil = 'Usuário' {filtro}
        ORDER BY nome
    """, tuple(params)).fetchall()


def copiar_do_backup(conn_atual, armario_id):
    if not BACKUP_DB.exists():
        print(f"    Backup DB não encontrado: {BACKUP_DB}")
        return 0

    conn_bak = sqlite3.connect(str(BACKUP_DB))
    conn_bak.row_factory = sqlite3.Row
    rows = conn_bak.execute("""
        SELECT nome, email, telefone, senha, perfil, status, armario_id
        FROM usuarios
        WHERE perfil = 'Usuário' AND status = 1
    """).fetchall()
    conn_bak.close()

    if not rows:
        print("    Backup sem moradores (perfil Usuário)")
        return 0

    inseridos = 0
    for r in rows:
        existe = conn_atual.execute(
            "SELECT id FROM usuarios WHERE email = ? LIMIT 1",
            (r["email"],),
        ).fetchone()
        if existe:
            continue
        conn_atual.execute("""
            INSERT INTO usuarios (nome, email, telefone, senha, perfil, status, armario_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            r["nome"], r["email"], r["telefone"], r["senha"],
            r["perfil"], r["status"], armario_id,
        ))
        inseridos += 1
    conn_atual.commit()
    return inseridos


def vincular_matriz(conn, armario_id):
    cur = conn.execute("""
        UPDATE usuarios
        SET armario_id = ?
        WHERE perfil = 'Usuário' AND status = 1
          AND (armario_id IS NULL OR armario_id != ?)
    """, (armario_id, armario_id))
    conn.commit()
    return cur.rowcount


def main():
    """Delega para restaurar_usuarios_armario (compatibilidade totem)."""
    import restaurar_usuarios_armario
    return restaurar_usuarios_armario.main()


if __name__ == "__main__":
    raise SystemExit(main())
