#!/usr/bin/env python3
"""Diagnóstico: usuários vinculados a armários."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env_bancada import aplicar_bancada_processo

aplicar_bancada_processo()
os.environ.setdefault("SKIP_BACKUP", "1")

from database import criar_banco

criar_banco()

from pathlib import Path
from db.connection import coluna_existe, get_connection


def main():
    db_path = Path(__file__).resolve().parent.parent / "database" / "elevalocker.db"
    print("=" * 60)
    print("  DIAGNÓSTICO — USUÁRIOS × ARMÁRIOS")
    print("=" * 60)
    print(f"\nBanco: {db_path}")

    conn = get_connection()
    cur = conn.cursor()
    tem_coluna = coluna_existe(cur, "usuarios", "armario_id")
    print(f"Coluna usuarios.armario_id: {'OK' if tem_coluna else 'FALTANDO'}")

    if not tem_coluna:
        return 1

    armarios = cur.execute("SELECT id, nome, site_id FROM armarios ORDER BY id").fetchall()
    print(f"\nArmários ({len(armarios)}):")
    for a in armarios:
        n = cur.execute(
            "SELECT COUNT(*) FROM usuarios WHERE armario_id = ?",
            (a["id"],),
        ).fetchone()[0]
        print(f"  id={a['id']} | {a['nome']} | site={a['site_id']} | usuários={n}")

    todos = cur.execute("""
        SELECT u.id, u.nome, u.email, u.perfil, u.status, u.armario_id, a.nome AS armario_nome
        FROM usuarios u
        LEFT JOIN armarios a ON a.id = u.armario_id
        ORDER BY u.perfil, u.nome
    """).fetchall()

    print(f"\nTodos os usuários ({len(todos)}):")
    for u in todos:
        arm = u["armario_nome"] or (f"id={u['armario_id']} (ÓRFÃO)" if u["armario_id"] else "—")
        print(f"  id={u['id']} | {u['perfil']} | {u['email']} | armário={arm}")

    orfaos = [u for u in todos if u["armario_id"] and not u["armario_nome"]]
    desvinc = [
        u for u in todos
        if u["perfil"] in ("Usuário", "Operador") and u["status"] and u["armario_id"] is None
    ]

    if orfaos:
        print(f"\n⚠ {len(orfaos)} usuário(s) com armario_id inválido")
    if desvinc:
        print(f"\n? {len(desvinc)} Operador/Usuário ativo(s) sem armário (global ou perdido)")

    print("\nCorreção rápida:")
    print("  tools\\restaurar_usuarios_armario.bat")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
