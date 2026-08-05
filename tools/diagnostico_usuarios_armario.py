#!/usr/bin/env python3
"""Verifica coluna armario_id e usuários por armário."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SKIP_BACKUP", "1")

from database import criar_banco

criar_banco()

from pathlib import Path
from db.connection import coluna_existe, get_connection
from repositories.usuario_repository import UsuarioRepository


def main():
    db_path = Path(__file__).resolve().parent.parent / "database" / "elevalocker.db"
    print(f"Banco: {db_path}")

    conn = get_connection()
    cur = conn.cursor()
    tem_coluna = coluna_existe(cur, "usuarios", "armario_id")
    print(f"Coluna usuarios.armario_id: {'OK' if tem_coluna else 'FALTANDO — reinicie py app.py'}")

    if not tem_coluna:
        return 1

    todos = UsuarioRepository.listar()
    print(f"\nTotal usuários: {len(todos)}")
    for u in todos:
        print(
            f"  id={u['id']} | {u['email']} | armario_id={u['armario_id']} | {u['perfil']}"
        )

    arm3 = UsuarioRepository.listar(3)
    print(f"\nUsuários armário #3: {len(arm3)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
