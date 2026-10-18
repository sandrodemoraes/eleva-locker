#!/usr/bin/env python3
"""Garante armário Matriz no banco e TOTEM_ARMARIO_ID no .env para o totem."""

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SKIP_BACKUP", "1")

NOME_ARMARIO = "ELEVA Locker Matriz"
ENV_PATH = ROOT / ".env"


def _gravar_env(chave, valor):
    linhas = []
    achou = False
    if ENV_PATH.exists():
        for linha in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if re.match(rf"^\s*{re.escape(chave)}\s*=", linha) and not linha.strip().startswith("#"):
                linhas.append(f"{chave}={valor}")
                achou = True
            else:
                linhas.append(linha)
    if not achou:
        if linhas and linhas[-1].strip():
            linhas.append("")
        linhas.append(f"{chave}={valor}")
    ENV_PATH.write_text("\n".join(linhas).rstrip() + "\n", encoding="utf-8")
    print(f"  OK  {chave}={valor} no .env")


def main():
    from database import criar_banco

    criar_banco()
    from repositories.base_repository import BaseRepository

    with BaseRepository.get_connection() as conn:
        conn.execute("""
            UPDATE armarios SET status = 'ativo'
            WHERE status IS NULL OR TRIM(COALESCE(status, '')) = ''
        """)
        conn.commit()

        row = conn.execute(
            "SELECT id, nome, status FROM armarios ORDER BY id"
        ).fetchall()

        print("\nArmários no banco:")
        if not row:
            print("  (nenhum — cadastre em Armários no painel)")
        for r in row:
            print(f"  id={r['id']}  nome={r['nome']!r}  status={r['status']!r}")

        alvo = conn.execute(
            "SELECT id FROM armarios WHERE LOWER(nome) LIKE '%matriz%' ORDER BY id LIMIT 1"
        ).fetchone()

        if not alvo:
            site = conn.execute(
                "SELECT id FROM sites WHERE LOWER(nome) LIKE '%matriz%' ORDER BY id LIMIT 1"
            ).fetchone()
            site_id = site["id"] if site else 1
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO armarios (nome, endereco, cidade, estado, status, site_id, max_portas)
                VALUES (?, 'Matriz ELEVA', 'Lauro Müller', 'SC', 'ativo', ?, 16)
            """, (NOME_ARMARIO, site_id))
            conn.commit()
            armario_id = cursor.lastrowid
            print(f"\n  Criado armário {NOME_ARMARIO} id={armario_id}")
        else:
            armario_id = alvo["id"]
            conn.execute(
                "UPDATE armarios SET status = 'ativo', max_portas = COALESCE(max_portas, 16) WHERE id = ?",
                (armario_id,),
            )
            conn.commit()
            print(f"\n  Usando armário Matriz id={armario_id}")

    _gravar_env("TOTEM_ARMARIO_ID", str(armario_id))
    print(f"\nReinicie o servidor e abra: /totem/{armario_id}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
