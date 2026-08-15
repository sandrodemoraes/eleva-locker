#!/usr/bin/env python3
"""
Corrige status dos compartimentos conforme encomendas pendentes.

Uso: py tools/fix_status_compartimentos.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SKIP_BACKUP", "1")

from database import criar_banco

criar_banco()

from repositories.base_repository import BaseRepository


def main():
    with BaseRepository.get_connection() as conn:
        rows = conn.execute("""
            SELECT c.id, c.numero, c.status, a.nome AS armario
            FROM compartimentos c
            JOIN armarios a ON a.id = c.armario
            ORDER BY a.nome, c.numero
        """).fetchall()

        corrigidos = 0
        for c in rows:
            pendente = conn.execute("""
                SELECT id FROM encomendas
                WHERE compartimento = ? AND status = 'aguardando_retirada'
                LIMIT 1
            """, (c["id"],)).fetchone()

            esperado = "ocupado" if pendente else "livre"
            if c["status"] != esperado:
                conn.execute(
                    "UPDATE compartimentos SET status = ? WHERE id = ?",
                    (esperado, c["id"]),
                )
                print(
                    f"  #{c['numero']} {c['armario']}: "
                    f"{c['status']} → {esperado}"
                )
                corrigidos += 1

        conn.commit()

    print(f"\n{corrigidos} compartimento(s) corrigido(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
