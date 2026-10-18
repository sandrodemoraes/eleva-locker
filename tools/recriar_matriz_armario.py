#!/usr/bin/env python3
"""Recria ELEVA Locker Matriz no banco (16 portas, site Matriz ELEVA) e ajusta TOTEM_ARMARIO_ID."""

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
        site = conn.execute(
            "SELECT id FROM sites WHERE LOWER(nome) LIKE '%matriz%' ORDER BY id LIMIT 1"
        ).fetchone()
        site_id = site["id"] if site else 1

        print("\nArmários atuais:")
        for r in conn.execute("SELECT id, nome, max_portas, site_id, status FROM armarios ORDER BY id"):
            print(f"  id={r['id']}  nome={r['nome']!r}  portas={r['max_portas']}  site={r['site_id']}  status={r['status']!r}")

        matriz = conn.execute(
            """
            SELECT id FROM armarios
            WHERE LOWER(nome) LIKE '%matriz%'
            ORDER BY id LIMIT 1
            """
        ).fetchone()

        if matriz:
            armario_id = matriz["id"]
            conn.execute(
                """
                UPDATE armarios
                SET nome = ?, status = 'ativo', max_portas = 16, site_id = ?
                WHERE id = ?
                """,
                (NOME_ARMARIO, site_id, armario_id),
            )
            conn.commit()
            print(f"\n  Matriz já existia — atualizada id={armario_id}")
        else:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO armarios (nome, endereco, cidade, estado, status, site_id, max_portas)
                VALUES (?, 'Matriz ELEVA', 'Lauro Müller', 'SC', 'ativo', ?, 16)
                """,
                (NOME_ARMARIO, site_id),
            )
            conn.commit()
            armario_id = cursor.lastrowid
            print(f"\n  Criada {NOME_ARMARIO} id={armario_id} (16 portas, site_id={site_id})")
            print("  Abra /armarios e clique na engrenagem para cadastrar ESP .104 e .155.")

    _gravar_env("TOTEM_ARMARIO_ID", str(armario_id))
    print(f"\nReinicie o servidor: py app.py")
    print(f"Totem: /totem/{armario_id}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
